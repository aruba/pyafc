# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Utility functions and classes for VLAN management.

This module provides:
- get_vlans: Get all VLANs configured on the Fabric
- get_vlan: Get a specific VLAN by its ID
- create_vlan: Create one or more VLANs and assign them to devices
- update_vlan: Update VLAN(s) and/or assign them to additional devices
- delete_vlan: Delete VLAN(s) entirely or unassign them from devices
"""

from __future__ import annotations

import json

from pydantic import ValidationError

from pyafc.common import utils
from pyafc.fabric import models


class Vlan:
    def __init__(self) -> None:
        """__init__ Init Method."""

    def get_vlans(self) -> list:
        """get_vlans Get all VLANs configured on that Fabric.

        Returns:
            List of VLAN objects in JSON format.

        """
        vlan_request = self.client.get(f"fabrics/{self.uuid}/vlans")
        return vlan_request.json()["result"]

    def get_vlan(self, vlan_id: int) -> dict | bool:
        """get_vlan Get a specific VLAN by its ID.

        Args:
            vlan_id (int): VLAN ID.

        Returns:
            VLAN object in JSON format if found, else False.

        """
        for vlan in self.get_vlans():
            if vlan["vlan_id"] == int(vlan_id):
                return vlan
        return False

    @staticmethod
    def _expand_vlan_range(vlan_id: str | int) -> list:
        """_expand_vlan_range Expand a VLAN range into a list of IDs.

        Args:
            vlan_id (str | int): VLAN range(s), e.g. "10", "10,20-22".

        Returns:
            List of VLAN IDs as integers.

        """
        vlan_ids: list = []
        for chunk in str(vlan_id).split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            if "-" in chunk:
                start, end = chunk.split("-")
                vlan_ids.extend(range(int(start), int(end) + 1))
            else:
                vlan_ids.append(int(chunk))
        return vlan_ids

    def _resolve_vlan_uuids(self, vlan_id: str | int) -> list:
        """_resolve_vlan_uuids Find the UUIDs of the specified VLAN IDs.

        Args:
            vlan_id (str | int): VLAN range(s), e.g. "10", "10,20-22".

        Returns:
            List of VLAN UUIDs matching the requested IDs.

        """
        wanted = set(self._expand_vlan_range(vlan_id))
        return [
            vlan["uuid"]
            for vlan in self.get_vlans()
            if vlan["vlan_id"] in wanted
        ]

    def create_vlan(self, **kwargs: dict) -> tuple:
        """create_vlan Create one or more VLANs and assign them to devices.

        Args:
            vlan_id (str): VLAN range(s), e.g. "10" or "10,20-30".
            vlan_name (str, optional): Name given to the VLAN(s).
            switches (list, optional): List of devices (IP or name) to which
                the VLAN(s) are assigned.
            fabric_scope (str, optional): Alternative to switches. One of
                'include_spine' or 'exclude_spine'.
            strict_firewall_bypass_enabled (bool, optional): Defaults to True.

        Example:
            fabric_instance.create_vlan(
                vlan_id="100,200-202",
                vlan_name="Production",
                switches=["10.149.2.10", "Leaf-1"],
            )

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            switches = kwargs.get("switches")
            fabric_scope = kwargs.get("fabric_scope")

            if switches:
                switch_uuids = utils.consolidate_switches_list(
                    self.client, switches,
                )
                if not switch_uuids:
                    return (
                        "No matching device found. No action taken",
                        False,
                        False,
                    )
                vlan_scope = {"switch_uuids": switch_uuids}
            elif fabric_scope:
                vlan_scope = {"fabric_scope": fabric_scope}
            else:
                return (
                    "Neither switches nor fabric_scope provided. "
                    "No action taken",
                    False,
                    False,
                )

            vlan_entry = {
                "vlan_id": kwargs.get("vlan_id"),
                "vlan_name": kwargs.get("vlan_name"),
            }
            if kwargs.get("strict_firewall_bypass_enabled") is not None:
                vlan_entry["strict_firewall_bypass_enabled"] = kwargs[
                    "strict_firewall_bypass_enabled"
                ]

            data = models.VlanTable(vlans=[vlan_entry], vlan_scope=vlan_scope)
            vlan_request = self.client.post(
                f"fabrics/{self.uuid}/vlans",
                data=json.dumps(data.model_dump(exclude_none=True)),
            )
            if vlan_request.status_code in utils.response_ok:
                _message = f"Successfully created VLAN(s) {kwargs.get('vlan_id')}"
                _status = True
                _changed = True
            else:
                _message = vlan_request.json()["result"]

        except ValidationError as exc:
            _message = f"An exception {exc} occurred"
        except Exception as exc:
            _message = f"An issue occured - {exc}. No action taken"

        return _message, _status, _changed

    def update_vlan(self, **kwargs: dict) -> tuple:
        """update_vlan Update VLAN(s) and/or assign them to more devices.

        Args:
            vlan_id (str): VLAN range(s) to update, e.g. "10" or "10,20-30".
            vlan_name (str, optional): New name for the VLAN(s). Renaming an
                existing VLAN is dependent on the AFC version and may be a
                no-op on some releases; assigning devices always applies.
            switches (list, optional): List of devices (IP or name) to which
                the VLAN(s) are additionally assigned.
            strict_firewall_bypass_enabled (bool, optional): New value.

        Example:
            fabric_instance.update_vlan(
                vlan_id="100",
                vlan_name="Prod-Renamed",
                switches=["Leaf-2"],
            )

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            vlan_id = kwargs.get("vlan_id")
            vlan_uuids = self._resolve_vlan_uuids(vlan_id)
            if not vlan_uuids:
                return (
                    f"VLAN(s) {vlan_id} not found. No action taken",
                    False,
                    False,
                )

            patch: list = []
            if kwargs.get("switches"):
                switch_uuids = utils.consolidate_switches_list(
                    self.client, kwargs["switches"],
                )
                if not switch_uuids:
                    return (
                        "No matching device found. No action taken",
                        False,
                        False,
                    )
                patch.append(
                    {
                        "op": "add",
                        "path": "/switch_uuids",
                        "value": switch_uuids,
                    },
                )
            if kwargs.get("vlan_name") is not None:
                patch.append(
                    {
                        "op": "replace",
                        "path": "/vlan_name",
                        "value": kwargs["vlan_name"],
                    },
                )
            if kwargs.get("strict_firewall_bypass_enabled") is not None:
                patch.append(
                    {
                        "op": "replace",
                        "path": "/strict_firewall_bypass_enabled",
                        "value": kwargs["strict_firewall_bypass_enabled"],
                    },
                )

            if not patch:
                return "Nothing to update. No action taken", True, False

            body = [{"uuids": vlan_uuids, "patch": patch}]
            vlan_request = self.client.patch(
                f"fabrics/{self.uuid}/vlans",
                data=json.dumps(body),
            )
            if vlan_request.status_code in utils.response_ok:
                _message = f"Successfully updated VLAN(s) {vlan_id}"
                _status = True
                _changed = True
            else:
                _message = vlan_request.json()["result"]

        except Exception as exc:
            _message = f"An issue occured - {exc}. No action taken"

        return _message, _status, _changed

    def delete_vlan(self, **kwargs: dict) -> tuple:
        """delete_vlan Delete VLAN(s) or unassign them from devices.

        When 'switches' is provided, the VLAN(s) are only removed from the
        specified devices. Without 'switches', the VLAN(s) are deleted from
        the whole Fabric.

        Args:
            vlan_id (str): VLAN range(s), e.g. "10" or "10,20-30".
            switches (list, optional): List of devices (IP or name) from which
                the VLAN(s) are unassigned.

        Example:
            fabric_instance.delete_vlan(vlan_id="100")
            fabric_instance.delete_vlan(vlan_id="100", switches=["Leaf-2"])

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            vlan_id = kwargs.get("vlan_id")
            vlan_uuids = self._resolve_vlan_uuids(vlan_id)
            if not vlan_uuids:
                return (
                    f"VLAN(s) {vlan_id} not found. No action taken",
                    True,
                    False,
                )

            uri_vlan = (
                f"fabrics/{self.uuid}/vlans?vlan_uuids={','.join(vlan_uuids)}"
            )
            if kwargs.get("switches"):
                switch_uuids = utils.consolidate_switches_list(
                    self.client, kwargs["switches"],
                )
                if not switch_uuids:
                    return (
                        "No matching device found. No action taken",
                        False,
                        False,
                    )
                uri_vlan += f"&switches={','.join(switch_uuids)}"

            vlan_request = self.client.delete(uri_vlan)
            if vlan_request.status_code in utils.response_ok:
                if kwargs.get("switches"):
                    _message = (
                        f"Successfully unassigned VLAN(s) {vlan_id} "
                        "from the specified devices"
                    )
                else:
                    _message = f"Successfully deleted VLAN(s) {vlan_id}"
                _status = True
                _changed = True
            else:
                _message = vlan_request.json()["result"]

        except Exception as exc:
            _message = f"An issue occured - {exc}. No action taken"

        return _message, _status, _changed
