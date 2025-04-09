# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Utility functions and classes for Switch management.

This module provides:
- get_switch_details: Get Switch detail;
- get_switch_uuid: Get Switch UUID;
- get_switches_fabric: Get Switch Fabric;
- reboot: Reboot the Switch
- reconcile: Reconcile the Switch;
- save_config: Save switch config ("write memory")
- delete: Delete Switch from AFC;
- discover_device: Discover device;
- discover_multiple_devices: Discover multiple Devices at once;
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
import time
from ipaddress import IPv4Address
from typing import TYPE_CHECKING

from pydantic import ValidationError

from pyafc.common import exceptions, utils
from pyafc.fabric import fabric
from pyafc.switches import models

if TYPE_CHECKING:
    from httpx import Client

sys.tracebacklimit = 0


class Switch:
    """Switch Class representing a Switch.

    Attributes:
        client (Any): Client instance to Connect and Authenticate on AFC.
        ipaddress (str): Device's IP Address.
        kwargs (dict): Additional values.

    """

    def __init__(
        self,
        client: Client,
        device: str | None = None,
        **kwargs: dict,
    ) -> None:
        """__init__ Init Method.

        Args:
            client (Client): Client instance to Connect and Authenticate.
            device (str): Device's Identification - Can be IP Address or name.
            kwargs: Switch's additional values.

        """
        self.client = client
        self.ipaddress = None
        self.name = None
        if device:
            self.__name_or_ip(device)
            if not self.__instantiate_attributes() and kwargs:
                self.discover_device(**kwargs)

    def __instantiate_attributes(self) -> bool:
        """__instantiate_details Find Switch UUID.

        Returns:
            True if found and UUID is set as the class attribute, else False.

        """
        self.__get_switch_ip_by_name()
        switch_request = self.client.get(
            f"switches?ip_address={self.ipaddress}",
        )
        if (
            switch_request.json()["result"]
            and switch_request.status_code != utils.response_nok
        ):
            for item, value in switch_request.json()["result"][0].items():
                setattr(self, item, value)
            return True
        return False

    def __name_or_ip(self, device: str):
        """__name_or_ip Find device format.

        Args:
            device (str): Device identification.

        """
        try:
            self.ipaddress = IPv4Address(device)
        except:  # noqa: E722
            self.name = device

    def get_switch_details(self) -> dict:
        """get_switch_details Find Switch details.

        Args:
            client (Any): AFC Connection object.
            ipaddress (str): IP address of the switch.

        Returns:
            Switch config data in JSON format.

        """
        self.__get_switch_ip_by_name()
        switch_request = self.client.get(
            f"switches?ip_address={self.ipaddress}",
        )
        return switch_request.json()["result"][0]

    def __get_switch_ip_by_name(self) -> None:
        if self.name:
            switch_request = self.client.get("switches")
            for switch in switch_request.json()["result"]:
                if switch["name"] == self.name:
                    self.ipaddress = switch["ip_address"]

    @staticmethod
    def get_switch_uuid(client: Client, switch: str) -> dict | bool:
        """get_switch_uuid Find Switch UUID.

        Args:
            client (Client): Client instance to Connect and Authenticate.
            switch (str): Switch's IP Address.

        Returns:
            Switch details if found, else False.

        """
        try:
            ipaddress = IPv4Address(switch)
        except ipaddress.AddressValueError:
            error_msg = "IP Addresses are missing"
            raise exceptions.NotIPv4Address(
                error_msg,
            ) from None

        switch_request = client.get(f"switches?ip_address={switch}")
        if switch_request.json()["result"]:
            return switch_request.json()["result"][0]["uuid"]
        return False

    @staticmethod
    def consolidate_ip(client: Client, device: str) -> str | bool:
        """consolidate_ip Find Switch IP based on IP or Name.

        Args:
            client (Client): Client instance to Connect and Authenticate.
            device (str): Switch's Identification.

        Returns:
            Switch IP if found, else False.

        """
        switch_ip = None
        try:
            switch_ip = IPv4Address(device)
        except:
            switch_request = client.get("switches")
            for switch in switch_request.json()["result"]:
                if switch["name"] == device:
                    switch_ip = switch["ip_address"]

        return str(switch_ip)

    @staticmethod
    def get_switches_fabric(client: Client, fabric_uuid: str) -> dict | bool:
        """get_switches_fabric Find if switch belongs to the fabric specified.

        Args:
            client (Client): Client instance to Connect and Authenticate.
            fabric_uuid (str): Fabric's UUID.

        Returns:
            True if the switch is part of Fabric, else False.

        """
        switch_request = client.get(
            f"switches?fabrics={fabric_uuid}",
        )
        if switch_request.json()["result"]:
            return switch_request.json()["result"]
        return False

    @staticmethod
    def reboot(client: Client, data: dict) -> tuple:
        """Reboot Reboot switches.

        Args:
            client (Client): Client instance to Connect and Authenticate.
            data (dict): Reboot data including boot partition.

        Example:
            reboot_data = {
                "fabric": ["DC1"],
                "boot_partition": "non-active"
                }

            switches.Switch.reboot(afc_instance.client, reboot_data)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _status = False
        _message = ""
        _changed = False

        def _define_partition(
            switch: str, switch_payload: dict, target: str
        ) -> dict:
            if target == "active":
                switch_payload["boot_partition"] = switch["booted_partition"]
            elif target == "non-active":
                switch_payload["boot_partition"] = (
                    "primary"
                    if switch["booted_partition"] == "secondary"
                    else "secondary"
                )
            else:
                switch_payload["boot_partition"] = target
            return switch_payload

        switches_request = client.get("switches?software=true")
        switches_list: list = []

        if data.get("boot_partition"):
            data_tmp = data.copy()
            data_tmp.pop("boot_partition")
            switches_scope = data_tmp

        switches_scope_list: list = []
        try:
            switches_scope_uuid = utils.populate_list_switches(
                client,
                switches_scope,
                switches_request.json()["result"],
            )

            switches_scope_list.extend(
                {
                    "uuid": switch,
                }
                for switch in switches_scope_uuid
            )

            reboot_partition = (
                "active"
                if not switches_scope.get("boot_partition")
                else switches_scope["boot_partition"]
            )
            for switch in switches_scope_list:
                for switch_from_afc in switches_request.json()["result"]:
                    if switch["uuid"] == switch_from_afc["uuid"]:
                        _define_partition(
                            switch_from_afc, switch, reboot_partition
                        )

            switches_list = switches_list + switches_scope_list

        except exceptions.NotGoodVar:
            switches_list = []
            _message = ("Fabric and Switches variables are not provided. "
                        "No action taken")
        except exceptions.FabricNotFound:
            switches_list = []
            _message = "Fabric not found - No action taken"
        except exceptions.NoDeviceFound:
            switches_list = []
            _message = "Devices not found - No action taken"

        if switches_list:
            data = models.RebootSwitches(switches=switches_list)
            uri_reboot = "/switches/reboot"
            reboot_request = client.put(
                uri_reboot,
                data=json.dumps(data.dict()),
            )
            if reboot_request.status_code in utils.response_ok:
                _message = "Successfully rebooted devices"
                _status = True
                _changed = True
            else:
                _message = reboot_request.json()["result"]

        return _message, _status, _changed

    @staticmethod
    def reconcile(client: Client, data: dict) -> tuple:
        """Reconcile Reconcile switch configuration.

        Args:
            client (Client): Client instance to Connect and Authenticate.
            switches (list, optional): List of switches to reconcile.
            fabric (list, optional): List of Fabrics to reconcile.

        Example:
            reconcile_data = {
                "switches": ["10.149.2.100-10.149.2.109"]
                }

            switches.Switch.reconcile(afc_instance.client, reconcile_data)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _status = False
        _message = ""
        _changed = False

        try:

            switches_list = utils.populate_list_fabrics_switches(
                client,
                data,
            )

        except exceptions.NotGoodVar:
            _message = ("Fabric and Switches variables are not "
                        "provided. No action taken")
            return _message, _status, _changed
        except exceptions.FabricNotFound:
            _message = "Fabric not found - No action taken"
            return _message, _status, _changed
        except exceptions.NoDeviceFound:
            _message = "Devices not found - No action taken"
            return _message, _status, _changed

        data = models.ReconcileSwitches(
            switches=switches_list["switch_uuids "]
        )
        uri_reconcile = "/switches/reconcile"
        reconcile_request = client.put(
            uri_reconcile,
            data=json.dumps(data.dict()),
        )

        if reconcile_request.status_code in utils.response_ok:
            _message = "Successfully launch devices reconciliation"
            _status = True
            _changed = True
        else:
            _message = reconcile_request.json()["result"]

        return _message, _status, _changed

    @staticmethod
    def save_config(client: Client, data: dict) -> tuple:
        """save_config Save switch configuration.

        Args:
            client (Client): Client instance to Connect and Authenticate.
            switches (list, optional): List of switches on which configuration
                has to be saved.
            fabrics (list, optional): List of Fabrics on which configuration
                has to be saved.

        Example:
            save_data = {
                "switches": ["10.149.2.100-10.149.2.109"]
                }

            switches.Switch.save_config(afc_instance.client, save_data)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _status = False
        _message = ""
        _changed = False

        try:
            switches_list = utils.populate_list_fabrics_switches(
                client,
                data,
            )

        except exceptions.NotGoodVar:
            _message = ("Fabric and Switches variables are not "
                        "provided. No action taken")
            return _message, _status, _changed
        except exceptions.FabricNotFound:
            _message = "Fabric not found - No action taken"
            return _message, _status, _changed
        except exceptions.NoDeviceFound:
            _message = "Devices not found - No action taken"
            return _message, _status, _changed


        data = models.SaveConfigSwitches(
            switches=switches_list["switch_uuids"]
        )
        uri_save_config = "/switches/save_config"
        save_config_request = client.put(
            uri_save_config,
            data=json.dumps(data.dict()),
        )
        if save_config_request.status_code in utils.response_ok:
            _message = "Successfully saved configuration"
            _status = True
            _changed = True
        else:
            _message = save_config_request.json()["result"]

        return _message, _status, _changed

    def update(self, data: dict) -> tuple:
        """Update the switch in AFC.

        Args:
            data (dict): Data to update.

        Returns:
            True if the switch is deleted, else False.

        """
        _status = False
        _message = ""
        _changed = False

        try:
            data = models.Switch(**data).dict(exclude_none=True)
        except ValidationError:
            _message = "Some attributes or values are not as expected"
            return _message, _status, _changed

        try:
            update_payload = []
            device_payload = {}
            device_payload["uuids"] = [self.uuid]
            device_payload["patch"] = []

            if data.get("fabric"):
                data["fabric_uuid"] = fabric.Fabric.get_fabric_uuid(
                    data["fabric"],
                )
                if not data["fabric_uuid"]:
                    _message = (f"Fabric {data['fabric']} "
                                "not found. No action taken")
                    return _message, _status, _changed

            for item, value in data.items():
                device_payload["patch"].append(
                    {
                        "path": f"/{item}",
                        "value": value,
                        "op": "replace",
                    }
                )
            update_payload.append(device_payload)

            switch_request = self.client.patch(
                "switches", data=json.dumps(update_payload)
            )

            if switch_request.status_code in utils.response_ok:
                _message = "Device successfully updated"
                _status = True
                _changed = True
            else:
                _message = "Device has not been updated"
        except Exception:
            _message = "An issue ocurred"

        return _message, _status, _changed

    def delete(self) -> bool:
        """Delete Delete the switch from AFC.

        Returns:
            True if the switch is deleted, else False.

        """
        switch_request = self.client.delete(
            f"switches/{self.uuid}",
        )
        return switch_request.status_code in utils.response_ok

    def discover_device(self, **kwargs: dict) -> bool:
        """_discover_device Triggers Device Discovery in AFC.

        Args:
            kwargs (str): device IP Addresses.

        Returns:
            bool: True if successful, otherwise False.

        """
        try:
            data = models.SwitchDiscovery(switches=[self.ipaddress], **kwargs)
            add_request = self.client.post(
                "switches/discover",
                data=json.dumps(data.dict(exclude_none=True)),
            )
            if add_request.status_code in utils.response_ok:
                switch_details = self.get_switch_details()
                while (
                    switch_details["status"] != "UNASSIGNED"
                    and switch_details["health"]["status"] != "healthy_but"
                ):
                    time.sleep(2)
                    switch_details = self.get_switch_details()
                self.__instantiate_attributes()
            else:
                return False
        except ValidationError:
            return False

    async def __check_devices_status(
        self,
        devices: list,
        **kwargs: dict,
    ) -> None:
        """__check_devices_status Asyncio function to check device status.

        Args:
            devices (list): List of devices IP addresses.
            kwargs (str): Additional details.

        Returns:
            bool: True if successful, otherwise False.

        """
        async_tasks = []

        async def check_status(device: str) -> bool:
            switch_instance = Switch(self.client, device, **kwargs)
            switch_details = switch_instance.get_switch_details()
            while (
                switch_details["status"] != "UNASSIGNED"
                and switch_details["health"]["status"] != "healthy_but"
            ):
                await asyncio.sleep(2)
                switch_details = switch_instance.get_switch_details()
            return True

        async_tasks.extend(
            asyncio.create_task(check_status(device)) for device in devices
        )

        await asyncio.gather(*async_tasks)

    def __correlate_ips_issues(self, statement: str) -> str:
        _s = " "
        _ip = re.findall(r"[0-9]+(?:\.[0-9]+){3}", statement)
        _issues = re.findall(r"\(.*?\)", statement)
        _existing_list = []
        _unreachable_list = []
        for _index, _item in enumerate(_issues):
            if _item == "(already exists)":
                _existing_list.append(_ip[_index])
            if _item == "(Unreachable)":
                _unreachable_list.append(_ip[_index])
        if _existing_list:
            _s += f"{_s.join(_existing_list)} are already discovered."
        if _unreachable_list:
            _s += f"{_s.join(_unreachable_list)} are unreachable."
        return _s

    def discover_multiple_devices(self, **kwargs: dict) -> tuple:
        """discover_multiple_devices Triggers discovery of multiple devices.

        Args:
            switches (list) = List of IP Addresses to discover
            admin_passwd (str) = Admin password to connect on switches.
            afc_admin_passwd (str) = AFC user password to create on switches

        Example:
            device_discovery = ["10.149.2.100-10.149.2.107","10.149.2.110"]
            discovery_data = {
                    "admin_passwd": "<switch_password>",
                    "afc_admin_passwd": "<afc_password>",
                }
            switches_instance.discover_multiple_devices(switches=device_discovery,
                                                        **discovery_data)
        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _status = False
        _message = ""
        _changed = False

        try:
            kwargs["switches"] = utils.extend_switches_ranges(
                kwargs["switches"],
            )

            data = models.SwitchDiscovery(**kwargs)

            add_request = self.client.post(
                "switches/discover",
                data=json.dumps(data.dict(exclude_none=True)),
            )

            if add_request.status_code in utils.response_ok:
                asyncio.run(
                    self.__check_devices_status(kwargs["switches"], **kwargs),
                )
                if len(add_request.json()["result"]) > 0:
                    _s = " "
                    _message = ("Successfully completed discovery of "
                                f"{_s.join(kwargs['switches'])}")
                    _status = True
                    _changed = True
            elif (
                isinstance(add_request.json()["result"], str)
                and ("already" or "Unreachable")
                in add_request.json()["result"]
            ):
                _message = self.__correlate_ips_issues(
                    add_request.json()["result"]
                )
                _status = True
            elif len(add_request.json()["result"]) > 0:
                _failure_ips = []
                _failure_message = " "
                for _item in add_request.json()["result"]:
                    if _item["status"] == "failure":
                        _ip = re.findall(
                            r"[0-9]+(?:\.[0-9]+){3}", _item["reason"]
                        )
                        _failure_ips += _ip
                        _failure_message += self.__correlate_ips_issues(
                            _item["reason"],
                        )
                _discovered_ips = [
                    x for x in kwargs["switches"] if x not in _failure_ips
                ]
                _s = " "
                _message += ("Successfully completed discovery "
                             f"of {_s.join(_discovered_ips)}.")
                if len(_failure_ips) > 0:
                    _message += _failure_message
                _status = True
                _changed = True

            else:
                _message = add_request.json()["result"]

        except ValidationError as exc:
            _message = (
                f"An exception {exc} occurred while discovering the switches"
            )
            return _message, _status, _changed

        else:
            return _message, _status, _changed
