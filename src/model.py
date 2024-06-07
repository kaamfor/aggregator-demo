from dataclasses import dataclass
from typing import Dict, List

@dataclass
class DeviceLink:
    sw_name: str
    port_id: str
    vlan: int
    status: str = ''
    port_description: str = ''

@dataclass
class DeviceEntry:
    mac: str
    port_links: List[DeviceLink]
    ip: str = ''
    name: str = ''
    
