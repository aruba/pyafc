# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
import yaml
from pyafc.services import dhcp_relay

filename = "inputs.yml"
with open(filename, "r") as stream:
    input_data = yaml.load(stream, Loader=yaml.FullLoader)
    stream.close()

data = {
    "ip": input_data["afc_ip"],
    "username": input_data["afc_username"],
    "password": input_data["afc_password"],
}

dhcp_relay_data = input_data["dhcp_relay_data"]
dhcp_relay_name = input_data["dhcp_relay_name"]
afc_instance = afc.Afc(data=data)

# Create dhcp relay
dhcp_relay_instance = dhcp_relay.DhcpRelay(
    afc_instance.client, name=dhcp_relay_name, **dhcp_relay_data
)
message, status, changed = dhcp_relay_instance.create_dhcp_relay(**dhcp_relay_data)
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
