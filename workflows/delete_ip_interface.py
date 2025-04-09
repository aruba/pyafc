# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.vrf import vrf
from pyafc.afc import afc
import yaml
from pyafc.fabric import fabric

filename = "inputs.yml"
with open(filename, "r") as stream:
    input_data = yaml.load(stream, Loader=yaml.FullLoader)
    stream.close()

data = {
    "ip": input_data["afc_ip"],
    "username": input_data["afc_username"],
    "password": input_data["afc_password"],
}

fabric_name = input_data["fabric_name"]
vlan_name = input_data["l2vni_props"]["ip_interface"]["name"]
ip_intf_data = input_data["l2vni_props"]["ip_interface"]

vrf_data = input_data["vrf_props"]
vrf_name = input_data["vrf_name"]

afc_instance = afc.Afc(data=data)

# Delete IP Interface
fabric_instance = fabric.Fabric(afc_instance.client, name=fabric_name)
vrf_instance = vrf.Vrf(
    afc_instance.client, name=vrf_name, fabric_uuid=fabric_instance.uuid, **vrf_data
)
message, status, changed = vrf_instance.delete_ip_interface(**ip_intf_data)
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
