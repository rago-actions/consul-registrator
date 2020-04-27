consul-registrator
==================

This will help u to build the Consul based service registry for your openshift cluster.


There are three files which are important to do this job.

1. consul-registrator.py
   This python program does below things
   - connects to the docker client using unix socket
   - watches the daemon for start, stop, destroy and restart of docker events
   - if there is an event it logs the debug information to /var/log/consul-registrator.log
   - if there's a start event, then it takes the container name then builds the payload using ConsulPayload.py  & registers the service.
   - if there's a stop event then simply deregisters the service
   - if there's a remove event then it de-registers the service
   - if there's a restart event then it de-registers and re-register the service

2. ConsulPayload.py
   - This python program prapares the payload to pass it to REST API

3. consul-registrator.service
   - This is service unit file which creates service for start/stop/restart
   
4. How to apply consul-registrator role to multple nodes in one Go?
   - Please read [readme.md](http://github.anim.dreamworks.com/PSO/consul-registrator/blob/master/consul-registrator/README.md) of the consul-registrator role.
   
5. How to uninstall consul-registrator agent from a single/multiple servers
   - Update the correct hosts list in hosts file
   - run below command to uninstall the consul-registrator agent from a specific host
   ```sh
   ansible-playbook -i hosts uninstall_CR.yml -l <specific host name>
   ```
   

6. Jira Tickets

| Jira Ticket | Description | Developed/Reviewd by |
| ------ | ------ | ------ |
| PE-529 | Research on register docker container to consul for service catalog | Ramesh |
| PE-576  | Implement/ Test service registry | Ramesh |
| PE-615 | Integration Test - Service Registry and Consul Agent | Tim |
| PE-723 | Deploy consul-registrator agent to Tesseract | Ramesh |
| PSO-20322 | problem register service into consul | Ramesh |
| PE-743 | Update consul-registrator agent to register existing services | Ramesh |
