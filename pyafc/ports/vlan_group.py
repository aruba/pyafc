# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

import json

from pyafc.common import utils
from pyafc.ports import models


class VlanGroup:
    def __init__(self, client, name: str, **kwargs: dict) -> None:
        self.client = client
        self.uuid = None
        self.name = name
        self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details Check if the vlan_group exists.

        Args:
            None

        Returns:
            True if the Vlan Group is found, else False.

        """
        vlan_groups_request = self.client.get("vlan_groups")
        for vlan_group in vlan_groups_request.json()["result"]:
            if vlan_group["name"] == self.name:
                for item, value in vlan_group.items():
                    setattr(self, item, value)
                return True
        return False

    def create_vlan_group(self, **kwargs: dict) -> tuple:
        """create_vlan_group Create Vlan Group.

        Args:
            name (str, optional): VLAN Group Name.
            description (str, optional): VLAN Group Description
            vlans (str, optional): VLANs to be pammed to this group.

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _status = False
        _message = ""
        _changed = False

        try:
            if self.__instantiate_details():
                _message = f"The VLAN Group {self.name} already exists. \
                            No action taken"
                _status = True
            else:

                if kwargs.get("name"):
                    kwargs.pop("name")

                data = models.VlanGroup(name=self.name, **kwargs)
                uri_vlan_groups = "vlan_groups"
                vlan_groups_request = self.client.post(
                    uri_vlan_groups,
                    data=json.dumps(data.dict()),
                )
                if vlan_groups_request.status_code in utils.response_ok:
                    _message = "Successfully created VLAN Group"
                    _status = True
                    _changed = True
                else:
                    _message = vlan_groups_request.json()["result"]
        except Exception as exc:
            _message = f"An issue occured - {exc}. No action taken"

        return _message, _status, _changed

    def delete_vlan_group(self) -> tuple:
        """delete_vlan_group Delete vlan Group.

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _status = False
        _message = ""
        _changed = False

        try:
            uri_vlan_groups = f"vlan_groups/{self.uuid}"
            vlan_groups_request = self.client.delete(uri_vlan_groups)
            if vlan_groups_request.status_code in utils.response_ok:
                _message = "Successfully deleted VLAN Group"
                _status = True
                _changed = True
            else:
                _message = vlan_groups_request.json()["result"]
        except Exception as exc:
            _message = f"An issue occured - {exc}. No action taken"

        return _message, _status, _changed
