# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
from pyafc.dss import policies
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

dss_policy_name = input_data["dss_policy_name"]
dss_policy_data = input_data["dss_policy_data"]

afc_instance = afc.Afc(data=data)

# Create DSS Policy
policy_instance = policies.Policy(afc_instance.client, name=dss_policy_name)
message, status, changed = policy_instance.create_policy(**dss_policy_data)
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
