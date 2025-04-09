# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

import json

from pyafc.common import utils
from pyafc.services import models


class Dns:
    def __init__(self, client, name: str, **kwargs: dict) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the DNS.

        Returns:
            existing_eg (bool): True if available, False if not.

        """
        self.client = client
        self.uuid = None
        self.name = name
        self.existing_dns = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details Find DNS config UUID.

        Returns:
            If found, the UUID is set as a Class attribute.

        """
        dns_request = self.client.get(
            "dns_client_configurations?in_use_only=false"
        )
        for dns in dns_request.json()["result"]:
            if dns["name"] == self.name:
                self.uuid = dns["uuid"]
                for item, value in dns.items():
                    setattr(self, item, value)
                return True
        return False

    @staticmethod
    def get_dns(client, name: str) -> dict | bool:
        """get_dns Get DNS client configuration.

        Args:
            client (Any): AFC Connection object.
            name (str): DNS Entry name.

        Returns:
            If found, the DNS configuration is returned, else False.

        """
        dns_request = client.get("dns_client_configurations?in_use_only=false")

        for dns in dns_request.json()["result"]:
            if dns["name"] == name:
                return dns
        return False

    def create_dns(self, **kwargs: dict) -> tuple:
        """create_dns Create DNS configuration.

        Args:
            description (str) = Description
            domain_name (str, optional) = Domain Name.
                Not required if "domain_list" is used.
            name_servers (list, optional) = List of DNS Servers
            domain_list (list, optional) = List of Domains Names.
                Not required if "domain_name" is used.
            management_software (bool, optional) = Whether or not Management
                Software uses this DNS Client Configuration.
                Defaults to False
            fabrics (list, optional) = List of Fabrics
            switches (list, optional) = List of Switches

        Example:
            dns_data = {
                "fabrics": ["DC1"],
                "domain_name": "example.com",
                "name_servers": ["1.2.3.4"]
            }

            dns_instance = dns.Dns(afc_instance.client, name="New_DNS")
            dns_instance.create_dns(**dns_data,)

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:

            if self.existing_dns:
                _message = (
                    f"The DNS entry {self.name} already exists. "
                    "No action taken."
                )
                _status = True
            else:
                kwargs = utils.populate_list_fabrics_switches(
                    self.client, kwargs
                )

                if "name" in kwargs:
                    del kwargs["name"]

                data = models.Dns(name=self.name, **kwargs)
                add_request = self.client.post(
                    "dns_client_configurations",
                    data=json.dumps(data.dict()),
                )
                if add_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully created DNS configuration "
                        f"{self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]
        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while creating "
                f"DNS configuration {self.name}"
            )

        return _message, _status, _changed

    def delete_dns(self) -> tuple:
        """delete_dns Delete DNS configuration.

        Returns:
            message: Action message.
            status: True if successful, otherwise False.
            changed: True if deleted, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_dns:
                delete_request = self.client.delete(
                    f"dns_client_configurations/{self.uuid}",
                )

                if delete_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully deleted DNS configuration "
                        f"{self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = delete_request.json()["result"]
            else:
                _message = (
                    f"The DNS entry {self.name} does not exist. "
                    "No action taken."
                )
                _status = True

        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while "
                "deleting DNS configuration {self.name}"
            )

        return _message, _status, _changed
