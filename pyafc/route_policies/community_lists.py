# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import utils
from pyafc.route_policies import models


class CommunityList:

    def __init__(self, client, name: str | None = None, **kwargs: dict) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of Community List.

        Returns:
            existing_eg (bool): True if available, False if not.

        """
        if name:
            self.name = name
        if client:
            self.client = client
        self.uuid = None
        self.existing_cl = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details Get the UUID of Community List.

        Returns:
            None: If found, the UUID is set as a Class attribute.

        """
        community_list_request = self.client.get("community_lists")
        for cl in community_list_request.json()["result"]:
            if cl["name"] == self.name:
                self.uuid = cl["uuid"]
                for item, value in cl.items():
                    setattr(self, item, value)
                return True
        return False

    @staticmethod
    def get_community_list(client, name: str) -> dict | bool:
        """get_community_list Find community list.

        Args:
            client (Any): AFC Connection object.
            name (str): Community List name.

        Returns:
            community_list_data (list): If found, return the\
                community lists else return false.

        """
        uri_community_list = "community_lists"

        community_list_request = client.get(uri_community_list)

        for cl in community_list_request.json()["result"]:
            if cl["name"] == name:
                return cl
        return False

    def create_community_list(self, **values: dict) -> tuple:
        """create_community_list Create community list.

        Args:
            fabric (list) = List of Fabrics
            switches (list, optional) = List of Switches
            type (str) = One of:
                - 'community-list'
                - 'community-expanded-list'
                - 'extcommunity-list'
                - 'extcommunity-expanded-list'
            entries (list) = List of Community List entries. Check example.

        Example:
            cl_data = {
                "switches": ["10.149.2.100-10.149.2.101"],
                "object_type": "community-expanded-list",
                "entries": [
                    {
                        "seq": 10,
                        "action": "permit",
                        "match_string": "internet",
                    }
                ]
                }

            community_list_instance = community_lists.CommunityList(afc_instance.client, name="New_CL")
            community_list_instance.create_community_list(**cl_data,)

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_cl:
                _message = (f"The Community List {self.name} already exists. "
                            "No action taken.")
                _status = True
            else:
                values = utils.populate_list_fabrics_switches(
                    self.client,
                    values,
                )

                if values.get("name"):
                    values.pop("name")

                values["type"] = values["object_type"]

                data = models.CommunityList(name=self.name, **values)

                add_request = self.client.post(
                    "community_lists",
                    data=json.dumps(data.dict(exclude_none=True)),
                )
                if add_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully created community list {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]
        except Exception as exc:
            _message = (f"An exception {exc} occurred while creating "
                        f"community list {self.name}")

        return _message, _status, _changed

    def delete_community_list(self) -> tuple:
        """delete_community_list Delete community list.

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_cl:
                delete_request = self.client.delete(
                    f"community_lists/{self.uuid}",
                )

                if delete_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully deleted community list {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = delete_request.json()["result"]
            else:
                _message = (f"Community List {self.name} does not exist. "
                            "No action taken.")
                _status = True

        except Exception as exc:
            _message = (f"An exception {exc} occurred while deleting "
                        f"community list {self.name}")

        return _message, _status, _changed

    def add_community_list_entry(self, **values: dict) -> tuple:
        """add_community_list_entry Create community list entry.

        Args:
            description (str) = Description
            action (str) = One of 'permit','deny'
            seq (int) = Sequence Number
            match_string (int) = Match String

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            data = models.CommunityListEntry(**values)

            add_request = self.client.post(
                f"community_lists/{self.uuid}/community_lists_entries",
                data=json.dumps(data.dict(exclude_none=True)),
            )
            if add_request.status_code in utils.response_ok:
                _message = (
                    f"Successfully added community list entry to {self.name}"
                )
                _status = True
                _changed = True
            else:
                _message = add_request.json()["result"]

        except Exception as exc:
            _message = (f"An exception {exc} occurred while adding "
                        "community list entry")

        return _message, _status, _changed
