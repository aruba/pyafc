# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
import yaml
from pyafc.services import ntp

filename = "inputs.yml"
with open(filename, "r") as stream:
    input_data = yaml.load(stream, Loader=yaml.FullLoader)
    stream.close()

data = {
    "ip": input_data["afc_ip"],
    "username": input_data["afc_username"],
    "password": input_data["afc_password"],
}

ntp_data = input_data["ntp_data"]
ntp_name = input_data["ntp_name"]
afc_instance = afc.Afc(data=data)

# Delete NTP configuration
ntp_instance = ntp.Ntp(afc_instance.client, name=ntp_name)
message, status, changed = ntp_instance.delete_ntp()
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
