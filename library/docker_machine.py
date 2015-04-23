#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE


DRIVERS = [
    'amazonec2', 'azure', 'digitalocean', 'google', 'openstack', 'rackspace',
    'softlayer', 'virtualbox', 'vmwarevcloudair', 'vmwarevsphere'
]


def command(module, cmd):
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode
    if rc != 0:
        module.fail_json(
            msg='Error executing command.',
            cmd=' '.join(cmd), out=out, err=err, rc=rc
        )
    return out


def docker_machine_exists(module):
    out = command(
        module, ['docker-machine', 'ls', '-q', module.params['name']]
    )
    return module.params['name'] in out


def docker_machine_create(module):
    params = module.params
    cmd = ['docker-machine', 'create', '--driver', params['driver']]
    if 'digitalocean' == params['driver']:
        cmd.extend([
            '--digitalocean-access-token', params['digitalocean_access_token']
        ])
        if params['digitalocean_image']:
            cmd.extend([
                '--digitalocean-image', params['digitalocean_image']
            ])
        if params['digitalocean_region']:
            cmd.extend([
                '--digitalocean-region', params['digitalocean_region']
            ])
        if params['digitalocean_size']:
            cmd.extend([
                '--digitalocean-size', params['digitalocean_size']
            ])
    cmd.append(params['name'])
    command(module, cmd)


def docker_machine_rm(module):
    docker_machine_exists(module)
    command(
        module, ['docker-machine', 'rm', '-f', module.params['name']]
    )


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            state=dict(choices=['present', 'absent'], required=True),
            driver=dict(choices=DRIVERS),

            digitalocean_access_token=dict(),
            digitalocean_image=dict(),
            digitalocean_region=dict(),
            digitalocean_size=dict(),
        ),
    )
    state = module.params['state']
    changed = True

    if 'present' == state:
        if not module.params['driver']:
            module.fail_json(msg='Driver required')

        if 'digitalocean' == module.params['driver']:
            if not module.params['digitalocean_access_token']:
                module.fail_json(msg='DigitalOcean access token required.')

            if not docker_machine_exists(module):
                docker_machine_create(module)
            else:
                changed = False

        else:
            module.fail_json(
                msg='Driver [%s] not supported by this module. \
You may contribute it :).' % module.params['driver']
            )

    elif 'absent' == state:
        if docker_machine_exists(module):
            docker_machine_rm(module)
        else:
            changed = False

    module.exit_json(changed=changed)


from ansible.module_utils.basic import *
main()
