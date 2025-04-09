# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
import yaml
from pyafc.services import dns

filename = "inputs.yml"
with open(filename, "r") as stream:
    input_data = yaml.load(stream, Loader=yaml.FullLoader)
    stream.close()

data = {
    "ip": input_data["afc_ip"],
    "username": input_data["afc_username"],
    "password": input_data["afc_password"],
}

dns_data = input_data["dns_data"]
dns_name = input_data["dns_name"]

afc_instance = afc.Afc(data=data)

# Delete DNS entry
dns_instance = dns.Dns(afc_instance.client, name=dns_name)
message, status, changed = dns_instance.delete_dns()
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
