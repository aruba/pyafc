# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Utility functions and classes Networks management.

This module provides:
- get_network_uuid: get Network UUID
- create_network: Create a Network for AMD Pensando Chipsets in Aruba 10k
- delete_network: Delete a Network on AMD Pensando Chipsets in Aruba 10k
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from pydantic import ValidationError

from pyafc.common import utils
from pyafc.vrf import models

if TYPE_CHECKING:
    from httpx import Client


class Network:
    def __init__(self) -> None:
        """__init__ Init Method."""

    def create_network(self, **kwargs: dict) -> tuple:
        """create_network Create Network configuration.

        Args:
            name (str): Network Name.
            vlan_id (int): VLAN ID.

        Example:
            vrf_instance.create_network(name="Network_VLAN10", vlan_id=10)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            data = models.Network(**kwargs)
            uri_network = f"/vrfs/{self.uuid}/networks"
            existing_networks = self.client.get(uri_network).json()["result"]
            vlan_exists = False
            for network in existing_networks:
                if (
                    network["name"] == kwargs["name"]
                    or network["vlan_id"] == kwargs["vlan_id"]
                ):
                    vlan_exists = True

            if not vlan_exists:
                network_request = self.client.post(
                    uri_network,
                    data=json.dumps(data.dict()),
                )

                if network_request.status_code in utils.response_ok:
                    _message = f"Successfully created VLAN {kwargs['vlan_id']}"
                    _status = True
                    _changed = True
                else:
                    _message = network_request.json()["result"]
            else:
                _status = True
                _message = (f"Network with VLAN {kwargs['vlan_id']} already exists "
                            "on that VRF. No action taken")

        except ValidationError as exc:
            _message = f"An exception {exc} occurred"

        return _message, _status, _changed

    def update_network(self, **kwargs: dict) -> tuple:
        """create_network Create Network configuration.

        Args:
            name (str): Network Name.
            vlan_id (int): VLAN ID.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            data = models.Network(**kwargs)
            networks_request = self.client.get(f"/vrfs/{self.uuid}/networks")
            existing_networks = networks_request.json()["result"]
            vlan_exists = False
            for network in existing_networks:
                if (
                    network["name"] == kwargs["name"]
                    or network["vlan_id"] == kwargs["vlan_id"]
                ):
                    vlan_exists = True
                    break

            if vlan_exists:
                for key, value in data.dict(exclude_none=True).items():
                    network[key] = value

                network_request = self.client.put(
                    f"/vrfs/{self.uuid}/networks/{network['uuid']}",
                    data=json.dumps(network),
                )
                if network_request.status_code in utils.response_ok:
                    _message = f"Successfully updated VLAN {kwargs['vlan_id']}"
                    _status = True
                    _changed = True
                else:
                    _message = network_request.json()["result"]
            else:
                _message = (f"Network with VLAN {kwargs['vlan_id']} does "
                            "not exist on that VRF. No action taken")

        except ValidationError as exc:
            _message = f"An exception {exc} occurred"

        return _message, _status, _changed

    def delete_network(self, **kwargs: dict) -> tuple:
        """delete_network Delete Network configuration.

        Args:
            name (str): Network Name.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            uri_network = f"/vrfs/{self.uuid}/networks"
            existing_networks = self.client.get(uri_network).json()["result"]
            vlan_exists = False
            for network in existing_networks:
                if network["name"] == kwargs["name"]:
                    vlan_exists = True
                    vlan_uuid = network["uuid"]
            if vlan_exists:
                uri_delete_network = f"/vrfs/{self.uuid}/networks/{vlan_uuid}"
                network_request = self.client.delete(
                    uri_delete_network,
                )
                if network_request.status_code in utils.response_ok:
                    _message = f"Successfully deleted Network {kwargs['name']}"
                    _status = True
                    _changed = True
                else:
                    _message = network_request.json()["result"]
            else:
                _message = (f"Network {kwargs['name']} does not exist. "
                            "No action taken")

        except ValidationError as exc:
            _message = f"An exception {exc} occurred"

        return _message, _status, _changed

    @staticmethod
    def get_network_uuid(
        client: Client, name: str, vrf_uuid: int
    ) -> str | bool:
        """get_network_uuid Find Network UUID from the VRF.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the Network.
            vrf_uuid (str): VRF UUID.

        Returns:
            Network UUID and False if not found.

        """
        network_request = client.get(f"/vrfs/{vrf_uuid}/networks")
        for network in network_request.json()["result"]:
            if network["name"] == name:
                return network["uuid"]
        return False
