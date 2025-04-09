# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import utils
from pyafc.services import models


class Syslog:

    def __init__(self, client, name: str, **kwargs: dict) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the Syslog configuration.

        Returns:
            existing_eg (bool): True if available, False if not.

        """
        self.client = client
        self.uuid = None
        self.name = name
        self.existing_syslog = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details Find Syslog Config UUID.

        Args:
            client (Any): AFC Connection object.

        Returns:
            True if found and UUID is set as the class attribute, else False.

        """
        syslog_request = self.client.get("syslog_client_configurations")
        for syslog in syslog_request.json()["result"]:
            if syslog["name"] == self.name:
                self.uuid = syslog["uuid"]
                for item, value in syslog.items():
                    setattr(self, item, value)
                return True
        return False

    @staticmethod
    def get_syslog(client, name: str) -> dict | bool:
        """get_syslog Find Syslog Config.

        Args:
            client (Any): AFC Connection object.
            name (str): Name of the Syslog Config.

        Returns:
            Syslog config data in JSON format and False if not found.

        """
        syslog_request = client.get("syslog_client_configurations")

        for syslog in syslog_request.json()["result"]:
            if syslog["name"] == name:
                return syslog
        return False

    def create_syslog(self, **values: dict) -> tuple:
        """create_syslog Create Syslog configuration.

        Args:
            description (str) = Description
            entry_list (list) = List of Syslog Entries. Check example
            management_software (bool, optional) = Whether or not Management
                Software uses this DNS Client Configuration.
                Defaults to False
            facility (str, optional) = One of:
                - 'LOCAL0'
                - 'LOCAL1'
                - 'LOCAL2'
                - 'LOCAL3'
                - 'LOCAL4'
                - 'LOCAL5'
                - 'LOCAL6'
                - 'LOCAL7'.
                Defaults to 'LOCAL7'.
            logging_persistent_storage (dict, optional) = Persistent Storage
                                                configuration. Check example.
            fabrics (list, optional) = List of Fabrics
            switches (list, optional) = List of Switches

        Example:
            syslog_data = {
                "fabrics": ["DC1"],
                "facility": "LOCAL7",
                "entry_list":
                    [{
                        "host": "1.2.3.4",
                        "severity": "ERROR",
                        "port": 514,
                        "include_auditable_events": True,
                        "transport": "tcp"
                    }]
            }

            syslog_instance = syslog.Syslog(afc_instance.client, name="New_Syslog")
            syslog_instance.create_syslog(**syslog_data,)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_syslog:
                _message = (
                    f"Syslog configuration {self.name} already exists. "
                    "No action taken"
                )
                _status = True
            else:
                temp_values = utils.populate_list_fabrics_switches(
                    self.client,
                    values,
                )

                if "name" in temp_values:
                    del temp_values["name"]

                data = models.Syslog(name=self.name, **temp_values)
                add_request = self.client.post(
                    "syslog_client_configurations",
                    data=json.dumps(data.dict(exclude_none=True)),
                )
                if add_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully applied syslog configuration "
                        f"{self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]

        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while creating "
                f"syslog configuration {self.name}"
            )

        return _message, _status, _changed

    def delete_syslog(self) -> tuple:
        """delete_syslog Delete Syslog configuration.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_syslog:
                delete_request = self.client.delete(
                    f"syslog_client_configurations/{self.uuid}",
                )
                if delete_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully deleted the syslog "
                        f"configuration {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = delete_request.json()["result"]

            else:
                _message = (
                    f"Syslog configuration {self.name} does not exist. "
                    "No action taken"
                )
                _status = True

        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while deleting the "
                f"syslog configuration {self.name}"
            )

        return _message, _status, _changed
