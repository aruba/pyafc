# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import utils
from pyafc.services import models
from pyafc.switches import switches


class STP:
    def __init__(self, client, name: str, **kwargs: dict) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the STP configuration.

        Returns:
            existing_eg (bool): True if available, False if not.

        """
        self.client = client
        self.uuid = None
        self.name = name
        self.existing_stp = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details Find STP Config UUID.

        Returns:
            True if found and UUID is set as the class attribute, else False.

        """
        stp_request = self.client.get("spanning_tree/stp_configuration")
        for stp in stp_request.json()["result"]:
            if stp["name"] == self.name:
                self.uuid = stp["uuid"]
                return True
        return False

    @staticmethod
    def get_stp(client, name: str):
        """get_stp Find STP Config.

        Args:
            client (Any): AFC Connection object.
            name (str): Name of the STP Config.
            type (str): Type of the STP config.

        Returns:
            STP config data in JSON format and False if not found.

        """
        radius_request = client.get("spanning_tree")

        for srv in radius_request.json()["result"]:
            if srv["name"] == name:
                return srv
        return False

    @staticmethod
    def configure_stp_global(client, **kwargs: dict) -> tuple:
        """configure_stp_global Configure Global configuration.

        Args:
            client (Any): AFC Connection object.
            kwargs (dict): Global STP configuration data.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        values = []

        try:
            if kwargs.get("switches"):
                values["switch_uuids"] = []
                if isinstance(values["switches"], str):
                    switch_uuid = switches.Switch.get_switch_uuid(
                        client,
                        values["switches"],
                    )
                    values["switch_uuids"].append(switch_uuid)
                else:
                    for switch in values["switches"]:
                        switch_uuid = switches.Switch.get_switch_uuid(
                            client, switch
                        )
                        values["switch_uuids"].append(switch_uuid)

            global_change = []
            change_payload = {"uuids": [kwargs.uuid], "patch": []}
            for item, item_value in kwargs.items():
                change_payload["patch"].append(
                    {"path": f"/{item}", "value": item_value, "op": "replace"}
                )
            global_change.append(change_payload)
            port_request = client.patch(
                "ports", data=json.dumps(global_change)
            )
            if port_request.status_code in utils.response_ok:
                _message = (
                    f"Successfully applied STP configuration {kwargs.name}"
                )
                _status = True
                _changed = True
            else:
                _message = port_request.json()["result"]

        except Exception:
            _message = "An exception occurred while configuring STP global"

        return _message, _status, _changed

    def create_stp(self, **kwargs: dict) -> tuple:
        """create_stp Create STP configuration.

        Args:
            description (str, optional) = Description
            config_type (str, optional) = One of:
                - 'mstp'
                - 'stp.
                Defaults to 'mstp'
            configuration (dict) = STP Configuration

        Example:
            stp_data = {
                "fabrics": ["DC1"],
                "config_type": "mstp",
                "configuration": {
                    "mstp_config": {
                        "config_revision": 0,
                        "config_name": "MSTP_Configuration"
                        }
                    }
            }
            stp_instance = stp.STP(afc_instance.client, name="New_STP")
            stp_instance.create_stp(**stp_data,)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_stp:
                _message = (
                    f"STP configuration {self.name} already exists. "
                    "No action taken"
                )
                _status = True
            else:

                if "name" in kwargs:
                    del kwargs["name"]

                data = models.Stp(name=self.name, **kwargs)
                stp_request = self.client.post(
                    "spanning_tree/stp_configuration",
                    data=json.dumps(data.dict(exclude_none=True)),
                )

                if stp_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully created STP configuration {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = stp_request.json()["result"]

        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while "
                f"configuring STP {self.name}"
            )

        return _message, _status, _changed

    def delete_stp(self) -> tuple:
        """delete_stp Delete STP configuration.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_stp:
                stp_request = self.client.delete(
                    f"spanning_tree/stp_configuration/{self.uuid}",
                )

                if stp_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully deleted STP configuration "
                        f"{self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = stp_request.json()["result"]
            else:
                _message = (
                    f"STP configuration {self.name} does not exist. "
                    "No action taken"
                )
                _status = True

        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while deleting "
                f"STP {self.name}"
            )

        return _message, _status, _changed
