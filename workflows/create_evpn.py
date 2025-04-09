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

evpn_name = input_data["l2vni_props"]["l2vni"]["name_prefix"]

l2vni = input_data["l2vni_props"]["l2vni"]

afc_instance = afc.Afc(data=data)

# Create eVPN
fabric_instance = fabric.Fabric(afc_instance.client, name=fabric_name)
message, status, changed = fabric_instance.create_evpn(name=evpn_name, **l2vni)
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
