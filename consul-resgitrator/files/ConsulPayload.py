import docker
import json
import os
import socket
import subprocess
import logging
import re

# Connect to the Docker Client using socket communication
client = docker.APIClient(base_url='unix://var/run/docker.sock', version='auto')


# Print Json Content in pretty format
def pp_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


# Inspects the Container Data
def service_fulldata(con_name):
    try:
        container_data = client.inspect_container(con_name)
    except docker.errors.NotFound:
        raise ValueError("404 Client Error: Not Found: " + con_name)
    return container_data


# Pull the service name from Container data
def service_name(container_data):
    try:
        ServiceName = container_data['Config']['Labels']['io.kubernetes.pod.name']  # podname
    except KeyError:
       if container_data['Name']:
          ContainerName = container_data['Name']
          ServiceName = ContainerName.strip('\"\/') 
    logging.info('service name ' + ServiceName)
    return ServiceName

# Pull the IP Address from Container data
def service_address(container_data):
    if container_data['NetworkSettings']['IPAddress']:
        ServiceAddress = container_data['NetworkSettings']['IPAddress']  # podipaddress
    else:
        ServiceAddress = None
    logging.info('service address ' + str(ServiceAddress))
    return ServiceAddress


# Pull the Namespace details from Container data
def service_namespace(container_data):
    Namespace = []
    try:
        Namespace.append("sd:namespace={}".format( container_data['Config']['Labels']['io.kubernetes.pod.namespace']))  # namespace the pod belong to
    except KeyError:
        Namespace.append("sd:namespace=None")
    logging.info('namespace ' + str(Namespace))
    return Namespace

# Parse the namespace
def service_namespace_parse(container_data):
    Parsed_Namespace = []
    namespace = service_namespace(container_data)
    if 'None' not in namespace[0].split("=")[1]:
       ns_list = namespace[0].split("=")[1].split("-")
       try:
          Parsed_Namespace.append("sd:org={}".format(ns_list[0]))
       except:
          Parsed_Namespace.append("sd:org=None")

       try:
          Parsed_Namespace.append("sd:show={}".format(ns_list[1]))
       except:
          Parsed_Namespace.append("sd:show=None")

       try:
          Parsed_Namespace.append("sd:env={}".format(ns_list[2]))
       except:
          Parsed_Namespace.append("sd:env=None")
    else:
       Parsed_Namespace.append("sd:org=None")
       Parsed_Namespace.append("sd:show=None")
       Parsed_Namespace.append("sd:env=None")

    return Parsed_Namespace
   
#Pull the Docker Digest details
def service_dockerdigest(container_data):
    docker_digest = []
    try:
      docker_digest.append("sd:dockerdigest={}".format(container_data['Image']))
    except: 
      docker_digest.append("sd:dockerdigest=None")
    return docker_digest

# Pull the pod creation details
def service_creationtime(container_data):
    service_created = []
    try:
      service_created.append("sd:created={}".format(container_data['Created']))
    except:
      service_created.append("sd:created=None")
    return service_created

# Pull the Image details from Container data
def service_image(container_data):
    Image = []
    if container_data['Config']['Image']:
        Image.append("sd:image={}".format(container_data['Config']['Image']))  # Pod image
    else:
        Image.append("sd:image=None")
    logging.info("service_image " + str(Image))
    return Image

# Pull the LogPath details from Container data
def service_logpath(container_data):
    LogPath = []
    if container_data['LogPath']:
        LogPath.append("sd:logpath={}".format(container_data['LogPath']))  # container log location path
    else:
        LogPath.append("sd:logpath=None")
    logging.info('logpath ' + str(LogPath))
    return LogPath

# Pull the Ports details from Container data
def service_ports(container_data):
    Ports = []
    PortsList = []
    if container_data['NetworkSettings']['Ports']:
        Ports = container_data['NetworkSettings']['Ports']  # ports
        for PortItem in Ports:
           PortsList.append("sd:port={}".format(PortItem))
        Ports = PortsList
    else:
        Ports.append("ports:None")
    logging.info('ports ' + str(Ports))
    return Ports

# Pull the Networks details from Container data
def service_networks(container_data):
    Networks = []
    if container_data['NetworkSettings']['Networks']:
        Networks = container_data['NetworkSettings']['Networks']  # network info
        NetworksList = []
        for i in Networks: 
           for j in Networks[i]: 
              NetworksList.append("sd:{}={}".format(j,Networks[i][j])) 
        Networks = NetworksList
    else: 
        Networks.append("networks:None")
    logging.info('networks ' + str(Networks))
    return Networks

# Pull the Volumes details from Container data
def service_volumes(container_data):
    Volumes = []
    if container_data['Config']['Volumes']:
        Volumes.append("sd:volumes={}".format((k) for k,v in container_data['Config']['Volumes'].items()))  # volumes
    else:
        Volumes.append("sd:volumes=None")
    logging.info('Volumes ' + str(Volumes))
    return Volumes

# Pull the Labels details from Container data
def service_labels(container_data):
    Labels = []
    if container_data['Config']['Labels']:
        Labels = container_data['Config']['Labels']  # labels
        LabelsList = []
        for LabelItem in Labels:
            if (LabelItem == "com.dreamworks.groupId") or \
                    (LabelItem == "com.dreamworks.version") or \
                    (LabelItem == "com.dreamworks.service"):
                logging.info('label item ' + LabelItem)
                LabelsList.append("sd:{}={}".format(LabelItem, Labels[LabelItem]))
            else:
                continue

        Labels = LabelsList
    else:
        Labels.append("sd:labels=None")
    logging.info('Labels' + str(Labels))
    return Labels

# Pull the Container State details from Container data
def service_state(container_data):
    State = []
    if container_data['State']:
        State = container_data['State']  # container state
        StateList = []
        for StateItem in State:
           StateList.append("sd:{}={}".format(StateItem, State[StateItem]))
        State = StateList
    else:
        State.append("sd:state=None")
    logging.info('State ' + str(State))
    return State

# Pull the Container Host details from Container data
def service_nodedata():
    nodedata = []
    nodename = "sd:nodename={}".format(socket.gethostname())
    nodeip = "sd:nodeipaddress={}".format(socket.gethostbyname(socket.gethostname()))
    nodedata.append(nodename)
    nodedata.append(nodeip)
    return nodedata

# Constrcut the payload to pass it to Consul Cluster API
def construct_payload(container_data):
    final_payload = {}
    final_payload['Tags'] = service_namespace(container_data) + \
                            service_namespace_parse(container_data) + \
                            service_image(container_data) + \
                            service_dockerdigest(container_data) + \
                            service_volumes(container_data) + \
                            service_labels(container_data) + \
                            service_creationtime(container_data) + \
                            service_nodedata()

    final_payload["Address"] = service_address(container_data)
    final_payload["Name"] = service_name(container_data)
    return final_payload
