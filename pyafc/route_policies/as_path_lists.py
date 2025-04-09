# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from __future__ import annotations

import json

from pyafc.common import utils
from pyafc.route_policies import models


class ASPathList:

    def __init__(self, client, name: str | None = None, **kwargs: dict) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of AS Path List.

        Returns:
            existing_eg (bool): True if available, False if not.

        """
        if name:
            self.name = name
        if client:
            self.client = client
        self.uuid = None
        self.existing_aspath = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details Check if ASPath list exists.

        Returns:
            ASPath List UUID

        """
        checkpoint_request = self.client.get("aspath_lists")
        for checkpoint in checkpoint_request.json()["result"]:
            if checkpoint["name"] == self.name:
                self.uuid = checkpoint["uuid"]
                for item, value in checkpoint.items():
                    setattr(self, item, value)
                return True
        return False

    @staticmethod
    def get_aspath_list(client, name: str) -> dict | bool:
        """get_aspath_list Find aspath list. If found, returns the aspath list.

        Args:
            name (str): ASPath name.
            type (str): ASPath type.

        Returns:
            ASPath List (list): Properties of the ASPath List.

        """
        uri_aspath_list = "aspath_lists"

        apl_request = client.get(uri_aspath_list)

        for apl in apl_request.json()["result"]:
            if apl["name"] == name:
                return apl
        return False

    def create_aspath_list(self, **values: dict) -> tuple:
        """create_aspath_list Create ASPath List.

        Args:
            description (str): Description of the AS Path list
            fabric (list, optional) = List of Fabrics
            switches (list, optional) = List of Switches
            entries (list) = List of AS Path List entries. Check example.

        Example:
            asp_data = {
                "switches": ["10.149.2.100-10.149.2.101"],
                "entries": [
                    {
                        "seq": 10,
                        "action": "permit",
                        "regex": "^65100_",
                    },
                    {
                        "seq": 20,
                        "action": "permit",
                        "regex": "^65100$",
                    },
                ]
                }

            aspath_list_instance = as_path_lists.ASPathList(afc_instance.client, name="New_APL")
            aspath_list_instance.create_aspath_list(**asp_data,)

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_aspath:
                _message = (f"The requested ASPath List {self.name} already "
                            "exists. No action taken")
                _status = True
            else:
                values = utils.populate_list_fabrics_switches(
                    self.client, values,
                )

                if values.get("name"):
                    values.pop("name")

                data = models.ASPathList(name=self.name, **values)

                add_request = self.client.post(
                    "aspath_lists",
                    data=json.dumps(data.dict(exclude_none=True)),
                )
                if add_request.status_code in utils.response_ok:
                    _message = f"Successfully created the aspath {self.name}"
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]
        except Exception as exc:
            _message = (f"An exception {exc} occurred while creating "
                        f"ASPath {self.name}")

        return _message, _status, _changed

    def delete_aspath_list(self) -> tuple:
        """delete_aspath_list Delete ASPath List.

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_aspath:
                delete_request = self.client.delete(
                    f"aspath_lists/{self.uuid}",
                )

                if delete_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully deleted the ASPath list {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = delete_request.json()["result"]

            else:
                _message = (f"The requested ASPath {self.name} does not exist. "
                            "No action taken")
                _status = True

        except Exception as exc:
            _message = (f"An exception {exc} occurred while deleting "
                        "ASPath {self.name}")

        return _message, _status, _changed
