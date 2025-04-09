# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
from pyafc.dss import rules
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

dss_rule_data = input_data["dss_rule_data"]
dss_rule_name = input_data["dss_rule_name"]

afc_instance = afc.Afc(data=data)

# Delete DSS Rule
rules_instance = rules.Rule(afc_instance.client, name=dss_rule_name)
message, status, changed = rules_instance.delete_rule()
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
