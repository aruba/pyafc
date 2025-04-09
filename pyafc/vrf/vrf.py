# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Utility functions and classes for VRF management.

This module provides:
- get_vrf_uuid: Get VRF UUID;
- get_ip_interfaces: Get IP Interfaces for the specified VRF
- get_ip_interface: Get IP Interface for the specified VRF
- create_vrf: create a VRF.
- delete_vrf: delete a VRF.
- reapply_vrf: Reapply VRF.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from pydantic import ValidationError

from pyafc.common import exceptions, utils
from pyafc.switches import switches
from pyafc.vrf import (
    bgp,
    ip_interfaces,
    models,
    networks,
    ospf,
    overlay,
    static_routes,
    underlay,
)

if TYPE_CHECKING:
    from httpx import Client


class Vrf(
    underlay.Underlay,
    overlay.Overlay,
    bgp.BGP,
    ospf.OSPF,
    networks.Network,
    ip_interfaces.IPInterface,
    static_routes.StaticRoute,
):
    """Vrf CLass representing a VRF.

    Attributes:
        client (Any): Client instance to Connect on AFC
        name (name): VRF's name
        fabric_uuid (str): Fabric UUID
        Inherits from Underlay, Overlay, BGP, OSPF, Network and IPInterface.

    """

    def __init__(self, client: Client, name: str, fabric_uuid: str) -> None:
        """__init__ Init Method.

        Args:
            client (Client): Client instance to Connect on AFC.
            name (name): VRF's name.
            fabric_uuid (str): Fabric UUID.

        Returns:
            Sets properties of the VRF as class attributes. Else, false.

        """
        self.client = client
        self.uuid = None
        self.name = name
        self.fabric_uuid = fabric_uuid
        self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details Check if VRF exists.

        Returns:
            True if found, False if not.

        """
        vrf_request = self.client.get(f"vrfs?fabrics={self.fabric_uuid}")
        for vrf in vrf_request.json()["result"]:
            if vrf["name"] == self.name:
                for item, value in vrf.items():
                    setattr(self, item, value)
                    return True
        return False

    @staticmethod
    def get_vrf_uuid(client: Client, name: str, fabric: str) -> str | bool:
        """get_vrf_uuid Find VRF UUID.

        Args:
            client (Client): Client instance to Connect on AFC.
            name (str): Name of the VRF.
            fabric (str): Name of the fabric.

        Returns:
            VRF UUID if found and False if not found.

        """
        vrf_request = client.get(f"vrfs?fabrics={fabric}")
        for vrf in vrf_request.json()["result"]:
            if vrf["name"] == name:
                return vrf["uuid"]
        return False

    def get_ip_interface(self, switch: str, name: str) -> dict | bool:
        """get_ip_interface Get specific IP interface in a VRF.

        Args:
            name (str): Name of the IP Interface.
            switch (str): Switch IP address.

        Returns:
            IP Interface available in the VRF in JSON format.

        """
        switch_uuid = switches.Switch.get_switch_uuid(self.client, switch)
        ip_intf_uri = f"vrfs?fabrics={self.fabric_uuid}&ip_interfaces=true&\
            include_referenced_objects=true"
        request_ip_intf = self.client.get(ip_intf_uri)
        for intf in request_ip_intf.json()["result"][0]["ip_interfaces"]:
            if intf["name"] == name and intf["switch_uuid"] == switch_uuid:
                return intf
        return False

    def create_vrf(self, **kwargs: dict) -> tuple:
        """create_vrf Create VRF.

        Args:
            name (str): VRF's name.
            description (str, optional) = VRF's description
            fabric (str) = Fabric on which the new VRF must be created.
            vni (int, optional) = L3VNI
            switches (list, optional) = List of switches
            route_target (dict, optional) = Route Targets which must be used.
            route_distinguisher (str, optional) = Route Distinguisher format.
                Defaults to "loopback1:1"
            max_cps_mode (str, optional) = One of:
                - "enabled"
                - "unlimited"
                Defaults to "unlimited"
            max_sessions_mode (str, optional) = One of:
                - "enabled"
                - "unlimited"
                Defaults to "unlimited"
            max_sessions (int, optional) = Maximum number of sessions to be
                concurrently allowed for this vrf per Distributed Services
                Module only applies if mode is enabled.
            max_cps (int, optional) = Maximum number of Connections Per Second
                allowed for this vrf per Distributed Services Module only
                applies if mode is enabled.
            allow_session_reuse (bool, optional) = Allow session reuse.
                Defaults to False
            connection_tracking_mode (bool, optional) = Connection tracking
                mode.
                Defaults to False

        Example:
            new_vrf_data = {
                    "vni": 12000,
                    "route_target": {
                        "primary_route_target": {
                        "as_number": "65000:1",
                        "address_family": "evpn",
                        "evpn": False,
                        "route_mode": "both",
                        },
                        "secondary_route_targets": [
                        {
                            "as_number": "1:1",
                            "address_family": "evpn",
                            "evpn": False,
                            "route_mode": "both",
                        },
                        ],
                    },
                }

            new_vrf = vrf.Vrf(afc_instance.client,
                              name="New_VRF",
                              fabric_uuid=fabric_instance.uuid)
            message, status, changed = new_vrf.create_vrf(**new_vrf_data)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        ## Gathers the Fabric UUID on which the VRF has to be created
        try:
            if kwargs.get("switches"):
                kwargs["switch_uuids"] = utils.consolidate_switches_list(
                    self.client,
                    kwargs["switches"],
                )

            if kwargs.get("name"):
                kwargs.pop("name")

            data = models.VRF(
                name=self.name,
                fabric_uuid=self.fabric_uuid,
                **kwargs,
            )

            vrf_request = self.client.post(
                "vrfs",
                data=json.dumps(data.dict(exclude_none=True)),
            )
            if (
                "should be unique for fabric" in vrf_request.json()["result"]
                or "already exists" in vrf_request.json()["result"]
            ):
                _message = (
                    f"The VRF {self.name} already exists. No action taken"
                )
                _status = True
            elif vrf_request.status_code in utils.response_ok:
                if self.__instantiate_details():
                    _message = f"The VRF {self.name} is successfully created"
                    _status = True
                    _changed = True
            else:
                _message = vrf_request.json()["result"]

        except ValidationError as exc:
            _message = f"An exception occurred. {exc}"

        return _message, _status, _changed

    def delete_vrf(self) -> tuple:
        """delete_vrf Delete VRF.

        Args:
            name (str): Name of the VRF, taken from the class attribute.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            models.VRF(name=self.name, fabric_uuid=self.fabric_uuid)
            vrf_uuid = self.get_vrf_uuid(
                client=self.client,
                name=self.name,
                fabric=self.fabric_uuid,
            )
            if vrf_uuid:
                vrf_delete_request = self.client.delete(f"vrfs/{vrf_uuid}")
                if vrf_delete_request.status_code in utils.response_ok:
                    if not self.__instantiate_details():
                        _message = (
                            f"The VRF {self.name} is successfully deleted"
                        )
                        _status = True
                        _changed = True
                    else:
                        _message = ("A problem has been encountered while "
                                    f"deleting the VRF {self.name}")
                else:
                    _message = ("A problem has been encountered while "
                                f"deleting the VRF {self.name}")
            else:
                _message = (
                    f"The VRF {self.name} does not exist. No action taken"
                )
                _status = True

        except ValidationError as exc:
            _message = f"An exception occurred. {exc}"

        return _message, _status, _changed

    def _update_new_devices_in_vrf(self, **kwargs: dict):
        """_update_new_devices_in_vrf Update devices in the VF.

        Returns:
            True if successful, else false.

        """
        vrf_request = self.client.get(f"vrfs/{self.uuid}/switches")

        for switch in vrf_request.json()["result"]:
            if not switch["route_distinguisher"]:
                kwargs["route_target"] = switch["route_target"]
                kwargs["name"] = switch["name"]
                kwargs["switch_uuid"] = switch["switch_uuid"]
                data = models.VRFReapply(**kwargs)
                vrf_request = self.client.put(
                    f"vrfs/{self.uuid}/switches/{switch['switch_uuid']}",
                    data=json.dumps(data.dict()),
                )
                if vrf_request.status_code not in utils.response_ok:
                    raise exceptions.UpdateFailed(switch["name"])

    def reapply_vrf(self, **kwargs: dict) -> tuple:
        """reapply_vrf Reapply the VRF configuration.

        Returns:
            True if successful, else false.

        """
        _message = ""
        _status = False
        _changed = False

        data = {}
        data["vrf_uuids"] = [self.uuid]

        vrf_request = self.client.post(
            "vrfs/reapply",
            data=json.dumps(data),
        )

        if vrf_request.status_code in utils.response_ok:
            try:
                self._update_new_devices_in_vrf(**kwargs)
                _message = f"The VRF {self.name} is successfully updated"
                _status = True
                _changed = True
            except exceptions.UpdateFailed as exc:
                _message = ("Devices have been added to the VRF, but "
                            f"RD or RT configuration failed on {exc}")
        else:
            _message = ("A problem has been encountered while "
                        "updating the VRF {self.name}")

        return _message, _status, _changed
