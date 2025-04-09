# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Utility functions and classes Overlay management.

This module provides:
- get_overlay: get overlay information and current configuration;
- create_overderlay: create an overlay for the given VRF.
- delete_overderlay: delete the overlay for the given VRF.
"""

from __future__ import annotations

import json

from pydantic import ValidationError

from pyafc.common import utils
from pyafc.services import resource_pools
from pyafc.switches import switches
from pyafc.vrf import models


class Overlay:
    def __init__(self) -> None:
        """__init__ Init Method."""

    def get_overlay(self, name: str) -> dict | bool:
        """get_overlay Find Overlay config.

        Args:
            name (str): Name of the Overlay Config.

        Returns:
            Overlay config data in JSON format and False if not found.

        """
        get_request = self.client.get(
            f"vrfs/{self.uuid}/overlay",
        )
        for overlay in get_request.json()["result"]:
            if overlay["name"] == name:
                return overlay
        return False

    def create_overlay(self, name: str, **kwargs: dict) -> tuple:
        """create_overlay Create Overlay configuration.

        Args:
            name (str): Overlay configuration name.
            description (str, optional) = Overlay's description
            bgp_type (str) = One of:
                - "internal"
                - "external"
            ibgp (dict, optional) = iBGP Configuration. Check example
            ebgp (dict, optional) = eBGP Configuration. Check example
            ipv4_address (str) = IPv4 Resource pool to be used for loopbacks
            keepalive_timer (int, optional) = KeepAlive Timer.
                Defaults to 60
            holddown_timer (int, optional) = Hold Down Timer.
                Defaults to 180

        Example:
            overlay_data = {
                    "ipv4_address": "DC1 Loopback Interfaces",
                    "spine_leaf_asn": "65001",
                    "bgp_type": 'internal'
                    }

            vrf_instance.create_overlay(name="DC1 Overlay",
                                        **overlay_data)

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
            if not ipv4_pool:
                _message = (f"IP Pool {kwargs['ipv4_address']} does not"
                            " exist. No action taken")
                return _message, _status, _changed

            kwargs["ipv4_address"] = ipv4_pool["uuid"]
            if kwargs["bgp_type"] == "internal":
                if not kwargs.get("rr_server"):
                    kwargs["rr_server"] = []
                    switches_list = switches.Switch.get_switches_fabric(
                        self.client,
                        self.fabric_uuid,
                    )
                    for switch in switches_list:
                        if switch["role"] == "spine":
                            kwargs["rr_server"].append(switch["uuid"])
                else:
                    kwargs["rr_server"] = utils.consolidate_switches_list(
                        self.client,
                        kwargs["rr_server"],
                    )

            data = models.Overlay(name=name, **kwargs)
            uri_overlay = f"/vrfs/{self.uuid}/overlay"
            overlay_request = self.client.post(
                uri_overlay,
                data=json.dumps(data.dict(exclude_none=True)),
            )

            if overlay_request.status_code in utils.response_ok:
                _message = "Successfully created Overlay"
                _status = True
                _changed = True
            else:
                if (
                    "Overlay configuration already exists"
                    in overlay_request.json()["result"]
                ):
                    _status = True
                _message = overlay_request.json()["result"]

        except Exception as exc:
            _message = f"An exception {exc} occurred"

        return _message, _status, _changed

    def delete_overlay(self, name: str) -> tuple:
        """delete_overlay Delete the overlay configuration.

        Args:
            name (dict): Name of the overlay.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            overlay = self.get_overlay(name)
            if overlay:
                uri_overlay = f"/vrfs/{self.uuid}/overlay/{overlay['uuid']}"
                overlay_request = self.client.delete(
                    uri_overlay,
                )
                if overlay_request.status_code in utils.response_ok:
                    _message = "Successfully deleted overlay"
                    _status = True
                    _changed = True
                else:
                    _message = overlay_request.json()["result"]
            else:
                _message = f"Overlay {name} does not exist - No action taken"
        except Exception as exc:
            _message = f"An exception {exc} occurred - No action taken"

        return _message, _status, _changed

    def reapply_overlay(self, name: str) -> tuple:
        """reapply_overlay Reapply the overlay configuration on new devices.

        Args:
            name (dict): Name of the overlay.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            data = self.get_overlay(name)
            url_overlay = f"vrfs/{self.uuid}/overlay/{data['uuid']}"
            data = models.OverlayReapply(**data)
            data = utils.remove_null_from_dict(data.dict())
            data["update"] = False
            overlay_request = self.client.put(
                url_overlay,
                data=json.dumps(data),
            )
            if overlay_request.status_code in utils.response_ok:
                _message = "Successfully updated overlay as per the inputs"
                _status = True
                _changed = True
            else:
                _message = overlay_request.json()["result"]

        except ValidationError as exc:
            _message = f"An exception {exc} occurred"

        return _message, _status, _changed
