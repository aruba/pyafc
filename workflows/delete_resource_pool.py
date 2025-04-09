# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
import yaml
from pyafc.services import resource_pools

filename = "inputs.yml"
with open(filename, "r") as stream:
    input_data = yaml.load(stream, Loader=yaml.FullLoader)
    stream.close()

data = {
    "ip": input_data["afc_ip"],
    "username": input_data["afc_username"],
    "password": input_data["afc_password"],
}

resource_pool_data = input_data["resource_pool_data"]
resource_pool_name = input_data["resource_pool_name"]

afc_instance = afc.Afc(data=data)

# Delete Resource Pool
resource_pool_instance = resource_pools.Pool(
    afc_instance.client, name=resource_pool_name
)
message, status, changed = resource_pool_instance.delete_pool()
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
