# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

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
vrf_name = input_data["vrf_name"]
l3ls_data = input_data["l3ls_data"]

afc_instance = afc.Afc(data=data)

# Create Leaf Spine configuration
fabric_instance = fabric.Fabric(afc_instance.client, name=fabric_name)
message, status, changed = fabric_instance.create_l3ls(
    name=l3ls_data["name"], leaf_spine_ip_pool_range=l3ls_data["pool_ranges"]
)
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
