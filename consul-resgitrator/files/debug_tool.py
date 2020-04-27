#!/usr/bin/python

import requests
import json

acl_token = {'X-Consul-Token': '6935fe0c-16b0-be15-14f3-c60826ddc59d'}
agent_url = 'http://127.0.0.1:8500/v1'
#agent_url = 'http://10.172.6.21:8500/v1'
#agent_url = 'http://d_con_pso_discovery.db.gld.dreamworks.net:8500/v1'
deregister_action = agent_url + '/agent/service/deregister'
list_service = agent_url + '/agent/services'
print(list_service)
get_service_list = requests.get(list_service, headers=acl_token)
print(json.dumps(get_service_list.json(), indent=2))

catalog_action = agent_url + '/catalog/services'
get_catalog = requests.get(catalog_action, headers=acl_token)
print(get_catalog.status_code)
print(json.dumps(get_catalog.json(), indent=2))
if get_catalog.json().keys():
  for key in get_catalog.json().keys():
    if key == "consul":
      continue
    else:
      rs = deregister_action + '/' + key
      rs_result = requests.put(rs, headers=acl_token)
      print('Remove ' + str(key) + ' status : ' + str(rs_result.status_code))


#rm_json_string = '{"Address": "172.17.0.3", "Datacenter": "gld", "Node": "10.172.6.21", "ServiceID": "naughty_mayer"}'

#catalog_rm = agent_url + '/catalog/deregister'
#r_catalog = requests.put(catalog_rm, headers=acl_token, data=rm_json_string)
#print(r_catalog.status_code)
~                                
