#!/usr/bin/env python2
import json
import subprocess
import sys


BASE_PARAMS = {
    'ansible_python_interpreter': '/usr/bin/python2.7',
}


out = subprocess.check_output(['docker-machine', 'ls'])
dockers = {}
machines = out.splitlines()[1:]
for machine_info in machines:
    try:
        machine_info = machine_info.replace('*', '').split()
        machine_name = machine_info[0]
        machine_driver = machine_info[2]
        if not machine_info[3].startswith('tcp://'):
            continue
        machine_ip = machine_info[3].replace('tcp://', '').split(':')[:1][0]
    except:
        continue

    dockers[machine_name] = {
        'ansible_ssh_private_key_file': '~/.docker/machine/machines/%s/id_rsa' % machine_name,
        'ansible_ssh_user': 'root',
        'ansible_ssh_host': machine_ip,
    }
    dockers[machine_name].update(BASE_PARAMS)

inventory = {
    'localhost': {'ansible_connection': 'local', },
    'dockers': dockers.keys(),
}
inventory['localhost'].update(BASE_PARAMS)
inventory.update(dockers)

json.dump(inventory, sys.stdout)
