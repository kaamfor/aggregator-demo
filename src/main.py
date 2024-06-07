import datetime
import requests
from bottle import get, run, static_file, error, request, response, template, auth_basic
from typing import List, Dict, Callable

from model import DeviceEntry, DeviceLink

MIN_FETCH_TIME = datetime.timedelta(seconds=1)

# bottle - from standalone python file
# beautifulSoup

username = '<CUSTOM-PASSWORD>'
password = '<CUSTOM-PASSWORD>'

def auth_check(user, pw):
    return user == username and pw == password

from sw_m4100.fetch import fetch_devices as sw_m4100_fetch, login as sw_m4100_login
from sw_stacked.fetch import fetch_devices as sw_stacked_fetch, login as sw_stacked_login

polling_targets = [sw_m4100_fetch, sw_stacked_fetch]
setup_method = {sw_m4100_fetch: sw_m4100_login, sw_stacked_fetch: sw_stacked_login}


session_dict: Dict[Callable[[requests.Session], List[DeviceEntry]], requests.Session] = {target: requests.Session() for target in polling_targets}
# Setup session
for target, session in session_dict.items():
    setup_method[target](session)
    # TODO: check reply!

time_last_fetched = datetime.datetime.min
def list_devices() -> List[DeviceEntry]:
    if datetime.datetime.now() - time_last_fetched < MIN_FETCH_TIME:
        return
    
    # MAC <-> Device assignment
    device_dict = {}
    for target, session in session_dict.items():
        current_dict = {dev.mac: dev for dev in target(session)}
        
        if not len(device_dict):
            device_dict = current_dict
            continue
        
        mac_addresses = set(device_dict.keys()).intersection(set(current_dict.keys()))
        for mac in mac_addresses:
            current_dict[mac].port_links.extend(device_dict[mac].port_links)
        
        device_dict.update(current_dict)
    
    return device_dict.values()

@get('/')
@get('/<refresh:int>')
@auth_basic(auth_check)
def index(refresh: int = 600):
    device_list = list_devices()
    
    return template('index.tpl', refresh=refresh, device_list=device_list)

@get('/static/<filename>')
@auth_basic(auth_check)
def server_static(filename):
    return static_file(filename, root='./static')

@error(404)
def error404(error):
    return '404 - Nothing here, fella'

run(host='0.0.0.0', port=8080, debug=True)
