# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
import yaml
from pyafc.fabric import fabric
from pyafc.vrf import vrf

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
vrf_name = input_data["vrf_name"]

ospf_area_name = input_data["ospf_area_name"]
ospf_area_data = input_data["ospf_area_data"]

afc_instance = afc.Afc(data=data)

# Create OSPF Area
fabric_instance = fabric.Fabric(afc_instance.client, name=fabric_name)
vrf_instance = vrf.Vrf(
    afc_instance.client, name=vrf_name, fabric_uuid=fabric_instance.uuid
)
message, status, changed = vrf_instance.create_ospf_area(
    name=ospf_area_name, **ospf_area_data
)
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
