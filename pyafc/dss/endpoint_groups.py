# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import exceptions, utils
from pyafc.dss import models
from pyafc.integrations import vmware


class EndpointGroup:
    def __init__(self, client=None, name: str | None = None, **kwargs: dict) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the Endpoint Group.

        Returns:
            existing_eg (bool): True if available, False if not.

        """
        if name:
            self.name = name
        if client:
            self.client = client
        self.uuid = None
        self.existing_eg = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details class attribute uuid is set.

        Returns:
            existing_eg (bool): True if available, False if not.

        """
        eg_request = self.client.get("endpoint_groups")
        for eg in eg_request.json()["result"]:
            if eg["name"] == self.name:
                self.uuid = eg["uuid"]
                return True
        return False

    def _get_vm_detail(
        self,
        vm_name: str | None = None,
        vmkernel_adapter_name: str | None = None,
        vnic_name: str | None = None,
        vm_tag: str | None = None,
        ipv4_range: str | None = None,
        host_name: str | None = None,
        **kwargs: dict,
    ) -> tuple:
        """_get_vm_detail the function is used to get the VM details.

        Args:
            vm_name (str, optional): Name of the VM.
            vmkernel_adapter_name (str, optional): VMKernel adapter name.
            vnic_name (str, optional): vNIC Name.
            vm_tag (str, optional): VM Tag.
            ipv4_range (str, optional): IPv4 Range.
            host_name (str, optional): Host name.

        Returns:
            VM Details (dict): Get details of the VM.

        """
        vsphere_uuid = False
        vm_tag = vm_tag if vm_tag else []

        if vm_name:
            vm_info, host = vmware.Vsphere.get_vm_info(
                self.client, vm_name, vm_tag,
            )
            if vm_info:
                for nic in vm_info["nics"]:
                    if nic["name"] == vnic_name:
                        if len(nic["ip_addresses"]) == 1 and not ipv4_range:
                            ipv4_range = f"{nic['ip_addresses'][0]}/32"
                        elif ipv4_range in nic["ip_addresses"]:
                            ipv4_range = f"{ipv4_range}/32"
                        else:
                            msg = f"NIC for VM {vm_name} has not been found"
                            raise exceptions.NICNotFound(msg)
                        vsphere_uuid = host["associated_objects"]["vmware"][
                            "vsphere_uuid"
                        ]
                        host_name = host["name"]
        elif vmkernel_adapter_name:
            vmk_info, host = vmware.Vsphere.get_vmkernel_info(
                self.client, vmkernel_adapter_name
            )
            if vmk_info:
                if len(vmk_info["ip_addresses"]) == 1 and not ipv4_range:
                    ipv4_range = f"{vmk_info['ip_addresses'][0]}/32"
                elif ipv4_range in vmk_info["ip_addresses"]:
                    ipv4_range = f"{ipv4_range}/32"
                else:
                    msg = (f"VMK {vmkernel_adapter_name} has "
                           "not been found on Host {host_name}")
                    raise exceptions.VMKNotFound(msg)
                vsphere_uuid = host["associated_objects"]["vmware"][
                    "vsphere_uuid"
                ]
                host_name = host["name"]

        if not vsphere_uuid:
            msg = "One of the VMK Adapters or VMs has not been found"
            raise exceptions.HostNotFound(msg)

        return vsphere_uuid, host_name, ipv4_range

    def create_eg(self, **values: dict) -> tuple:
        """create_eg is used to create endpoint group.

        Args:
            description (str): Endpoint Group description.
            type (str, optional): One of:
                - 'layer3'
                - 'layer2'
                - 'firewall'.
                Defaults to 'firewall'
            sub_type (str, optional): One of :
                - 'ip_collection'
                - 'ip_address'.
                Defaults to 'ip_address'.
            endpoints (list): List of Endpoints.

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of if something is changed.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if values.get("endpoints"):
                for eg in values["endpoints"]:
                    if (
                        eg.get(
                            "vm_name",
                        )
                        or eg.get(
                            "vm_tag",
                        )
                        or eg.get(
                            "vmkernel_adapter_name",
                        )
                    ):
                        (
                            eg["vsphere_uuid"],
                            eg["host_name"],
                            eg["ipv4_range"],
                        ) = self._get_vm_detail(**eg)
                    else:
                        eg["ipv4_range"] = eg["ip"]

            if self.existing_eg:
                _message = (f"Endpoint Group with name {self.name} "
                            "already exists. No action taken")
                _status = True
            else:
                if values.get("name"):
                    values.pop("name")
                data = models.PsmEndpointGroups(name=self.name, **values)

                add_request = self.client.post(
                    "endpoint_groups",
                    data=json.dumps(data.dict(exclude_none=True)),
                )

                if add_request.status_code in utils.response_ok:
                    _message = f"Created endpoint group {self.name}"
                    _status = True
                    _changed = True
                elif "already exists" in add_request.json()["result"]:
                    _message = add_request.json()["result"]
                    _status = True
                else:
                    _message = add_request.json()["result"]

        except (
            exceptions.VMNotFound,
            exceptions.NICNotFound,
            exceptions.VMKNotFound,
        ) as exc:
            _message = (f"An exception occurred {exc} while "
                        "creating endpoint group {self.name}")

        return _message, _status, _changed

    def delete_eg(self) -> tuple:
        """delete_eg is used to delete endpoint group.

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_eg:
                delete_request = self.client.delete(
                    f"endpoint_groups/{self.uuid}",
                )

                if delete_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully deleted endpoint group {self.name,}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = delete_request.json()["result"]
            else:
                _message = (f"The endpoint group {self.name,} does not exist. "
                            "No action taken.")
                _status = True

        except (
            exceptions.VMNotFound,
            exceptions.NICNotFound,
            exceptions.VMKNotFound,
        ) as exc:
            _message = (f"An exception occurred {exc} "
                        "while deleting endpoint group {self.name}")

        return _message, _status, _changed
