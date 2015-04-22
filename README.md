# How to test

```bash
# Create new machine with docker_machine module [TODO]
ansible-playbook -i hosts.py playbook.yml --tags create -e token=YOU_DIGITALOCEAN_TOKEN

# Deploy nginx to new machine with docker_machine connection plugin
ansible-playbook -i hosts.py playbook.yml --tags deploy
```
