# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from __future__ import annotations

import json

from pyafc.common import utils
from pyafc.route_policies import models


class PrefixList:

    def __init__(self, client, name: str | None = None, **kwargs: dict) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of Prefix List.

        Returns:
            existing_eg (bool): True if available, False if not.

        """
        if name:
            self.name = name
        if client:
            self.client = client
        self.uuid = None
        self.existing_pl = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details Find Prefix List UUID.

        Returns:
            If found, the UUID is set as a Class attribute

        """
        pl_request = self.client.get("prefix_lists")
        for pl in pl_request.json()["result"]:
            if pl["name"] == self.name:
                self.uuid = pl["uuid"]
                for item, value in pl.items():
                    setattr(self, item, value)
                return True
        return False

    @staticmethod
    def get_prefix_list(client, name: str) -> dict | bool:
        """get_prefix_list Get prefix list.

        Args:
            client (Any): AFC Connection object.
            name (str): Prefix list name.

        Returns:
            JSON Data of prefix list.

        """
        pl_request = client.get("prefix_lists")

        for pl in pl_request.json()["result"]:
            if pl["name"] == name:
                return pl
        return False

    def create_prefix_list(self, **values: dict) -> tuple:
        """create_prefix_list Create prefix list.

        Args:
            description (str): Description of the Prefix list
            fabric (list, optional) = List of Fabrics
            switches (list, optional) = List of Switches
            entries (list) = List of Prefix List entries. Check example.

        Example:
            pl_data = {
                "switches": ["10.149.2.100-10.149.2.101"],
                "entries": [
                    {
                        "seq": 10,
                        "action": "permit",
                        "prefix": "192.168.1.0/24",
                    },
                ]
                }

            prefix_list_instance = prefix_lists.PrefixList(afc_instance.client, name="New_PFL")
            prefix_list_instance.create_prefix_list(**pl_data,)

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_pl:
                _message = (f"The Prefix List {self.name} already exists. "
                            "No action taken.")
                _status = True
            else:
                values = utils.populate_list_fabrics_switches(
                    self.client,
                    values,
                )

                if values.get("name"):
                    values.pop("name")

                data = models.PrefixList(name=self.name, **values)

                add_request = self.client.post(
                    "prefix_lists",
                    data=json.dumps(data.dict(exclude_none=True)),
                )
                if add_request.status_code in utils.response_ok:
                    _message = f"Successfully created prefix list {self.name}"
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]
        except Exception as exc:
            _message = (f"An exception {exc} occurred while creating the "
                        f"prefix list {self.name}")

        return _message, _status, _changed

    def delete_prefix_list(self) -> tuple:
        """delete_prefix_list Delete prefix list.

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_pl:
                delete_request = self.client.delete(
                    f"prefix_lists/{self.uuid}",
                )

                if delete_request.status_code in utils.response_ok:
                    _message = f"Successfully deleted prefix list {self.name}"
                    _status = True
                    _changed = True
                else:
                    _message = delete_request.json()["result"]
            else:
                _message = (f"The Prefix List {self.name} does not exist. "
                            "No action taken.")
                _status = True

        except Exception as exc:
            _message = (f"An exception {exc} occurred while deleting the "
                        "prefix list {self.name}")

        return _message, _status, _changed

    def add_prefix_list_entry(self, **values: dict) -> tuple:
        """add_prefix_list_entry Add prefix list entry.

        Args:
            description (str) = Description
            action (str) = One of 'permit','deny'
            seq (int) = Sequence Number
            prefix (str) = IP Prefix or 'any'
            ge (int) = Greater than
            le (int) = Less than

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            data = models.PrefixListEntry(**values)

            add_request = self.client.post(
                f"prefix_lists/{self.uuid}/prefix_list_entries",
                data=json.dumps(data.dict(exclude_none=True)),
            )
            if add_request.status_code in utils.response_ok:
                _message = (
                    f"Successfully added prefix list entry on {self.name}"
                )
                _status = True
                _changed = True
            else:
                _message = add_request.json()["result"]
        except Exception as exc:
            _message = (f"An exception {exc} occurred while adding "
                        f"prefix list entry on {self.name}")

        return _message, _status, _changed
