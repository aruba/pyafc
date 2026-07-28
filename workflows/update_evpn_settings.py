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

evpn_settings = input_data["evpn_settings"]

afc_instance = afc.Afc(data=data)

# Update the global EVPN settings of the fabric
fabric_instance = fabric.Fabric(afc_instance.client, name=fabric_name)
message, status, changed = fabric_instance.update_evpn_settings(**evpn_settings)
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
