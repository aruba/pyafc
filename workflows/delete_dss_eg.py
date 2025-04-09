# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
from pyafc.dss import endpoint_groups
import yaml

filename = "inputs.yml"
with open(filename, "r") as stream:
    input_data = yaml.load(stream, Loader=yaml.FullLoader)
    stream.close()

data = {
    "ip": input_data["afc_ip"],
    "username": input_data["afc_username"],
    "password": input_data["afc_password"],
}

dss_eg_name = input_data["dss_eg_name"]
dss_eg_data = input_data["dss_eg_data"]

afc_instance = afc.Afc(data=data)

# Delete Endpoint Group
eg_instance = endpoint_groups.EndpointGroup(afc_instance.client, name=dss_eg_name)
message, status, changed = eg_instance.delete_eg()
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
