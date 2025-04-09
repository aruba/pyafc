# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
from pyafc.dss import qualifiers
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

dss_qualifier_name = input_data["dss_qualifier_name"]
dss_qualifier_data = input_data["dss_qualifier_data"]

afc_instance = afc.Afc(data=data)

# Delete DSS Qualifier
qualifiers_instance = qualifiers.Qualifier(afc_instance.client, name=dss_qualifier_name)
message, status, changed = qualifiers_instance.delete_qualifier()
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
