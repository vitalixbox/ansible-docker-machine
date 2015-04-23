# Intro

This is plugins collection for working with docker-machine through ansible.

Provided plugins:
* **Connection plugin** This plugin extends local.py connection plugin and set environment variables DOCKER_HOST, DOCKER_CERT_PATH, DOCKER_TLS_VERIFY to every exec commands. 
* **Machines creation/deletion module** This module is wrapper on docker-machine create/rm command. Include only DigitalOcean drivers.
* **Dynamic inventory** Build inventory from local configured docker-machine's.

# How to test

This command create new machine on DigitalOcean with name test-machine and deploy nginx container on test-machine:
```bash
ansible-playbook -i hosts.py playbook.yml -e token=YOU_DIGITALOCEAN_TOKEN
# And you may open browser and see "Welcome to nginx!". Ip is - `docker-machine ip test-machine`
```

This is equivalent:
* `docker-machine create --driver=digitalocean --digitalocean-access-token=YOU_DIGITALOCEAN_TOKEN test-machine`
* `docker $(docker-machine config test-machine) run --name nginx -d -p 80:80 nginx`
