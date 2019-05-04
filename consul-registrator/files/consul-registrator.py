#!/usr/bin/python
# -*- coding: utf-8 -*-

import signal
import sys
import requests
import docker
import os
import socket
import json
import logging
import subprocess
import re
from ConsulPayload import *


def main():

    if len(sys.argv) == 2:

        if 'start' == sys.argv[1]:
            # daemonize main process
            # with daemon.DaemonContext():
            logging.info("starting daemon monitoring  routine")
            watch_daemon()

        elif 'stop' == sys.argv[1]:
            logging.info("stopping daemon")
            os.kill(os.getpid(), signal.SIGTERM)
            logging.info("daemon stopped")

        elif 'restart' == sys.argv[1]:
            logging.info("restarting daemon")
            os.kill(os.getpid(), signal.SIGTERM)
            watch_daemon()
            logging.info("Daemon restarted")
        else:
            logging.warning("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        logging.info("main if failed :- usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)


def get_client():
    cli = docker.APIClient(base_url=data["base_url"], version='auto')
    return cli


def callonevent(cli):
    thismodule = sys.modules[__name__]
    events = cli.events(decode=True)
    for event in events:
        if str(event["Action"]) in ["start", "stop", "destroy"]:
            logging.debug(str(event["Action"])+" \n")
            if (hasattr(thismodule, event['Action'])):
                getattr(thismodule, event['Action'])(cli, event)


def watch_daemon():
    cli = get_client()
    logging.info("Started listening  for the events")
    find_existing_containers(cli)
    callonevent(cli)

def verify_service(Service_Name):
    resp = requests.get(data["url"] + "agent/services", headers=data["token"]   )
    registered_services = json.loads(resp.content)

    if service_name in registered_services.keys():
        return True
    else:
        return False

def find_existing_containers(cli): 
    icons_names = [ json.dumps(container['Names'][0]) for container in cli.containers() ]
    for container_name in icons_names: 
       container_name = container_name.strip('\"\/')
       if not re.search("k8s_POD", container_name):
            final_payload = construct_payload(service_fulldata(container_name))
            logging.info("final_payload")
            register_service(final_payload, container_name)
            logging.info("register_service")

def start(cli, event):
    logging.info("start event captured")
    container_name = event["Actor"]["Attributes"]["name"]
    container_name = container_name.strip('\"\/')
    if not re.search("k8s_POD", container_name):
           logging.info("container_name")
           final_payload = construct_payload(service_fulldata(container_name))
           logging.info("final_payload")
           register_service(final_payload, container_name)
           logging.info("register_service")

def stop(cli, event):
    logging.info("stop event captured")
    container_name = event["Actor"]["Attributes"]["name"]
    logging.info("container " + container_name + " stopped streaming logs below \n")
    logging.info(cli.logs(container_name))
    deregister_service(container_name, event)


def destroy(cli, event):

    logging.info("remove event captured")
    container_name = event["Actor"]["Attributes"]["name"]
    deregister_action = 'agent/service/deregister/' + container_name

    try:
        if container_name:
            logging.info("container_name " + str(container_name))
            resp = requests.put(url=data["url"] + deregister_action, headers=data["token"])
            logging.info("Destroy agent/service/de-register HTTP returned code: " + str(resp.status_code))
            if resp.status_code == requests.codes.ok:
                logging.info(container_name + "  de-registered")
            else:
                logging.error("service " + container_name + " failed to de-register.")

    except ValueError:
        logging.error("Value error " + str(ValueError))
        container_data = ''

def restart(cli,event):
    logging.info("restart event captured")
    destroy(cli, event)
    start(cli, event)


def register_service(final_payload, container_name):
    try:
        logging.info("payload type " + str(type(final_payload)))
        resp = requests.put(url=data["url"] + "agent/service/register", data=json.dumps(final_payload), headers=data["token"])
        # status code check
        logging.info("agent/service/regist HTTP returned code: " + str(resp.status_code))
        if resp.status_code == requests.codes.ok:
            logging.info("service " + container_name + " registered.")
        else:
            logging.error("service " + container_name + " failed to register.")
    except Exception as e:
        logging.error(e)


def deregister_service(container_name, event):

    container_data = service_fulldata(container_name)
    Service_Name = service_name(container_data)
    Url_Extension = "{}/{}".format("agent/service/deregister", Service_Name)
    try:
        logging.info("token " + str(data["token"]))
        logging.info("url " + str(data["url"]))
        resp = requests.put(url=data["url"] + Url_Extension, headers=data["token"])
        logging.info("agent/service/de-register HTTP returned code: " + str(resp.status_code))
        if resp.status_code == requests.codes.ok:
            logging.info(Service_Name + "  de-registered")
        else:
            logging.error("service " + container_name + " failed to de-register.")
    except Exception as e:
        logging.error(e)
        logging.info(Service_Name + " does not exist.")


#logging.basicConfig(filename='/var/log/consul-registrator.log', level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='/var/log/consul-registrator.log', level=logging.DEBUG)


if __name__ == "__main__":
    with open(os.getcwd() + "/config.json", "r") as config:
        data = json.loads(config.read())
    main()
