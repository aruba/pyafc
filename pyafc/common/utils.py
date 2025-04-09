# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Utility functions for module utilities.

This module provides:
- remove_null_from_dict: Get VRF UUID;
- extract_data: Get IP Interfaces for the specified VRF
- dtext: Get IP Interface for the specified VRF
- get_switches_uuid_from_list: create a VRF.
- get_switches_list_from_scope: delete a VRF.
"""

from __future__ import annotations

import ipaddress
from pathlib import Path
from typing import TYPE_CHECKING

import netaddr
import yaml

from pyafc.common import exceptions
from pyafc.fabric import fabric
from pyafc.switches import switches

if TYPE_CHECKING:
    from httpx import Client

response_ok = [200, 202, 207]
response_nok = [401, 404, 500]


def remove_null_from_dict(original_dict: dict) -> dict:
    """Remove Null entries from a dictionnary.

    Args:
        original_dict (dict): Original dictionary.

    Returns:
        updated_dict (dict): Updated dictionary.

    """
    if type(original_dict) is dict:
        return {
            k: remove_null_from_dict(v)
            for k, v in original_dict.items()
            if v and remove_null_from_dict(v)
        }
    return original_dict


def extract_data(file: str) -> dict | bool:
    """extract_data Extracts data from the input yaml file.

    Args:
        file (object): yml or yaml source file.

    Returns:
        data (dict): Retrieved data from the yml or yaml file.
        If found, the information are set as Class attributes
        This section is mostly used for direct SDK based execution

    """
    if not file.endswith(".yml") or not file.endswith(".yaml"):
        return False

    with Path.open(file) as stream:
        data = yaml.safe_load(stream)
        stream.close()
    return data


def get_switches_uuid_from_list(client: Client, switches_list: list) -> list:
    """get_switches_uuid_from_list is used to retrieve the UUIDs of Switches.

    Args:
        client (Any): Client instance to Connect and Authenticate on AFC
        switches_list (str): List of switches IP Addresses.

    Returns:
        switches_uuids (list): List of switches UUIDs to be returned

    """
    switches_uuids: list = []
    for switch in switches_list:
        dut = switches.Switch.get_switch_uuid(client, switch)
        switches_uuids.append(dut.uuid)
    return switches_uuids


def extend_switches_ranges(devices_list: list) -> list:
    """extend_switches_ranges is used to get the list of switch IPs.

    Args:
        devices_list (str): addresses with scope as input.

    Returns:
        devices (list): List of IPs to be returned

    """
    devices: list = []

    for scope in devices_list:
        tmp_list = get_switches_list_from_scope(scope)
        if isinstance(tmp_list, list):
            for device in tmp_list:
                devices.append(device)  # noqa: PERF402
        else:
            devices.append(tmp_list)

    return devices


def get_switches_list_from_scope(scope: str) -> list | bool:
    """get_switches_list_from_scope is used to return the list of switch IPs.

    Args:
        scope (str): addresses with scope as input.

    Returns:
        switches_list (list): List of switches to be returned

    """
    switches_list: list = []

    for subscope in scope.split(","):
        if len(subscope.split("-")) > 1:
            subscope_ips = subscope.split("-")
            try:
                ipaddress.IPv4Network(subscope)
                switches_list.extend(
                    str(ip) for ip in netaddr.IPNetwork(subscope).iter_hosts()
                )
            except ipaddress.AddressValueError:
                if len(subscope_ips) == 1:
                    switches_list.append(subscope)
                else:
                    ip_list = list(
                        netaddr.iter_iprange(subscope_ips[0], subscope_ips[1])
                    )
                    switches_list.extend(str(ip) for ip in ip_list)
            return switches_list
        else:
            return scope

    return False


def _get_uuids_from_devices_role(client, role: list, fab: str | None) -> list:

    if fab:

        fabric_uuid = fabric.Fabric.get_fabric_uuid(client, fab)
        switches_list = switches.Switch.get_switches_fabric(
            client, fabric_uuid,
        )
    else:
        switches_request = client.get("/switches")
        switches_list = switches_request.json()["result"]
    if switches_list:
        _devices_list = [
            switch["uuid"]
            for switch in switches_list
            if switch["role"] == role
        ]
    else:
        msg = "No devices found"
        raise exceptions.NoDeviceFound(msg)

    return _devices_list


def populate_list_fabrics_switches(client: Client, values: dict) -> dict:
    """populate_list_fabrics_switches to populate switch or fabric UUIDs.

    Args:
        client (Any): Client instance to Connect and Authenticate on AFC
        values (dict): List of Switches or Fabrics.

    Returns:
        values (dict): List of switches or Fabrics UUIDs to be returned

    """
    try:
        if values.get("fabrics"):
            values["fabric_uuids"] = []

            if isinstance(values["fabrics"], str):
                values["fabrics"] = [values["fabrics"]]

            for fab in values["fabrics"]:
                fab_uuid = fabric.Fabric.get_fabric_uuid(client, fab)

                if fab_uuid:
                    values["fabric_uuids"].append(fab_uuid)

        elif values.get("switches"):
            values["switch_uuids"] = []

            if isinstance(values["switches"], str):
                values["switches"] = [values["switches"]]

            for switches_entry in values["switches"]:
                if switches_entry == "all":
                    switches_request = client.get("/switches")
                    values["switch_uuids"].extend(
                        [
                            switch["uuid"]
                            for switch in switches_request.json()["result"]
                        ],
                    )
                elif switches_entry in [
                    "spine",
                    "leaf",
                    "sub_leaf",
                    "border_leaf",
                ]:
                    if values.get("roles_fabrics"):
                        if isinstance(values["roles_fabrics"], str):
                            values["roles_fabrics"] = [values["roles_fabrics"]]
                    else:
                        values["roles_fabrics"] = []
                    for fab in values["roles_fabrics"]:
                        values["switch_uuids"].extend(
                            _get_uuids_from_devices_role(
                                client, switches_entry, fab,
                            ),
                        )
                else:
                    values["switch_uuids"].extend(
                        consolidate_switches_list(client, switches_entry),
                    )

        else:
            msg = "No devices found"
            raise exceptions.NoDeviceFound(msg)

    except exceptions.NoDeviceFound as exc:
        raise exceptions.NoDeviceFound(exc)

    return values


def populate_list_switches(
    client: Client,
    values: dict,
    switches_request: dict,
) -> list:
    """populate_list_switches is used to populate switch uuids.

    Args:
        client (Any): Client instance to Connect and Authenticate on AFC
        values (dict): List of Switches or Fabrics.
        switches_request (dict): Switches list from API Request passed as arg

    Returns:
        switches_list (dict): List of switches UUIDs to be returned

    """
    switches_list: list = []

    for scope, scope_values in values.items():
        if scope == "fabric":
            for fabric_name in scope_values:
                fabric_instance = fabric.Fabric(client, fabric_name)
                if not fabric_instance.uuid:
                    raise exceptions.FabricNotFound
                switches_list.extend(
                    switch["uuid"]
                    for switch in switches_request
                    if switch["fabric_uuid"] == fabric_instance.uuid
                )
        elif scope == "switches":
            if scope_values == "all":
                switches_list.extend(
                    switch["uuid"] for switch in switches_request
                )
            elif scope_values in ["spine", "leaf", "sub_leaf", "border_leaf"]:
                pass
            else:
                try:
                    switches_list.extend(
                        consolidate_switches_list(client, values["switches"]),
                    )
                except exceptions.NoDeviceFound:
                    msg = "No devices found"
                    raise exceptions.NoDeviceFound(msg)
        else:
            raise exceptions.NotGoodVar

    return switches_list


def _get_uuid(client, switch: str) -> list:

    switch_ip = switches.Switch.consolidate_ip(client, switch)
    if not switch_ip:
        raise exceptions.NoDeviceFound(switch)
    switch_uuid = switches.Switch.get_switch_uuid(client, switch_ip)
    if not switch_uuid:
        raise exceptions.NoDeviceFound(switch)
    return switch_uuid


def consolidate_switches_list(client, devices_list: list) -> list:
    switches_uuids = []

    if not isinstance(devices_list, list):
        devices_list = [devices_list]

    for switch in devices_list:

        if len(switch.split("-")) > 1:
            try:
                netaddr.IPAddress(switch.split("-")[0])
                netaddr.IPAddress(switch.split("-")[1])
                sw_list = get_switches_list_from_scope(switch)
                for sw in sw_list:
                    sw_uuid = _get_uuid(client, sw)
                    switches_uuids.append(sw_uuid)
            except:
                sw_uuid = _get_uuid(client, switch)
                switches_uuids.append(sw_uuid)
        else:
            sw_uuid = _get_uuid(client, switch)
            switches_uuids.append(sw_uuid)

    return switches_uuids
