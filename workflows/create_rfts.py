# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
import yaml
from pyafc.services import rfts

filename = "inputs.yml"
with open(filename, "r") as stream:
    input_data = yaml.load(stream, Loader=yaml.FullLoader)
    stream.close()

data = {
    "ip": input_data["afc_ip"],
    "username": input_data["afc_username"],
    "password": input_data["afc_password"],
}

rfts_data = input_data["rfts_data"]
rfts_name = input_data["rfts_name"]

afc_instance = afc.Afc(data=data)

# Create Remote File Transfer Server
rfts_instance = rfts.Rfts(afc_instance.client, name=rfts_name, **rfts_data)
message, status, changed = rfts_instance.create_rfts(**rfts_data)
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
