# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
import yaml
from pyafc.route_policies import prefix_lists

filename = "inputs.yml"
with open(filename, "r") as stream:
    input_data = yaml.load(stream, Loader=yaml.FullLoader)
    stream.close()

data = {
    "ip": input_data["afc_ip"],
    "username": input_data["afc_username"],
    "password": input_data["afc_password"],
}

prefix_list_name = input_data["prefix_list_name"]
prefix_list_data = input_data["prefix_list_data"]

afc_instance = afc.Afc(data=data)

# Create prefix list
prefix_list_instance = prefix_lists.PrefixList(
    afc_instance.client, name=prefix_list_name
)
message, status, changed = prefix_list_instance.create_prefix_list(**prefix_list_data)
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
