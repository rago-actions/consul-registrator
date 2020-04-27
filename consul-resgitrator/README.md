consul-registrator
=========
This Role helps you to build the service-registery for openshift cluster.

Requirements
------------
This role required of logging and docker python modules but we are installating them using the same playbook.

```sh
yum install python-pip
import logging
import json
import docker
```
Role Variables
--------------
defaults/main.yml has one variable which is
```sh
consul_files_path: /etc/consul-registrator
```
we are storing our payload and consul-registrator script in above location, if u wanna deploy these files in a different location the change the value of this variable.

vars/main.yml has 3 variables which are
```sh
1. Consul_Token: ##Give the token
2. Consul_Url:  ##Accpets valid consul cluster url ex: http://localhost:8500/v1/
3. Consul_Env: ##Accepts string as a value ex: dev or prod
```

Dependencies
------------
This role does not depend on any other roles.

Example Playbook
----------------
```sh
- hosts: openshift
  gather_facts: true
  vars: 
   Consul_Url: 'http://localhost:8500/v1/'
   Consul_Token: 'xxxxxxxxxxxxxxxxxxxxxxxxx'
   Consul_Env: 'dev'
  roles:
    - consul-registrator
```
License
-------

BSD

Author Information
------------------
Ramesh Godishela <iamrago@yahoo.com>
