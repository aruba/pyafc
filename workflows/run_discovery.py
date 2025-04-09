# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.switches import switches
from pyafc.afc import afc
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

discovery_data = {
    "admin_passwd": input_data["switch_credentials"]["admin_passwd"],
    "afc_admin_passwd": input_data["switch_credentials"]["afc_admin_passwd"],
    "service_account_user": input_data["switch_credentials"]["service_account_user"],
}

devices_list = input_data["devices_list"]

afc_instance = afc.Afc(data=data)

# Discover switches
switches_instance = switches.Switch(
    afc_instance.client,
)
message, status, changed = switches_instance.discover_multiple_devices(
    devices_list, **discovery_data
)
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
