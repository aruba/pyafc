# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
import yaml
from pyafc.route_policies import route_maps

filename = "inputs.yml"
with open(filename, "r") as stream:
    input_data = yaml.load(stream, Loader=yaml.FullLoader)
    stream.close()

data = {
    "ip": input_data["afc_ip"],
    "username": input_data["afc_username"],
    "password": input_data["afc_password"],
}

route_map_name = input_data["route_map_name"]
route_map_data = input_data["route_map_data"]

afc_instance = afc.Afc(data=data)

# Create route map
route_map_instance = route_maps.RouteMap(afc_instance.client, name=route_map_name)
message, status, changed = route_map_instance.create_routemap(**route_map_data)
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
