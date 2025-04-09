# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
import yaml
from pyafc.services import snmp

filename = "inputs.yml"
with open(filename, "r") as stream:
    input_data = yaml.load(stream, Loader=yaml.FullLoader)
    stream.close()

data = {
    "ip": input_data["afc_ip"],
    "username": input_data["afc_username"],
    "password": input_data["afc_password"],
}

snmp_data = input_data["snmp_data"]
snmp_name = input_data["snmp_name"]

afc_instance = afc.Afc(data=data)

# Create SNMP configuration
snmp_instance = snmp.Snmp(afc_instance.client, name=snmp_name, **snmp_data)
message, status, changed = snmp_instance.create_snmp(**snmp_data)
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
