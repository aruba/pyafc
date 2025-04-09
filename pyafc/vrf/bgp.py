# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Utility functions and classes BGP management.

This module provides:
- get_bgp_switch_details: get underlay information and current configuration;
- update_bgp_vrf: create an Underlay for the given VRF.
- configure_bgp_on_device: delete the Underlay for the given VRF.
- apply_bgp_on_device: Apply BGP Global Config on a device
- delete_bgp_configuration: Delete BGP Configuration
- add_bgp_neighbor: Add a BGP Neighbor on a device
- delete_bgp_neighbor: Delete a BGP Neighbor on a device
"""

from __future__ import annotations

import json

from pyafc.common import utils
from pyafc.fabric import fabric
from pyafc.switches import switches
from pyafc.vrf import models, vrf


class BGP:
    """BGP CLass representing an BGP.

    It represents an BGP for a given VRF.
    """

    def __init__(self) -> None:
        """__init__ Init Method."""

    def get_bgp_switch_details(self, device: str) -> dict | bool:
        """get_bgp_switch_details Get BGP Information.

        Args:
            device (str): IP Address of the targeted device.

        Returns:
            bgp_switch_request: JSON of the BGP Configuration of the target.

        """
        switch_instance = switches.Switch(self.client, device)
        bgp_switch_request = self.client.get(
            f"vrfs/{self.uuid}/bgp/{switch_instance.uuid}",
        )
        if bgp_switch_request.json()["result"]:
            return bgp_switch_request.json()["result"]
        return False

    def update_bgp_config_vrf(self, **kwargs: dict) -> tuple:
        """update_bgp_config Updates BGP configuration on the given VRF.

        Args:
            switches (list) : List of BGP Config for switches
                              Check example.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        url_bgp = f"vrfs/{self.uuid}/bgp?switches=true"
        bgp_request = self.client.get(url_bgp)
        data = bgp_request.json()["result"]

        switches_data = models.BgpSwitchConfigList(switches=data["switches"])

        changes_needed = any(
            data.get(key) != value for key, value in kwargs.items()
        )

        if changes_needed:
            data = models.BGPUpdate(**kwargs)
            data = switches_data.dict() | data.dict()

            bgp_request = self.client.put(url_bgp, data=json.dumps(data))
            if bgp_request.status_code in utils.response_ok:
                _message = (f"BGP Properties on VRF {self.name} "
                            "successfully updated")
                _status = True
                _changed = True
            else:
                _message = bgp_request.json()["result"]
        else:
            _message = (f"BGP properties on VRF {self.name} are the same. "
                        "No action taken")
            _status = True

        return _message, _status, _changed

    def update_bgp_vrf(self, **kwargs: dict) -> tuple:
        """update_bgp_vrf Updates BGP configuration on the given VRF.

        Args:
            as_number (str) : AS Number
            description (str, optional) = Description
            router_id (str) = Router ID
            redistribute_ospf (bool, optional) = OSPF Redistribution.
                Defaults to False
            redistribute_static (bool, optional) = Static Redistribution.
                Defaults to False
            redistribute_loopback (bool, optional) = Loopback Redistribution.
                Defaults to False
            redistribute_connected (bool, optional) = Connected Redistribution.
                Defaults to False
            keepalive_timer (int, optional) = Keepalive timer.
                Defaults to 60 seconds
            holddown_timer (int, optional) = Keepalive timer.
                Defaults to 180 seconds
            enable (bool, optional) = BGP Enable
            bestpath (bool, optional) = BGP  Best Path
            fast_external_fallover (bool, optional) = Fast External
                Failover Enable
            trap_enable (bool, optional) = Trap Enable
            log_neighbor_changes (bool, optional) = Neighbor Logging Enable
            deterministic_med (bool, optional) = Deterministic MED Enable
            always_compare_med (bool, optional) = Always Compare MED Enable
            maximum_paths (int, optional) = BGP Max Paths. Default to 8
            networks (list, optional) = List of BGP Networks to announce
            neighbors (list, optional) = List of BGP Neighbors

        Example:
            update_bgp_data = {
                "as_number": 65000,
                "redistribute_ospf": True,
            }

            vrf_instance.update_bgp_vrf(**update_bgp_data)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        bgp_request = self.client.get(
            f"vrfs/{self.uuid}?fabrics={self.fabric_uuid}&include_bgp=true",
        )

        if not bgp_request.json()["result"]["bgp"]["switches"]:
            url_bgp = f"vrfs/{self.uuid}/bgp"
            bgp_request = self.client.get(url_bgp)
            data = bgp_request.json()["result"]
            change_needed = False

            for _key, _value in kwargs.items():
                if _key in [
                    "as_number",
                    "maximum_paths",
                    "keepalive_timer",
                    "holddown_timer",
                ]:
                    if int(data[_key]) != int(_value):
                        change_needed = True
                elif data.get(_key) and (data[_key] != _value):
                    change_needed = True

            if change_needed:
                data = models.BGPUpdate(**kwargs)
                bgp_request = self.client.put(
                    url_bgp,
                    data=json.dumps(data.dict()),
                )

                if bgp_request.status_code in utils.response_ok:
                    _message = f"Devices successfully added to VRF {self.name}"
                    _status = True
                    _changed = True
                else:
                    _message = bgp_request.json()["result"]

            else:
                msg = (f"BGP properties on VRF {self.name} are the same. "
                       "No Action Taken")
                _message = msg
                _status = True

        else:

            _message, _status, _changed = self.apply_bgp_on_device(**kwargs)

        return _message, _status, _changed

    def configure_bgp_on_device(self, **kwargs: dict) -> tuple:
        """configure_bgp_on_device Configures BGP configuration on the devices.

        Args:
            kwargs (dict): Values consumed by AFC to configure BGP \
                configuration with targets.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        if kwargs.get("same_config_than"):
            data = self.get_bgp_switch_details(kwargs["same_config_than"])
            data = models.BGPConfig(**data)
            data = data.dict()
            data["router_id"] = (
                kwargs["router_id"] if kwargs.get("router_id") else None
            )
        else:
            data = models.BGPConfig(**kwargs)
            data = data.dict()
        try:
            switch_instance = switches.Switch(self.client, kwargs["switch"])
            data["name"] = switch_instance.name
            data["switch_uuid"] = switch_instance.uuid
            bgp_request = self.client.put(
                f"vrfs/{self.uuid}/bgp/{switch_instance.uuid}",
                data=json.dumps(data),
            )
            if bgp_request.status_code in utils.response_ok:
                _message = "Successfully applied BGP properties"
                _status = True
                _changed = True
            else:
                _message = bgp_request.json()["result"]

        except Exception as exc:
            _message = f"An exception {exc} occurred - No action taken"

        return _message, _status, _changed

    def apply_bgp_on_device(self, **kwargs: dict) -> tuple:
        """apply_bgp_on_device Applies BGP configuration on the devices.

        Args:
            kwargs (dict): Values consumed by AFC to apply BGP configuration \
                with targets.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        if kwargs.get("same_config_than"):
            data = self.get_bgp_switch_details(kwargs["same_config_than"])
            data = models.BGPUpdateSwitch(**data)
        else:
            data = models.BGPUpdateSwitch(**kwargs)

        data = data.dict()

        if data["as_number"] == "0":
            _message = "AS Number not provided - No action taken"
            return _message, _status, _changed

        if kwargs.get("switches"):
            switches_uuid_list = utils.consolidate_switches_list(
                self.client, kwargs["switches"]
            )
        else:
            vrf_switch_request = self.client.get(f"vrfs/{self.uuid}/switches")

            switches_uuid_list = []
            for switch in vrf_switch_request.json()["result"]:
                switches_uuid_list.append(switch["switch_uuid"])

        switch_uuids = []
        for switch in switches_uuid_list:
            bgp_switch_request = self.client.get(
                f"vrfs/{self.uuid}/bgp/{switch}",
            )

            if not bgp_switch_request.json()["result"]:
                switch_uuids.append(switch)

        if not switch_uuids:
            _message = f"No new devices to enable in VRF {self.name}"
            _status = True

        for switch in switch_uuids:
            data["switch_uuid"] = switch

            if not kwargs.get("router_id"):
                fabric_uuid = fabric.Fabric.get_fabric_uuid(
                    self.client, kwargs["fabric"]
                )
                vrf_default_uuid = vrf.Vrf.get_vrf_uuid(
                    self.client,
                    "default",
                    fabric_uuid,
                )
                loopback_request = self.client.get(
                    f"vrfs/{vrf_default_uuid}/ip_interfaces?if_type=loopback"
                )
                if loopback_request.json()["result"]:
                    for loopback in loopback_request.json()["result"]:
                        if (
                            loopback["switch_uuid"] == switch
                            and loopback["name"] == "loopback0"
                        ):
                            data["router_id"] = loopback[
                                "ipv4_primary_address"
                            ]["address"]

            if not data["router_id"]:
                _message = "No Router ID can be found - No action taken"
            else:
                bgp_request = self.client.put(
                    f"vrfs/{self.uuid}/bgp/{switch}",
                    data=json.dumps(data),
                )
                if bgp_request.status_code in utils.response_ok:
                    _message = "Successfully applied BGP properties"
                    _status = True
                    _changed = True
                else:
                    _message = bgp_request.json()["result"]

        return _message, _status, _changed

    def delete_bgp_configuration(self, switch: str) -> tuple:
        """delete_bgp_configuration Deletes BGP configuration from the switch.

        Args:
            switch (str): Switch IP address.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        bgp_data = self.get_bgp_switch_details(switch)
        switch_uuid = switches.Switch.get_switch_uuid(self.client, switch)
        if bgp_data:
            bgp_request = self.client.delete(
                f"vrfs/{self.uuid}/bgp/{switch_uuid}",
            )
            if bgp_request.status_code in utils.response_ok:
                _message = "Successfully removed BGP configuration"
                _status = True
                _changed = True
            else:
                _message = bgp_request.json()["result"]
                _status = True
                _changed = True
        else:
            _message = "BGP not configured - No action taken"
            _status = True
            _changed = True

        return _message, _status, _changed

    def add_bgp_neighbor(self, name: str, **kwargs: dict) -> tuple:
        """add_bgp_neighbor Add BGP neighbor.

        Args:
            name (str) = Neighbor's name
            description (str, optional) = Neighbor's description
            neighbor_as_number (str) = Neighbor's AS Number
            neighbor_ip_address (str) = Neighbor's IP Address
            route_reflector_client (bool, optional) = Route Reflector Client.
                Defaults to False
            soft_reconfiguration_inboundt (bool, optional) = Inbound Soft
                Reconfiguration.
                Defaults to False
            weight (int, optional) = BGP Weight.
                Defaults to 0
            auth_password (str, optional) = BGP Auth Password
            keepalive_timer (int, optional) = KeepAlive Timer.
                Defaults to 60
            holddown_timer (int, optional) = Hold Down Timer.
                Defaults to 180
            neighbor_type (str) = One of:
                - "ibgp"
                - "ebgp"
            address_families (list): List of "evpn", "ipv4", "ipv6", "vpnv4".
                Defaults to ["ipv4"]
            external_bgp_multihop (int, optional) = eBGP Multihops
            update_source_address (str, optional) = Update Source address
            update_source_interface (str, optional) = Update Source interface
            default_originate (int, optional) = Default Originate
            admin_state_enable (bool, optional) = BGP Admin State.
                Defaults to True
            fall_over (bool, optional) = BGP Fall Over.
                Defaults to True
            local_as (str, optional) = Local AS Number
            remove_private_as (bool, optional) = BGP Remote Private AS.
                Defaults to False
            bfd_enable (bool, optional) = BFD Enabled.
                Defaults to False
            allowas_in (int, optional) = Allow AS.
                Default to 1
            route_map_in (str, optional) = EVPN Inbound Route Map
            route_map_out (str, optional) = EVPN Outbound Route Map
            route_map_in_ip (str, optional) = IPv4 Inbound Route Map
            route_map_out_ip (str, optional) = IPv4 Outbound Route Map
            send_community_ip (str, optional) = One of:
                - "standard"
                - "extended"
                - "both"
            send_community_evpn (str, optional) = One of:
                - "standard"
                - "extended"
                - "both"

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        bgp_data = self.get_bgp_switch_details(kwargs["switch"])
        switch_uuid = switches.Switch.get_switch_uuid(
            self.client,
            kwargs["switch"],
        )
        if bgp_data:
            data = models.BgpNeighbor(name=name, **kwargs)
            bgp_data["neighbors"].append(data.dict(exclude_none=True))
            bgp_request = self.client.put(
                f"vrfs/{self.uuid}/bgp/{switch_uuid}",
                data=json.dumps(bgp_data),
            )
            if bgp_request.status_code in utils.response_ok:
                _message = "Successfully Configured BGP neighbor"
                _status = True
                _changed = True
            else:
                _message = bgp_request.json()["result"]
                _status = True
                _changed = True
        else:
            _message = "BGP not configured - No action taken"
            _status = True
            _changed = True

        return _message, _status, _changed

    def delete_bgp_neighbor(
        self,
        switch: str,
        neighbor_ip_address: str,
    ) -> tuple:
        """add_bgp_neighbor Add BGP neighbor.

        Args:
            switch (str): Switch IP address.
            neighbor_ip_address (str): Neighbor IP address.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        bgp_data = self.get_bgp_switch_details(switch)
        switch_uuid = switches.Switch.get_switch_uuid(self.client, switch)
        if bgp_data:
            if bgp_data["neighbors"]:
                for neighbor in bgp_data["neighbors"]:
                    if neighbor["neighbor_ip_address"] == neighbor_ip_address:
                        bgp_data["neighbors"].remove(neighbor)

                bgp_request = self.client.put(
                    f"vrfs/{self.uuid}/bgp/{switch_uuid}",
                    data=json.dumps(bgp_data),
                )
                if bgp_request.status_code in utils.response_ok:
                    _message = "Successfully removed BGP neighbor"
                    _status = True
                    _changed = True
                else:
                    _message = bgp_request.json()["result"]
                    _status = True
                    _changed = True
            else:
                _message = "No BGP Neighbors configured - No action taken"
                _status = True
                _changed = True
        else:
            _message = "BGP not configured - No action taken"
            _status = True
            _changed = True

        return _message, _status, _changed
