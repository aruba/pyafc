# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
import yaml
from pyafc.route_policies import community_lists

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

community_list_name = input_data["community_list_name"]
community_list_data = input_data["community_list_data"]
afc_instance = afc.Afc(data=data)

# Create community list
community_list_instance = community_lists.CommunityList(
    afc_instance.client, name=community_list_name
)
message, status, changed = community_list_instance.create_community_list(
    **community_list_data
)
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
