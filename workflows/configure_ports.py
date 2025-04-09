# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
import yaml
from pyafc.ports import ports

filename = "inputs.yml"
with open(filename, "r") as stream:
    input_data = yaml.load(stream, Loader=yaml.FullLoader)
    stream.close()

data = {
    "ip": input_data["afc_ip"],
    "username": input_data["afc_username"],
    "password": input_data["afc_password"],
}

ports_data = input_data["ports_data"]

afc_instance = afc.Afc(data=data)

# Configure Ports
message, status, changed = ports.PORT.configure_multiple_physical_port(
    afc_instance.client, ports_data
)
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
