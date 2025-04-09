# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
import yaml
from pyafc.services import radius

filename = "inputs.yml"
with open(filename, "r") as stream:
    input_data = yaml.load(stream, Loader=yaml.FullLoader)
    stream.close()

data = {
    "ip": input_data["afc_ip"],
    "username": input_data["afc_username"],
    "password": input_data["afc_password"],
}

radius_name = input_data["radius_name"]

afc_instance = afc.Afc(data=data)

# Create Radius configuration
radius_instance = radius.Radius(afc_instance.client, name=radius_name)
message, status, changed = radius_instance.delete_radius()
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
