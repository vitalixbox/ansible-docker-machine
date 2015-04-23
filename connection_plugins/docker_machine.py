import os
import select
import fcntl
import subprocess
from subprocess import Popen, PIPE

from ansible.callbacks import vvv
from ansible import errors
from ansible import utils
from ansible.runner.connection_plugins.local import (
    Connection as LocalConnection
)


class Connection(LocalConnection):

    def __init__(self, *args, **kwargs):
        LocalConnection.__init__(self, *args, **kwargs)
        self.machine_name = kwargs['private_key_file'].split('/')[-2]
        self.envs = os.environ.copy()

        p = Popen(
            ['docker-machine', 'env', self.machine_name],
            stdin=PIPE, stdout=PIPE, stderr=PIPE
        )
        out, err = p.communicate()
        rc = p.returncode
        if rc != 0:
            raise errors.AnsibleError('Error with executing docker-machine env')
        for env in out.splitlines():
            env = env.replace('export ', '').split('=')
            self.envs[env[0]] = env[1]

    def exec_command(self, cmd, tmp_path, become_user=None, sudoable=False, executable='/bin/sh', in_data=None):
        ''' run a command on the local host '''

        # su requires to be run from a terminal, and therefore isn't supported here (yet?)
        if sudoable and self.runner.become and self.runner.become_method not in self.become_methods_supported:
            raise errors.AnsibleError("Internal Error: this module does not support running commands via %s" % self.runner.become_method)

        if in_data:
            raise errors.AnsibleError("Internal Error: this module does not support optimized module pipelining")

        if self.runner.become and sudoable:
            local_cmd, prompt, success_key = utils.make_become_cmd(cmd, become_user, executable, self.runner.become_method, '-H', self.runner.become_exe)
        else:
            if executable:
                local_cmd = executable.split() + ['-c', cmd]
            else:
                local_cmd = cmd
        executable = executable.split()[0] if executable else None

        vvv("EXEC %s" % (local_cmd), host=self.host)
        p = subprocess.Popen(local_cmd, shell=isinstance(local_cmd, basestring),
                             cwd=self.runner.basedir, executable=executable,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=self.envs)

        if self.runner.become and sudoable and self.runner.become_pass:
            fcntl.fcntl(p.stdout, fcntl.F_SETFL,
                        fcntl.fcntl(p.stdout, fcntl.F_GETFL) | os.O_NONBLOCK)
            fcntl.fcntl(p.stderr, fcntl.F_SETFL,
                        fcntl.fcntl(p.stderr, fcntl.F_GETFL) | os.O_NONBLOCK)
            become_output = ''
            while success_key not in become_output:

                if prompt and become_output.endswith(prompt):
                    break
                if utils.su_prompts.check_su_prompt(become_output):
                    break

                rfd, wfd, efd = select.select([p.stdout, p.stderr], [],
                                              [p.stdout, p.stderr], self.runner.timeout)
                if p.stdout in rfd:
                    chunk = p.stdout.read()
                elif p.stderr in rfd:
                    chunk = p.stderr.read()
                else:
                    stdout, stderr = p.communicate()
                    raise errors.AnsibleError('timeout waiting for %s password prompt:\n' % self.runner.become_method + become_output)
                if not chunk:
                    stdout, stderr = p.communicate()
                    raise errors.AnsibleError('%s output closed while waiting for password prompt:\n' % self.runner.become_method + become_output)
                become_output += chunk
            if success_key not in become_output:
                p.stdin.write(self.runner.become_pass + '\n')
            fcntl.fcntl(p.stdout, fcntl.F_SETFL, fcntl.fcntl(p.stdout, fcntl.F_GETFL) & ~os.O_NONBLOCK)
            fcntl.fcntl(p.stderr, fcntl.F_SETFL, fcntl.fcntl(p.stderr, fcntl.F_GETFL) & ~os.O_NONBLOCK)

        stdout, stderr = p.communicate()
        return (p.returncode, '', stdout, stderr)
