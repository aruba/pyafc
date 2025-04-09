# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.afc import afc
import yaml
from pyafc.services import syslog

filename = "inputs.yml"
with open(filename, "r") as stream:
    input_data = yaml.load(stream, Loader=yaml.FullLoader)
    stream.close()

data = {
    "ip": input_data["afc_ip"],
    "username": input_data["afc_username"],
    "password": input_data["afc_password"],
}

syslog_data = input_data["syslog_data"]
syslog_name = input_data["syslog_name"]
afc_instance = afc.Afc(data=data)

# Delete syslog configuration
syslog_instance = syslog.Syslog(afc_instance.client, name=syslog_name)
message, status, changed = syslog_instance.delete_syslog()
print(f"Message: {message}\nStatus: {status}\nChanged: {changed}")
