# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import utils
from pyafc.services import models


class Snmp:
    def __init__(self, client, name: str, **kwargs: dict) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the SNMP configuration.

        Returns:
            existing_eg (bool): True if available, False if not.

        """
        self.client = client
        self.uuid = None
        self.name = name
        self.existing_snmp = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details Find SNMP Config UUID.

        Returns:
            True if found and UUID is set as the class attribute, else False.

        """
        snmp_request = self.client.get("snmp_configurations")
        for inst in snmp_request.json()["result"]:
            if inst["name"] == self.name:
                self.uuid = inst["uuid"]
                for item, value in inst.items():
                    setattr(self, item, value)
                return True
        return False

    @staticmethod
    def get_snmp(client, name: str) -> dict | bool:
        """get_snmp Find SNMP Config.

        Args:
            client (Any): AFC Connection object.
            name (str): Name of the SNMP Config.

        Returns:
            SNMP config data in JSON format and False if not found.

        """
        snmp_request = client.get("snmp_configurations")

        for inst in snmp_request.json()["result"]:
            if inst["name"] == name:
                return inst
        return False

    def create_snmp(self, **values: dict) -> tuple:
        """create_snmp Create SNMP configuration.

        Args:
            description (str) = Description
            enable (bool, optional) = Configuration enabled.
                Defaults to True
            location (str, optional) = SNMP Location
            contact (str, optional) = SNMP contact
            community (str, optional) = SNMP community
            agent_port (int, optional) = Agent Port.
                Defaults to 161
            trap_port (int, optional) = Trap Port
            users (list, optional) = List of SNMPv3 Users. Check example
            servers (list, optional) = List of SNMP Trap Servers. Check example
            fabrics (list, optional) = List of Fabrics
            switches (list, optional) = List of Switches

        Example:
            snmp_data = {
                "fabrics": ["DC1"],
                "location": "DC1",
                "contact": "admin",
                "community": "dcn_community",
                "trap_port": 23,
                "agent_port": 161,
                "servers":
                    [{
                        "address": "1.2.3.4",
                        "community": "dcn_community",
                    }]
            }

            snmp_instance = snmp.Snmp(afc_instance.client, name="New_SNMP")
            snmp_instance.create_snmp(**snmp_data,)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_snmp:
                _message = (
                    f"SNMP configuration {self.name} already exists. "
                    "No action taken."
                )
                _status = True
            else:
                values = utils.populate_list_fabrics_switches(
                    self.client,
                    values,
                )
                if values.get("servers"):
                    values["trap_sink"] = values["servers"]

                if "name" in values:
                    del values["name"]

                data = models.Snmp(name=self.name, **values)

                add_request = self.client.post(
                    "snmp_configurations",
                    data=json.dumps(data.dict(exclude_none=True)),
                )
                if add_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully applied SNMP configuration {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]

        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while creating "
                f"SNMP configuration {self.name}"
            )

        return _message, _status, _changed

    def delete_snmp(self) -> tuple:
        """delete_snmp Delete SNMP configuration.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_snmp:
                delete_request = self.client.delete(
                    f"snmp_configurations/{self.uuid}",
                )

                if delete_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully deleted SNMP configuration {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = delete_request.json()["result"]
            else:
                _message = (
                    f"SNMP configuration {self.name} does not"
                    " exist. No action taken"
                )
                _status = True

        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while deleting "
                f"SNMP configuraiton {self.name}"
            )

        return _message, _status, _changed
