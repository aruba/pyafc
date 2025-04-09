# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import exceptions, utils
from pyafc.dss import models
from pyafc.integrations import vmware, vswitches


class VnicMove:
    def __init__(self, client, **kwargs: dict) -> None:
        """__init__ VnicMove main class file. Return the vNIC to be moved.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            kwargs (dict): Keyword arguments needed for vnic move.

        Returns:
            None.

        """
        if client:
            self.client = client
        self.vnic_move(**kwargs)

    def get_vm(
        self,
        vm_name: str | None = None,
        vnic_name: str | None = None,
        vm_tag: str | None = None,
    ) -> str:
        """get_vm get VM to perform vnic move.

        Args:
            vm_name (str): Name of the VM.
            vm_tag (str): Name of the vm tag.

        Returns:
            vm_info (dict): Dictionary value of VM Info.

        """
        vm_info, _ = vmware.Vsphere.get_vm_info(
            self.client, vm_name=vm_name, vm_tag=vm_tag,
        )

        if not vm_info:
            msg = f"VM {vm_name} has not been found"
            raise exceptions.VMNotFound(msg)

        for nic in vm_info["nics"]:
            if nic["name"] == vnic_name:
                return vm_info["nics"][0]["associated_objects"]["vmware"][
                    "uuid"
                ]

        msg = f"NIC {vnic_name} not found on VM {vm_name}"
        raise exceptions.NICNotFound(msg)

    def vnic_move(self, **values: dict) -> tuple:
        """vnic_move is used to to move vNICs.

        Args:
            vswitch (str): name of the vSwitch.
            vnics (list): List of vNICs to move.

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed somethings.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            vswitch_uuid = vswitches.vSwitch.get_vswitch_uuid(
                self.client, values["vswitch"]
            )

            if vswitch_uuid:
                for move in values["vnics"]:
                    move["portgroup_uuid"] = vswitches.vSwitch.get_pg_uuid(
                        self.client, move["portgroup"],
                    )
                    if move.get("vnics"):
                        vnics_uuids = [
                            self.get_vm(**vm) for vm in move["vnics"]
                        ]
                        move["vnic_uuids"] = vnics_uuids

            data = models.MoveVnic(**values)

            move_uri = f"hosts/vswitches/{vswitch_uuid}/add_pvlan_vnics"

            add_request = self.client.post(
                move_uri,
                data=json.dumps(data.dict(exclude_none=True)),
            )

            if add_request.status_code in utils.response_ok:
                _message = "Successfully moved VNIC"
                _status = True
                _changed = True
            else:
                _message = add_request.json()["result"]

        except (
            exceptions.PortGroupNotFound,
            exceptions.VMNotFound,
            exceptions.vSwitchNotFound,
            exceptions.NICNotFound,
        ) as exc:
            _message = f"An exception {exc} occurred"

        return _message, _status, _changed
