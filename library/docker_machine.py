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
    if 'virtualbox' == params['driver']:
        if params['virtualbox_cpu_count']:
            cmd.extend(['--virtualbox-cpu-count', params['virtualbox_cpu_count']])
        if params['virtualbox_boot2docker_url']:
            cmd.extend(['--virtualbox-boot2docker-url', params['virtualbox_boot2docker_url']])
        if params['virtualbox_disk_size']:
            cmd.extend(['--virtualbox-disk-size', params['virtualbox_disk_size']])
        if params['virtualbox_host_dns_resolver']:
            cmd.extend(['--virtualbox-host-dns-resolver', params['virtualbox_host_dns_resolver']])
        if params['virtualbox_hostonly_cidr']:
            cmd.extend(['--virtualbox-hostonly-cidr', params['virtualbox_hostonly_cidr']])
        if params['virtualbox_hostonly_nicpromisc']:
            cmd.extend(['--virtualbox-hostonly-nicpromisc', params['virtualbox_hostonly_nicpromisc']])
        if params['virtualbox_hostonly_nictype']:
            cmd.extend(['--virtualbox-hostonly-nictype', params['virtualbox_hostonly_nictype']])
        if params['virtualbox_hostonly_no_dhcp']:
            cmd.extend(['--virtualbox-hostonly-no-dhcp', params['virtualbox_hostonly_no_dhcp']])
        if params['virtualbox_import_boot2docker_vm']:
            cmd.extend(['--virtualbox-import-boot2docker-vm', params['virtualbox_import_boot2docker_vm']])
        if params['virtualbox_memory']:
            cmd.extend(['--virtualbox-memory', params['virtualbox_memory']])
        if params['virtualbox_nat_nictype']:
            cmd.extend(['--virtualbox-nat-nictype', params['virtualbox_nat_nictype']])
        if params['virtualbox_no_dns_proxy']:
            cmd.extend(['--virtualbox-no-dns-proxy', params['virtualbox_no_dns_proxy']])
        if params['virtualbox_no_share']:
            cmd.extend(['--virtualbox-no-share', params['virtualbox_no_share']])
        if params['virtualbox_no_vtx_check']:
            cmd.extend(['--virtualbox-no-vtx-check', params['virtualbox_no_vtx_check']])
        if params['virtualbox_share_folder']:
            cmd.extend(['--virtualbox-share-folder', params['virtualbox_share_folder']])
        if params['virtualbox_ui_type']:
            cmd.extend(['--virtualbox-ui-type', params['virtualbox_ui_type']])
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

            virtualbox_cpu_count=dict(),
            virtualbox_boot2docker_url=dict(),
            virtualbox_disk_size=dict(),
            virtualbox_host_dns_resolver=dict(),
            virtualbox_hostonly_cidr=dict(),
            virtualbox_hostonly_nicpromisc=dict(),
            virtualbox_hostonly_nictype=dict(),
            virtualbox_hostonly_no_dhcp=dict(),
            virtualbox_import_boot2docker_vm=dict(),
            virtualbox_nat_nictype=dict(),
            virtualbox_no_dns_proxy=dict(),
            virtualbox_no_share=dict(),
            virtualbox_no_vtx_check=dict(),
            virtualbox_share_folder=dict(),
            virtualbox_ui_type=dict(),
            virtualbox_memory=dict(),
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

        if 'virtualbox' == module.params['driver']:

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
