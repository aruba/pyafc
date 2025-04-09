# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import asyncio
import json
import time
from asyncio import run as aiorun
from ipaddress import IPv4Address

from pydantic import ValidationError

from pyafc.common import utils
from pyafc.common.internal import Internal
from pyafc.fabric import (
    evpn,
    leaf_spine,
    models,
    multi_fabrics,
    pvlan,
    vsx,
    vxlan,
)
from pyafc.switches import switches


class Fabric(
    leaf_spine.LS,
    evpn.EVPN,
    vsx.VSX,
    pvlan.PVLAN,
    multi_fabrics.MultiFabrics,
    vxlan.Vxlan,
    Internal,
):
    def __init__(self, client, name: str, **kwargs: dict) -> None:
        self.client = client
        self.uuid = None
        self.name = name
        self.__instantiate_details()

    @staticmethod
    def get_fabric_uuid(client, name: str) -> str | bool:
        """get_fabric_uuid Find Fabric UUID.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the fabric.

        Returns:
            fabric['uuid'] (str): Fabric UUID if found.

        """
        fabrics_request = client.get("fabrics")
        for fabric in fabrics_request.json()["result"]:
            if fabric["name"] == name:
                return fabric["uuid"]

        return False

    def __instantiate_details(self) -> bool:
        """__instantiate_details Instantiate Fabric attributes.

        Returns:
            True if found and UUID is set as the class attribute, False if not.

        """
        fabrics_request = self.client.get("fabrics")
        for fabric in fabrics_request.json()["result"]:
            if fabric["name"] == self.name:
                for item, value in fabric.items():
                    setattr(self, item, value)
                return True

        return False

    def create_fabric(self, name: str, **kwargs: dict) -> tuple:
        """create_fabric Function allowing to create a Fabric.

        Args:
            name (str): Name of the fabric.
            timezone (str): Timezone of the Fabric. Must use format
                            'America/Los Angeles'
            fabric_class (str, optional): One of :
                - 'Data'
                - 'Management'
                Defaults to 'Data'

        Example:
            fabric_instance.create_fabric('timezone': 'Europe/Paris')

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): True if configuration has changed, else false.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.__instantiate_details():
                _message = (
                    f"The Fabric {self.name} already exists. No action taken"
                )
                _status = True
            else:
                data = models.Fabric(name=name, **kwargs)
                fabric_request = self.client.post(
                    "fabrics",
                    data=json.dumps(data.dict(exclude_none=True)),
                )
                if fabric_request.status_code in utils.response_ok:
                    if self.__instantiate_details():
                        _message = (f"The Fabric {self.name} has been "
                                    "successfully created")
                        _status = True
                        _changed = True
                    else:
                        _message = (
                            f"There was an error creating fabric {self.name}"
                        )
                else:
                    _message = fabric_request.json()["result"]
        except ValidationError as exc:
            _message = (
                f"An exception {exc} occurred while trying to create Fabric"
            )

        return _message, _status, _changed

    def delete_fabric(self) -> tuple:
        """delete_fabric Function allowing to delete a Fabric.

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): True if configuration has changed, else false.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if not self.__instantiate_details():
                _message = (
                    f"The Fabric {self.name} does not exist. No action taken."
                )
                _status = True
            else:
                fabric_request = self.client.get(f"fabrics/{self.uuid}")
                fabric_objects = []
                l2_leaf_spine_request = self.client.get(
                    "fabrics/l2_leaf_spine",
                )
                if len(l2_leaf_spine_request.json()["result"]) > 0:
                    for l2_leaf_spine in l2_leaf_spine_request.json()[
                        "result"
                    ]:
                        if (
                            "fabric_uuid" in l2_leaf_spine
                            and self.uuid == l2_leaf_spine["fabric_uuid"]
                        ):
                            fabric_objects.append(l2_leaf_spine)
                leaf_spine_request = self.client.get("fabrics/leaf_spine")
                if len(leaf_spine_request.json()["result"]) > 0:
                    for leaf_spine in leaf_spine_request.json()["result"]:
                        if (
                            "fabric_uuid" in leaf_spine
                            and self.uuid == leaf_spine["fabric_uuid"]
                        ):
                            fabric_objects.append(leaf_spine)
                multi_hop_vxlan_request = self.client.get(
                    "fabrics/multi_hop_vxlan"
                )
                if len(multi_hop_vxlan_request.json()["result"]) > 0:
                    for multi_hop_vxlan in multi_hop_vxlan_request.json()[
                        "result"
                    ]:
                        if (
                            "fabric_uuid" in multi_hop_vxlan
                            and self.uuid == multi_hop_vxlan["fabric_uuid"]
                        ):
                            fabric_objects.append(multi_hop_vxlan)
                pvlans_request = self.client.get("fabrics/pvlans")
                if len(pvlans_request.json()["result"]) > 0:
                    for pvlan in pvlans_request.json()["result"]:
                        if (
                            "fabric_uuid" in pvlan
                            and self.uuid == pvlan["fabric_uuid"]
                        ):
                            fabric_objects.append(pvlan)
                subleaf_leaf_request = self.client.get("fabrics/subleaf_leaf")
                if len(subleaf_leaf_request.json()["result"]) > 0:
                    for subleaf_leaf in subleaf_leaf_request.json()["result"]:
                        if (
                            "fabric_uuid" in subleaf_leaf
                            and self.uuid == subleaf_leaf["fabric_uuid"]
                        ):
                            fabric_objects.append(subleaf_leaf)
                vsf_request = self.client.get("fabrics/vsf")
                if len(vsf_request.json()["result"]) > 0:
                    for vsf in vsf_request.json()["result"]:
                        if (
                            "fabric_uuid" in vsf
                            and self.uuid == vsf["fabric_uuid"]
                        ):
                            fabric_objects.append(vsf)
                vsx_request = self.client.get("fabrics/vsx")
                if len(vsx_request.json()["result"]) > 0:
                    for vsx in vsx_request.json()["result"]:
                        if (
                            "fabric_uuid" in vsx
                            and self.uuid == vsx["fabric_uuid"]
                        ):
                            fabric_objects.append(vsx)
                vxlan_tunnels_request = self.client.get(
                    "fabrics/vxlan_tunnels"
                )
                if len(vxlan_tunnels_request.json()["result"]) > 0:
                    for vxlan_tunnel in vxlan_tunnels_request.json()["result"]:
                        if (
                            "fabric_uuid" in vxlan_tunnel
                            and self.uuid == vxlan_tunnel["fabric_uuid"]
                        ):
                            fabric_objects.append(vxlan_tunnel)
                switches_request = self.client.get("switches")
                if len(switches_request.json()["result"]) > 0:
                    for switch in switches_request.json()["result"]:
                        if (
                            "fabric_uuid" in switch
                            and self.uuid == switch["fabric_uuid"]
                        ):
                            fabric_objects.append(switch)
                if len(fabric_objects) > 0:
                    _message = (f"The fabric {self.name} has objects. "
                                "Cannot be deleted")
                else:
                    fabric_delete_request = self.client.delete(
                        f"fabrics/{self.uuid}",
                    )
                    if fabric_delete_request.status_code in utils.response_ok:
                        if not self.__instantiate_details():
                            _message = (f"The Fabric {self.name} has "
                                        "been successfully deleted")
                            _status = True
                            _changed = True
                        else:
                            _message = ("There was an error deleting "
                                        f"the fabric {self.name}")
                    else:
                        _message = fabric_request.json()["result"]
        except ValidationError as exc:
            _message = (
                f"An exception {exc} occurred while trying to delete Fabric"
            )

        return _message, _status, _changed

    def add_single_to_fabric(self, device: str, role: str = "leaf") -> tuple:
        """add_single_to_fabric Single device assignment to a Fabric.

        Args:
            device (str): IP address of the device to be added to the fabric.
            role (str): Role of the device during assignment, defaults to leaf.

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): True if configuration has changed, else false.

        """
        if not self.uuid:
            _message = "Fabric does not exist - Create it first"
            _changed = False
            _status = False
            return _message, _status, _changed

        switch_instance = switches.Switch(self.client, device)
        if switch_instance.uuid and not switch_instance.fabric_uuid:
            assign_payload = [
                {
                    "uuids": [switch_instance.uuid],
                    "patch": [
                        {
                            "path": "/fabric_uuid",
                            "value": self.uuid,
                            "op": "replace",
                        },
                        {
                            "path": "/role",
                            "value": role,
                            "op": "replace",
                        },
                    ],
                },
            ]
            add_request = self.client.patch(
                "switches",
                data=json.dumps(assign_payload),
            )
            if add_request.status_code in utils.response_ok:
                switch_details = switch_instance.get_switch_details()
                while (
                    switch_details["status"] != "SYNCED"
                    and switch_details["health"]["status"] != "healthy"
                ):
                    time.sleep(2)
                    switch_details = switch_instance.get_switch_details()
                return True

            return False
        return False

    async def __check_devices_status(self, devices: list) -> bool:
        """__check_devices_status Check the status of device for the workflow.

        Args:
            devices (list): List of devices IP addresses.

        Returns:
            True if status is SYNCED, else keeps retrying.

        """
        async_tasks = []

        async def check_status(device: dict) -> bool:
            switch_instance = switches.Switch(self.client, device)
            switch_details = switch_instance.get_switch_details()
            while (
                switch_details["status"] != "SYNCED"
                and switch_details["health"]["status"] != "healthy"
            ):
                time.sleep(2)
                switch_details = switch_instance.get_switch_details()
            return True

        for device in devices:
            async_tasks.append(asyncio.create_task(check_status(device)))

        await asyncio.gather(*async_tasks)

        return True

    def add_multiple_to_fabric(self, **kwargs: dict) -> tuple:
        """add_multiple_to_fabric Add multiple devices assignment to a Fabric.

        Args:
            roles (dict): Devices with respective role.

        Example:
            fabric_instance.add_multiple_to_fabric('roles': {
                                    '10.149.2.100-10.149.2.101': 'border_leaf',
                                    '10.149.2.102-10.149.2.103': 'spine',
                                    '10.149.2.104-10.149.2.107': 'leaf',
                                    '10.149.2.110': 'sub_leaf',
                                })

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed something.

        """
        leaf_switches = []
        spines_switches = []
        borders_switches = []
        subleaf_switches = []
        _status = False
        _changed = False
        _message = ""
        _extended_sw_list = {}
        _discovered_list = []
        _undiscovered_list = []
        _infabric_list = []

        if not self.uuid:
            _message = "Fabric does not exist - Create it first"
            _changed = False
            _status = False
            return _message, _status, _changed

        for device, role in kwargs["roles"].items():
            if len(device.split("-")) > 1:
                try:
                    IPv4Address(device.split("-")[0])
                    IPv4Address(device.split("-")[1])
                    sw_list = utils.get_switches_list_from_scope(device)
                    for sw in sw_list:
                        _extended_sw_list[sw] = role
                except:
                    _extended_sw_list[
                        switches.Switch.consolidate_ip(self.client, device)
                    ] = role  # noqa: E501
            else:
                _extended_sw_list[
                    switches.Switch.consolidate_ip(self.client, device)
                ] = role  # noqa: E501

        _devices_list = _extended_sw_list.copy()

        for device, role in _extended_sw_list.items():

            switch_instance = switches.Switch(self.client, device)

            if not hasattr(switch_instance, "uuid"):
                _undiscovered_list.append(device)
                _devices_list.pop(device)
            elif (
                hasattr(switch_instance, "fabric_uuid")
                and switch_instance.fabric_uuid is not None
            ):  # noqa: E501
                _infabric_list.append(device)
                _devices_list.pop(device)
            else:  # noqa: PLR5501
                if role == "leaf":
                    leaf_switches.append(switch_instance.uuid)
                    _discovered_list.append(device)
                elif role == "spine":
                    spines_switches.append(switch_instance.uuid)
                    _discovered_list.append(device)
                elif role == "border_leaf":
                    borders_switches.append(switch_instance.uuid)
                    _discovered_list.append(device)
                elif role == "sub_leaf":
                    subleaf_switches.append(switch_instance.uuid)
                    _discovered_list.append(device)
                else:
                    _devices_list.pop(device)

        assign_payload = []

        if len(leaf_switches) > 0:
            assign_payload.append(
                {
                    "uuids": leaf_switches,
                    "patch": [
                        {
                            "path": "/fabric_uuid",
                            "value": self.uuid,
                            "op": "replace",
                        },
                        {
                            "path": "/role",
                            "value": "leaf",
                            "op": "replace",
                        },
                    ],
                },
            )
        if len(spines_switches) > 0:
            assign_payload.append(
                {
                    "uuids": spines_switches,
                    "patch": [
                        {
                            "path": "/fabric_uuid",
                            "value": self.uuid,
                            "op": "replace",
                        },
                        {
                            "path": "/role",
                            "value": "spine",
                            "op": "replace",
                        },
                    ],
                },
            )
        if len(borders_switches) > 0:
            assign_payload.append(
                {
                    "uuids": borders_switches,
                    "patch": [
                        {
                            "path": "/fabric_uuid",
                            "value": self.uuid,
                            "op": "replace",
                        },
                        {
                            "path": "/role",
                            "value": "border_leaf",
                            "op": "replace",
                        },
                    ],
                },
            )
        if len(subleaf_switches) > 0:
            assign_payload.append(
                {
                    "uuids": subleaf_switches,
                    "patch": [
                        {
                            "path": "/fabric_uuid",
                            "value": self.uuid,
                            "op": "replace",
                        },
                        {
                            "path": "/role",
                            "value": "sub_leaf",
                            "op": "replace",
                        },
                    ],
                },
            )

        if (
            len(leaf_switches) > 0
            or len(spines_switches) > 0
            or len(borders_switches) > 0
            or len(subleaf_switches) > 0
        ):

            add_request = self.client.patch(
                "switches",
                data=json.dumps(assign_payload),
            )

            if add_request.status_code in utils.response_ok:
                if aiorun(self.__check_devices_status(_devices_list)):
                    if len(_devices_list.keys()) == 1:
                        _sv = "is"
                        _dev_sing_plu = "device"
                    else:
                        _sv = "are"
                        _dev_sing_plu = "devices"
                    _message = (f"Successfully added {_dev_sing_plu} "
                                f"{' '.join(_devices_list.keys())} "
                                "to the Fabric "
                                f"{self.name}.")
                    _status = True
                    _changed = True
                    if len(_undiscovered_list) > 0 and len(_infabric_list) > 0:
                        if len(_undiscovered_list) == 1:
                            _ud_sv = "is"
                            _ud_sing_plu = "Device"
                        else:
                            _ud_sv = "are"
                            _ud_sing_plu = "Devices"
                        if len(_infabric_list) == 1:
                            _if_sv = "is"
                            _if_sing_plu = "device"
                        else:
                            _if_sv = "are"
                            _if_sing_plu = "devices"
                        _message += (f" {_ud_sing_plu} "
                                     f"{' '.join(_undiscovered_list)} "
                                     f"{_ud_sv} not discovered yet "
                                     f"and {_if_sing_plu} "
                                     f"{' '.join(_infabric_list)} "
                                     f"{_if_sv} already part of a fabric.")
                    elif (
                        len(_undiscovered_list) > 0
                        and len(_infabric_list) == 0
                    ):
                        if len(_undiscovered_list) == 1:
                            _ud_sv = "is"
                            _ud_sing_plu = "Device"
                        else:
                            _ud_sv = "are"
                            _ud_sing_plu = "Devices"
                        _message += (f" {_ud_sing_plu} "
                                     f"{' '.join(_undiscovered_list)} "
                                     f"{_ud_sv} not discovered yet.")
                    elif (
                        len(_undiscovered_list) == 0
                        and len(_infabric_list) > 0
                    ):
                        if len(_infabric_list) == 1:
                            _if_sv = "is"
                            _if_sing_plu = "Device"
                        else:
                            _if_sv = "are"
                            _if_sing_plu = "Devices"
                        _message += (f" {_if_sing_plu} "
                                     f"{' '.join(_infabric_list)} "
                                     f"{_if_sv} already part of a fabric.")
                        _status = True
                    return _message, _status, _changed
            else:
                _message = add_request.json()["result"]
                _changed = False
                _status = False
                return _message, _status, _changed
        elif len(_undiscovered_list) > 0 and len(_infabric_list) > 0:
            if len(_undiscovered_list) == 1:
                _ud_sv = "is"
                _ud_sing_plu = "Device"
            else:
                _ud_sv = "are"
                _ud_sing_plu = "Devices"
            if len(_infabric_list) == 1:
                _if_sv = "is"
                _if_sing_plu = "device"
            else:
                _if_sv = "are"
                _if_sing_plu = "devices"
            _message += (f"{_ud_sing_plu} {' '.join(_undiscovered_list)} "
                         f"{_ud_sv} not discovered yet and {_if_sing_plu} "
                         f"{' '.join(_infabric_list)} {_if_sv} already part "
                         "of a fabric.")
        elif len(_undiscovered_list) > 0 and len(_infabric_list) == 0:
            if len(_undiscovered_list) == 1:
                _ud_sv = "is"
                _ud_sing_plu = "Device"
            else:
                _ud_sv = "are"
                _ud_sing_plu = "Devices"
            _message += (f"{_ud_sing_plu} {' '.join(_undiscovered_list)} "
                        f"{_ud_sv} not discovered yet.")
        elif len(_undiscovered_list) == 0 and len(_infabric_list) > 0:
            if len(_infabric_list) == 1:
                _if_sv = "is"
                _if_sing_plu = "Device"
            else:
                _if_sv = "are"
                _if_sing_plu = "Devices"
            _message += (f"{_if_sing_plu} {' '.join(_infabric_list)} "
                         f"{_if_sv} already part of a fabric.")
            _status = True
        return _message, _status, _changed
