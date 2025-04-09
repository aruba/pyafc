# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
import yaml
from pyafc.services import sflow

filename = "inputs.yml"
with open(filename, "r") as stream:
    input_data = yaml.load(stream, Loader=yaml.FullLoader)
    stream.close()

data = {
    "ip": input_data["afc_ip"],
    "username": input_data["afc_username"],
    "password": input_data["afc_password"],
}

sflow_data = input_data["sflow_data"]
sflow_name = input_data["sflow_name"]

afc_instance = afc.Afc(data=data)

# Create SFlow configuration
sflow_instance = sflow.Sflow(afc_instance.client, name=sflow_name, **sflow_data)
message, status, changed = sflow_instance.create_sflow(**sflow_data)
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
