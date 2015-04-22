Collection of modules for ansible

* Connection plugin for run ansible modules through docker-machine
* Dynamic inventory for docker-machine
* Module for creating ans deleting machines through docker-machine

# How to test

```bash
# Create new machine with docker_machine module [TODO]
ansible-playbook -i hosts.py playbook.yml --tags create -e token=YOU_DIGITALOCEAN_TOKEN

# Deploy nginx to new machine with docker_machine connection plugin
ansible-playbook -i hosts.py playbook.yml --tags deploy
```
