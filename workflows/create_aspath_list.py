# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
import yaml
from pyafc.route_policies import as_path_lists

filename = "inputs.yml"
with open(filename, "r") as stream:
    input_data = yaml.load(stream, Loader=yaml.FullLoader)
    stream.close()

data = {
    "ip": input_data["afc_ip"],
    "username": input_data["afc_username"],
    "password": input_data["afc_password"],
}

fabric_data = {"timezone": input_data["fabric_timezone"]}

fabric_name = input_data["fabric_name"]

as_path_list_name = input_data["as_path_list_name"]
as_path_list_data = input_data["as_path_list_data"]
afc_instance = afc.Afc(data=data)

# Create route_map
aspath_list_instance = as_path_lists.ASPathList(
    afc_instance.client, name=as_path_list_name
)
message, status, changed = aspath_list_instance.create_aspath_list(**as_path_list_data)
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
