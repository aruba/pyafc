# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import utils
from pyafc.services import models


class Ntp:
    def __init__(self, client, name: str, **kwargs: dict) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the NTP.

        Returns:
            existing_eg (bool): True if available, False if not.

        """
        self.client = client
        self.uuid = None
        self.name = name
        self.existing_ntp = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details Find NTP Config UUID.

        Args:
            client (Any): AFC Connection object.

        Returns:
            True if found and UUID is set as the class attribute, else False.

        """
        ntp_request = self.client.get(
            "ntp_client_configurations?in_use_only=false",
        )
        for ntp in ntp_request.json()["result"]:
            if ntp["name"] == self.name:
                self.uuid = ntp["uuid"]
                for item, value in ntp.items():
                    setattr(self, item, value)
                return True
        return False

    @staticmethod
    def get_ntp_configuration(client, name: str) -> dict | bool:
        """get_ntp_configuration Find NTP configuration.

        Args:
            client (Any): AFC Connection object.
            name (str): NTP configuration name.

        Returns:
            NTP Configuration JSON data if found, else False.

        """
        uri_ntp = "ntp_client_configurations"

        ntp_request = client.get(uri_ntp)

        for ntp in ntp_request.json()["result"]:
            if ntp["name"] == name:
                return ntp
        return False

    def create_ntp(self, **kwargs: dict) -> tuple:
        """create_ntp Create NTP configuration.

        Args:
            description (str) = Description
            fabrics (list, optional) = List of Fabrics
            switches (list, optional) = List of Switches
            entry_list (list) = List of NTP Entries. Check example

        Example:
            ntp_data = {
                    "fabrics": ["DC1"],
                    "servers": [
                        {
                            "server": "10.100.100.111",
                            "burst_mode": "iburst",
                            "prefer": True
                        }]
                    }

            ntp_instance = ntp.Ntp(afc_instance.client, name="New_NTP")
            ntp_instance.create_ntp(**ntp_data,)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:

            if self.existing_ntp:
                _message = (
                    f"The NTP configuration {self.name} already"
                    " exists. No action taken."
                )
                _status = True
            else:
                kwargs = utils.populate_list_fabrics_switches(
                    self.client, kwargs
                )

                if "name" in kwargs:
                    del kwargs["name"]

                data = models.Ntp(name=self.name, **kwargs)

                add_request = self.client.post(
                    "ntp_client_configurations",
                    data=json.dumps(data.dict()),
                )
                if add_request.status_code in utils.response_nok:
                    _message = (
                        f"Successfully configured NTP settings " f"{self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]

        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while creating "
                f"NTP configuration {self.name}"
            )

        return _message, _status, _changed

    def delete_ntp(self) -> tuple:
        """delete_ntp Delete NTP configuration.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is deleted, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_ntp:
                delete_request = self.client.delete(
                    f"ntp_client_configurations/{self.uuid}",
                )
                if delete_request.status_code in utils.response_ok:
                    _message = f"Successfully deleted NTP settings {self.name}"
                    _status = True
                    _changed = True
                else:
                    _message = delete_request.json()["result"]
            else:
                _message = (
                    f"NTP configuration {self.name} does not exist. "
                    "No action taken."
                )
                _status = True

        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while deleting "
                f"NTP configuration {self.name}"
            )

        return _message, _status, _changed
