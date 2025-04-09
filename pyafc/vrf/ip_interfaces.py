# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Utility functions and classes Underlay management.

This module provides:
- get_underlay: get underlay information and current configuration;
- create_underlay: create an Underlay for the given VRF.
- delete_underlay: delete the Underlay for the given VRF.
"""

from __future__ import annotations

import ipaddress
import json

from pydantic import ValidationError

from pyafc.common import exceptions, utils
from pyafc.ports import physical
from pyafc.switches import switches
from pyafc.vrf import models


class IPInterface:
    """Underlay CLass representing an Underlay.

    It represents an Underlay for a given VRF.
    """

    def __init__(self) -> None:
        """__init__ Init Method."""

    def get_ip_interface(self, switch: str, name: str) -> dict | bool:
        """get_ip_interface Find IP Interface Config.

        Args:
            name (str): Name of the IP Interface Config.
            switch (str): Switch IP address.

        Returns:
            IP Interface config data in JSON format and False if not found.

        """
        switch_uuid = switches.Switch.get_switch_uuid(self.client, switch)

        lag_request = self.client.get("lags?type=internal")
        for lag in lag_request.json()["result"]:
            if (
                lag["name"] == f"LAG#{name}"
                and lag["port_properties"][0]["switch_uuid"] == switch_uuid
            ):
                lag_values = lag

        ip_intf_request = self.client.get(f"vrfs/{self.uuid}/ip_interfaces")
        for intf in ip_intf_request.json()["result"]:
            if intf["lag_uuid"] == lag_values["uuid"]:
                return intf

        return False

    def __select_switches(self, switches_list: list) -> list:
        """__select_switches Update the switch UUIDs from the IP addresses.

        Args:
            switches_list (list): List of switch IP addresses.

        Returns:
            List of switch UUIDs from the list of switch IP addresses.

        """
        switches_uuid = []
        switches_fabric = switches.Switch.get_switches_fabric(
            self.client,
            self.fabric_uuid,
        )

        for target in switches_list:
            if target in ["leaf", "sub_leaf", "border_leaf"]:
                switches_uuid.extend(
                    switch["uuid"]
                    for switch in switches_fabric
                    if switch["role"] == target
                )
            elif target == "all":
                switches_uuid.extend(
                    switch["uuid"]
                    for switch in switches_fabric
                    if switch["role"] in ["leaf", "sub_leaf", "border_leaf"]
                )
            else:
                switch_instance = switches.Switch(self.client, target)
                switches_uuid.extend(
                    switch["uuid"]
                    for switch in switches_fabric
                    if switch["ip_address"] == str(switch_instance.ipaddress)
                )

        return switches_uuid

    def __select_primary_ipv4(self, ipv4_range: str) -> list:
        """__select_primary_ipv4 Select the IP interface IP from the range.

        Args:
            ipv4_range (str): IP Address range.

        Returns:
            Returns the list of IP addresses picked from the range.

        """
        first_ip = ipaddress.IPv4Address(ipv4_range.split("-")[0])
        last_ip = ipaddress.IPv4Address(ipv4_range.split("-")[1])
        ipv4_set = []

        while first_ip <= last_ip:
            ipv4_set.append(str(first_ip))
            first_ip += 1
        return ipv4_set

    def __generate_rpi_values(self, values: dict) -> dict:
        """__generate_rpi_values Generate RPI values.

        Args:
            values (dict): RPI Values data.

        Returns:
            Returns RPI Values in expected format.

        """
        port_instance = physical.Physical(
            name=values["interface"],
            switches=values["switches"][0],
            client=self.client,
        )
        lag_request = self.client.get("lags?type=internal")
        for lag in lag_request.json()["result"]:
            if (
                lag["name"] == f"LAG#{values['interface']}"
                and lag["port_properties"][0]["port_uuids"][0]
                == port_instance.uuid
            ):
                values["lag_uuid"] = lag["uuid"]
                values["fabric_uuid"] = lag["fabric_uuid"]
                values["switch_uuid"] = lag["port_properties"][0][
                    "switch_uuid"
                ]
        return values

    def create_ip_interface(self, **kwargs: dict) -> tuple:
        """create_ip_interface Create IP Interface configuration.

        Args:
            name (str): IP interface name.
            enable (bool): Interface enabled.
            if_type (str) = One of:
                - "vlan"
                - "routed"
                - "loopback"
                - "evpn"
            description (str, optional): IP interface description.
            vlan (int, optional): VLAN ID.
            loopback_name (str, optional): Loopback name.
            vsx_shutdown_on_split (bool, optional): VSX Shutdown on Split
                enabled.
                Defaults to False.
            vsx_active_forwarding (bool, optional): VSX Active Forwarding
                enabled.
                Defaults to False.
            active_gateway (dict, optional): : ActiveGateway
            ipv4_primary_address (dict): IPv4 interface or range. Check example
            ipv4_secondary_addresses (list, optional): List of IPv4 secondary
                interfaces.
            local_proxy_arp_enabled (bool, optional): Local Proxy ARP enabled.
                Defaults to False.
            switches (list) = List of switches

        Example:
            ip_intf_data = {
                "if_type": "vlan",
                "vlan": 100,
                "active_gateway": {
                    "ipv4_address": "10.147.100.254",
                    "mac_address": "00:00:00:00:00:01",
                },
                "ipv4_primary_address": {
                    "address": "10.147.100.254",
                    "prefix_length": 24,
                },
                "local_proxy_arp_enabled": True,
                "switches": ["10.149.2.104-10.149.2.107"],
            }

            vrf_instance.create_ip_interface(name="VLAN 100",
                                             **ip_intf_data)

            ip_intf_data = {
                "if_type": "routed",
                "ipv4_primary_address": {
                    "address": "10.143.253.117",
                    "prefix_length": 31,
                    },
                "switches": ["10.149.2.100"],
                "interface": "1/1/2",
            }

            vrf_instance.create_ip_interface(name="DC1 to DC2 - Link 1",
                                             **ip_intf_data)

            ip_intf_data = {
                "if_type": "loopback",
                "loopback_name": "loopback2",
                "ipv4_primary_address": {
                    "address": "1.2.3.4",
                    "prefix_length": 32,
                    },
                "switches": ["10.149.2.100"],
            }

            vrf_instance.create_ip_interface(name="Loopback2",
                                             **ip_intf_data)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _changed = False
        _status = False
        _switches = kwargs["switches"]
        _switches_str = " ".join(_switches)

        try:

            ip_interfaces_array: list = []
            kwargs = utils.populate_list_fabrics_switches(self.client, kwargs)

            if not kwargs["switch_uuids"]:
                raise exceptions.NoDeviceFound()

            if len(kwargs["ipv4_primary_address"]["address"].split("-")) > 1:
                ipv4_range = self.__select_primary_ipv4(
                    kwargs["ipv4_primary_address"]["address"],
                )
            else:
                ipv4_range = kwargs["ipv4_primary_address"]["address"]

            uri_ip_interfaces = f"vrfs/{self.uuid}/ip_interfaces"
            existing_ip_interfaces = self.client.get(
                uri_ip_interfaces,
            ).json()["result"]
            used_ips: list = []

            if len(existing_ip_interfaces) > 0:
                used_ips.extend(
                    ip_interface["ipv4_primary_address"]["address"]
                    for ip_interface in existing_ip_interfaces
                )

            if isinstance(ipv4_range, list):
                for ip in ipv4_range:
                    if ip in used_ips:
                        ipv4_range.remove(ip)

            if isinstance(ipv4_range, list) and len(ipv4_range) < len(
                kwargs["switch_uuids"],
            ):
                _message = ("Not enough IP addresses to create "
                            f"IP Interfaces on {_switches_str}")

            else:
                try:
                    for switch in kwargs["switch_uuids"]:
                        if isinstance(ipv4_range, str):
                            kwargs["ipv4_primary_address"][
                                "address"
                            ] = ipv4_range
                        else:
                            kwargs["ipv4_primary_address"]["address"] = (
                                ipv4_range[0]
                            )
                            ipv4_range.pop(0)

                        if kwargs["if_type"] == "routed":
                            kwargs = self.__generate_rpi_values(kwargs)

                        kwargs["switch_uuid"] = switch
                        data = models.IPInterface(**kwargs)
                        ip_interfaces_array.append(
                            data.dict(exclude_none=True)
                        )
                except IndexError:
                    _message = "Not enough interfaces for IPv4 Primary"

                ip_interfaces_request = self.client.post(
                    uri_ip_interfaces,
                    data=json.dumps(ip_interfaces_array),
                )

                if ip_interfaces_request.status_code in utils.response_ok:
                    _message = ("Successfully created IP Interface "
                                f"{kwargs['name']} on {_switches_str}")
                    _changed = True
                    _status = True
                else:
                    if (
                        "already exists"
                        in ip_interfaces_request.json()["result"]
                        or "duplicate"
                        in ip_interfaces_request.json()["result"]
                    ):
                        _status = True
                    _message = ip_interfaces_request.json()["result"]

        except ValidationError as exc:
            _message = f"An exception occurred {exc}"

        except exceptions.NoDeviceFound:
            _message = "No device found"

        return _message, _status, _changed

    def delete_ip_interface(self, name: str, **kwargs: dict) -> tuple:
        """delete_ip_interface Delete IP Interface configuration.

        Args:
            name (str): IP interface name.
            vlan (int, optional): VLAN ID.
            switches (list) = List of switches

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _changed = False
        _status = False
        _int_vlan = ""

        if "vlan" in kwargs:
            _int_vlan = kwargs["vlan"]
        _switches = kwargs["switches"]

        try:
            switches_uuid = self.__select_switches(_switches)
            uri_ip_interfaces = f"vrfs/{self.uuid}/ip_interfaces"
            existing_ip_interfaces = self.client.get(
                uri_ip_interfaces,
            ).json()["result"]

            selected_interfaces = []

            if len(existing_ip_interfaces) > 0:
                selected_interfaces.extend(
                    {
                        "int_uuid": ip_interface["uuid"],
                        "switch_uuid": ip_interface["switch_uuid"],
                        "ip_address": ip_interface["ipv4_primary_address"][
                            "address"
                        ],
                    }
                    for ip_interface in existing_ip_interfaces
                    if (
                        ip_interface["name"] == name
                        or (
                            "vlan" in ip_interface
                            and ip_interface["vlan"] == _int_vlan
                        )
                    )
                )

            if len(selected_interfaces) == 0:
                _message = ("No IP interfaces are present "
                            f"in the VRF {self.name}")
            else:
                _message = []
                for item in selected_interfaces:
                    if item["switch_uuid"] in switches_uuid:
                        ip_interfaces_request = self.client.delete(
                            f'{uri_ip_interfaces}/{item["int_uuid"]}'
                        )

                        if (
                            ip_interfaces_request.status_code
                            in utils.response_ok
                        ):
                            _message.append(
                                (f"Successfully deleted interface with IP "
                                 f"{item['ip_address']} from VRF {self.name}"),
                            )
                            _changed = True
                            _status = True
                        else:
                            _message.append(
                                ip_interfaces_request.json()["result"]
                            )

        except ValidationError as exc:
            _message = f"An exception occurred {exc}"

        return _message, _status, _changed
