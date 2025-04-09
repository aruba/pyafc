# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import utils
from pyafc.services import models


class Sflow:
    def __init__(self, client, name: str, **kwargs: dict) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the sFlow configuration.

        Returns:
            existing_eg (bool): True if available, False if not.

        """
        self.client = client
        self.uuid = None
        self.name = name
        self.existing_sflow = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details Find SFlow Config UUID.

        Returns:
            True if found and UUID is set as the class attribute, else False.

        """
        sflow_request = self.client.get("sflow_configurations")
        for sflow in sflow_request.json()["result"]:
            if sflow["name"] == self.name:
                self.uuid = sflow["uuid"]
                for item, value in sflow.items():
                    setattr(self, item, value)
                return True
        return False

    @staticmethod
    def get_sflow(client, name: str) -> dict | bool:
        """get_sflow Find SFlow Config.

        Args:
            client (Any): AFC Connection object.
            name (str): Name of the SFlow Config.

        Returns:
            SFlow config data in JSON format and False if not found.

        """
        sflow_request = client.get("sflow_configurations")

        for sflow in sflow_request.json()["result"]:
            if sflow["name"] == name:
                return sflow
        return False

    def create_sflow(self, **values: dict) -> tuple:
        """create_sflow Create SFlow configuration.

        Args:
            description (str, optional) = Description
            enable_sflow (bool, optional) = Enable sFlow or not.
                Defaults to True
            polling_interval (int, optional) = Polling Interval.
                Defaults to 20.
            sampling_rate (int, optional) = Sampling Rate.
                Defaults to 20000
            collectors (list) = List of collectors. Check example.
            fabrics (list, optional) = List of Fabrics
            switches (list, optional) = List of Switches

        Example:
            sflow_data = {
                    "fabrics": ["DC1"],
                    "collectors": [
                        {
                        "destination_port": 6343,
                        "destination_ip_address": "10.10.10.10",
                        }]
                }

            sflow_instance = sflow.Sflow(afc_instance.client, name="New_Sflow")
            sflow_instance.create_sflow(**sflow_data,)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_sflow:
                _message = (
                    f"The sFlow configuration {self.name} already "
                    "exists. No action taken"
                )
                _status = True
            else:
                temp_values = utils.populate_list_fabrics_switches(
                    self.client, values
                )

                if "name" in temp_values:
                    del temp_values["name"]

                data = models.Sflow(**temp_values)
                add_request = self.client.post(
                    "sflow_configurations",
                    data=json.dumps(data.dict(exclude_none=True)),
                )
                if add_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully applied sFlow configuration {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]

        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while creating "
                "sFlow configuraiton {self.name}"
            )

        return _message, _status, _changed

    def delete_sflow(self) -> tuple:
        """delete_sflow Delete SFlow configuration.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_sflow:
                delete_request = self.client.delete(
                    f"sflow_configurations/{self.uuid}",
                )
                if delete_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully deleted the "
                        f"sFlow config {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = delete_request.json()["result"]

            else:
                _message = (
                    f"The sFlow configuration {self.name} does "
                    "not exist. No action taken"
                )
                _status = True

        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while deleting the "
                f"sFlow configuration {self.name}"
            )

        return _message, _status, _changed
