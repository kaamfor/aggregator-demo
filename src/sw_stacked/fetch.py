import requests
from bs4 import BeautifulSoup

from model import DeviceLink, DeviceEntry

from typing import Dict, List, Tuple

base_url = '<DEVICE-URL>'
stacked_switch_access = {
    'pwd': '<DEVICE-PASSWORD>',
    'login_button.x': 13,
    'login_button.y': 6,
    'err_flag': 0,
    'err_msg': '',
    'submt': ''
}

# TODO: create check!
def login(http_session: requests.Session) -> bool:
    e = http_session.post(base_url+'/base/netgear_login.html', data=stacked_switch_access)
    return True


def fetch_devices(http_session: requests.Session) -> List[DeviceEntry]:
    sw_infos = fetch_hw_infos(http_session)
    print('stacked1', sw_infos)
    
    device_list: List[DeviceEntry] = []
    
    def new_device(vlan_id, mac, port, status) -> DeviceEntry:
        link = DeviceLink(
            sw_name=sw_infos.get('System Name', ''),
            port_id=port,
            vlan=int(vlan_id),
            status=status
        )
        
        entry = DeviceEntry(
            mac=mac, ip='', port_links=[link]
        )
        return entry
    
    ## Create device list based on MAC address table
    
    mac_table = http_session.get(base_url+'/basicAddressTable.html')
    mac_table_soup = BeautifulSoup(mac_table.text, 'html.parser')
    
    for entry in mac_table_soup.find_all(id='1_2')[1:]:
        # [VLAN ID, MAC Address, Port, status]
        # (there's a hidden, unprocessed col: 2)
        row_data = map(lambda i: str(entry.find_all(id='1_2_'+str(i))[0].input['value']).strip(), [1,3,4,6])
        
        device_list.append(new_device(*row_data))
    
    ## Collect and set link descriptions
    
    port_description = fetch_port_descriptions(http_session)
    
    for link_list in map(lambda device: device.port_links, device_list):
        assert len(link_list)
        
        for link in link_list:
            link.port_description = port_description.get(link.port_id, link.port_description)
    
    return device_list

# ['System Name', ...]
# ['System Location', ...]
# ['System Contact', ...]
# ['Serial Number', ...]
# ['System Object OID', ...]
# ['Date & Time', ...]
# ['System Up Time', ...]
# ['Base MAC Address', ...]
def fetch_hw_infos(http_session: requests.Session) -> Dict[str, str]:
    output_dict = {}
    
    hw_info = http_session.get(base_url+'/base/system/management/sysInfo.html')
    hw_info_soup = BeautifulSoup(hw_info.text, 'html.parser')
    
    info_tbl = hw_info_soup.table.table.table
    
    for row in info_tbl.find_all('tr'):
        keypair = row.find_all('td')
        
        if len(keypair) >= 2:
            key = keypair[0].get_text().strip()
            if not key:
                continue
            
            got_select = keypair[1].find_all('select')
            got_input = keypair[1].find_all('input')
            if len(got_select):
                check_selected_attr = lambda tag: tag.name == 'option' and tag.has_attr('selected')
                
                default_option_arr = got_select[0].find_all(check_selected_attr)
                if len(default_option_arr):
                    default_value = default_option_arr[0].get_text()
                else:
                    default_value = got_select.option.get_text()
                    print(456)
                
                value = default_value
            elif len(got_input):
                value = keypair[1].input['value']
            else:
                value = keypair[1].get_text().strip()
            
            output_dict[key] = value
    
    return output_dict

def fetch_port_descriptions(http_session: requests.Session) -> Dict[str, str]:
    ## Collect port description
    port_description = {}
    
    descr_html = http_session.get(base_url+'/portsConfiguration.html')
    descr_soup = BeautifulSoup(descr_html.text, 'html.parser')
    
    for entry in descr_soup.find_all(id='1_2')[1:]:
        # [Port] [Description] [Port Type] [Admin Mode] [Port Speed] [Physical Status] [Link Status] [Link Trap] [Maximum Frame Size (1518 to 9216)] [MAC Address] [PortList Bit Offset] [ifindex]
        row_data = list(map(lambda i: str(entry.find_all(id='1_2_'+str(i))[0].get_text()).strip(), [1,2,4,6,7,9,10,11,12,15,16,13]))
        
        if len(row_data) >= 2:
            port, name = row_data[0], row_data[1]
            port_description[port] = name
    
    return port_description