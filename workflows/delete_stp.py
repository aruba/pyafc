# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
import yaml
from pyafc.services import stp

filename = "inputs.yml"
with open(filename, "r") as stream:
    input_data = yaml.load(stream, Loader=yaml.FullLoader)
    stream.close()

data = {
    "ip": input_data["afc_ip"],
    "username": input_data["afc_username"],
    "password": input_data["afc_password"],
}

stp_data = input_data["stp_data"]
stp_name = input_data["stp_name"]
afc_instance = afc.Afc(data=data)

# Delete STP Configuration
stp_instance = stp.STP(afc_instance.client, name=stp_name)
message, status, changed = stp_instance.delete_stp()
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
