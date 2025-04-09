# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Utility functions and classes Underlay management.

This module provides:
- get_underlay: get underlay information and current configuration;
- create_underlay: create an Underlay for the given VRF.
- delete_underlay: delete the Underlay for the given VRF.
"""

from __future__ import annotations

import json

from pydantic import ValidationError

from pyafc.common import utils
from pyafc.services import resource_pools
from pyafc.vrf import models


class Underlay:

    def __init__(self) -> None:
        """__init__ Init Method."""

    def get_underlay(self, name: str) -> dict | bool:
        """get_underlay - function to get underlay configuration.

        Args:
            name (str): Name of the Underlay in AFC

        Returns:
            underlay: Underlay information

        """
        get_request = self.client.get(
            f"vrfs/{self.uuid}/underlay",
        )
        for underlay in get_request.json()["result"]:
            if underlay["name"] == name:
                return underlay
        return False

    def create_underlay(self, name: str, **kwargs: dict) -> tuple:
        """create_underlay - function to create underlay configuration.

        Args:
            description (str) = Underlay's description
            underlay_type (str) = Underlay Type. One of:
                 - "OSPF"
                 - "EBGP"
            bfd (bool, optional) = Enable Bidirectional Forwarding Detection.
                         Default to False
            transit_vlan (int) = Transit VLAN ID
            ipv4_address (str) = Resource Pool used to create loopbacks
            ospf (dist, optional) = OSPF Configuration used for Underlay.
                Check example.
            bgp (dist, optional) = BGP Configuration used for Underlay.
                Check example.

        Example:
            underlay_data = {
                    "ipv4_address": "DC2 Underlay IP",
                    "transit_vlan": 120,
                    "underlay_type": "OSPF"
                    }

            vrf_instance2.create_underlay(name="Underlay DC2",
                                          **underlay_data)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            ipv4_pool = resource_pools.Pool.get_resource_pool(
                self.client,
                kwargs["ipv4_address"],
                "IPv4",
            )
            if ipv4_pool:
                kwargs["ipv4_address"] = ipv4_pool["uuid"]
                data = models.Underlay(name=name, **kwargs)
                uri_underlay = f"/vrfs/{self.uuid}/underlay"
                underlay_request = self.client.post(
                    uri_underlay,
                    data=json.dumps(data.dict(exclude_none=True)),
                )
                if underlay_request.status_code in utils.response_ok:
                    _message = (
                        "Successfully configured underlay as per the inputs"
                    )
                    _status = True
                    _changed = True
                elif "already exists" in underlay_request.json()["result"]:
                    _message = ("The underlay configuration already exists. "
                                "No action taken")
                    _status = True
                else:
                    _message = underlay_request.json()["result"]
            else:
                _message = (f"IP Pool {kwargs['ipv4_address']} does not exist."
                            " No action taken")
        except ValidationError as exc:
            _message = f"An exception {exc} occurred, No action taken"

        return _message, _status, _changed

    def delete_underlay(self, name: str) -> tuple:
        """delete_underlay Delete underlay configuration.

        Args:
            name (dict): Name of the Underlay.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            underlay = self.get_underlay(name)
            if underlay:
                uri_underlay = f"/vrfs/{self.uuid}/underlay/{underlay['uuid']}"
                underlay_request = self.client.delete(
                    uri_underlay,
                )
                if underlay_request.status_code in utils.response_ok:
                    _message = "Successfully deleted underlay"
                    _status = True
                    _changed = True
                else:
                    _message = underlay_request.json()["result"]
            else:
                _message = (f"Underlay {name} does not exist. "
                            "No action taken")
        except Exception as exc:
            _message = f"An exception {exc} occurred. No action taken"

        return _message, _status, _changed

    def reapply_underlay(self, name: dict) -> tuple:
        """reapply_underlay Reapply the underlay configuration on new devices.

        Args:
            name (dict): Name of the Underlay.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False
        try:
            data = self.get_underlay(name)
            url_underlay = f"vrfs/{self.uuid}/underlay/{data['uuid']}"
            data = models.UnderlayReapply(**data)
            data = utils.remove_null_from_dict(data.dict())
            data["update"] = False
            underlay_request = self.client.put(
                url_underlay,
                data=json.dumps(data),
            )
            if underlay_request.status_code in utils.response_ok:
                _message = "Successfully updated underlay"
                _status = True
                _changed = True
            else:
                _message = underlay_request.json()["result"]
        except ValidationError as exc:
            _message = f"An exception {exc} occurred"

        return _message, _status, _changed
