# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import exceptions, utils
from pyafc.integrations import models


class Vsphere:
    def __init__(self) -> None:
        pass

    def get_hosts(self) -> dict:
        """get_hosts Get hosts.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.

        Returns:
            Hosts list from the integration.

        """
        get_request = self.client.get("hosts")
        return get_request.json()["result"]

    @staticmethod
    def get_vm_info(client, vm_name: str | None, vm_tag: str | None) -> tuple:
        """get_vm_info Get VM Information.

        Args:
            vm_name (str, optional): Name of the VM to get the info.
            vnic_name (str, optional): Name of the vNIC.
            vm_tag (str, optional): VM Tag.

        Returns:
            VM Information in JSON format.

        """
        hosts_uri = "hosts?all_data=true"
        hosts_request = client.get(hosts_uri)

        vm_tag = vm_tag if vm_tag else []

        for host in hosts_request.json()["result"]:
            if vm_name and host["associated_objects"].get("vmware"):
                for vm in host["vms"]:
                    new_vm = False
                    if vm_tag:
                        if vm_tag in vm["infrastructure_tags"]:
                            new_vm = vm
                    else:
                        new_vm = vm

                    if new_vm and vm_name == new_vm["name"]:
                        return new_vm, host

        msg = f"VM {vm_name} has not been found"
        raise exceptions.VMNotFound(msg)

    @staticmethod
    def get_vmkernel_info(
        client,
        vmkernel_adapter_name: str | None,
        host_name: str | None,
    ) -> tuple:
        """get_vmkernel_info Get VM Information.

        Args:
            vmkernel_adapter_name (str): Name of the VM Kernel adapter.
            host_name (str): Name of the host.

        Returns:
            VM Kernel Information in JSON format.

        """
        hosts_uri = "hosts?all_data=true"
        hosts_request = client.get(hosts_uri)

        for host in hosts_request.json()["result"]:
            if host["name"] == host_name:
                for vmk in host["vmkernel_adapters"]:
                    if vmk["name"] == vmkernel_adapter_name:
                        return vmk, host

        msg = f"VM Kernel {vmkernel_adapter_name} not found"
        raise exceptions.VMKNotFound(
            msg,
        )

    def create_vmware_vsphere(self, **kwargs: dict) -> tuple:
        """create_vmware_vsphere Create VMWare integration.

        Args:
            name (str) = Integration's name
            description (str) = Integration's description
            host (str) = vCenter's IP Address
            username (str) = vCenter's Username
            password (str) = vCenter's Password
            enabled (bool, optional) = Integration enabled
            verify_ssl (bool, optional) = Indicates whether SSL/TLS
                certificates should be validated when connecting to
                the VMware vSphere system.
                Defaults to False
            auto_discovery (bool, optional) = Indicates whether LLDP/Advertise
                should be enabled on all Distributed vSwitches and
                CDP/Advertise should be enabled on all Standard vSwitches.
                Defaults to True
            storage_optimization (bool, optional) = Indicates if vSAN network
                traffic will be optimized through the use of policies.
                Defaults to False
            use_cdp (bool, optional) = Indicates whether CDP should be used
                instead of LLDP as the Discovery Protocol for Distributed
                vSwitches.
                Defaults to False
            downlink_vlan_provisioning (bool, optional) = Indicates whether
                VLANs will be automatically provisioned for downlink switches.
                Defaults to False
            downlink_vlan_range (str, optional) = No actions will be taken on
                VLANs outside this range.
                Defaults to None
            vlan_provisioning (bool, optional) = Indicates whether VLANs will
                be automatically provisioned.
                Defaults to False
            vlan_range (str, optional) = No actions will be taken on VLANs
                outside this range.
                Defaults to None
            pvlan_provisioning (bool, optional) = Indicates whether Private
                VLANs will be automatically provisioned.
                Defaults to False
            pvlan_range (str, optional) = No actions will be taken on VLANs
                outside this range.
                Default to None
            endpoint_group_provisioning (bool, optional) = Indicates whether
                auto creation of Endpoint group based on VM tags is enabled.
                Defaults to False
            cumulative_epg_provisioning (bool, optional) = Indicates whether
                auto creation of Cumulative endpoint group based on VM
                tags is enabled.
                Defaults to False

        Example:
            vmw_data = {
                "name": "vSphere",
                "host": "10.14.120.51",
                "username": "<username>",
                "password": "<password>",
                "description": "",
                "enabled": True,
                "verify_ssl": False,
                "auto_discovery": True,
                "vlan_provisioning": True,
                "pvlan_provisioning": True,
                "downlink_vlan_range": "1-4094",
                "vlan_range": "1-4094",
                "pvlan_range": "1-4094",
                "use_cdp": False,
                "downlink_vlan_provisioning": False,
                "storage_optimization": False,
                "endpoint_group_provisioning": True,
                }

            integration_instance.create_vmware_vsphere(**vmw_data)

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        data = models.vSphere(**kwargs)

        add_request = self.client.post(
            "vmware/vcenters",
            data=json.dumps(data.dict(exclude_none=True)),
        )

        if add_request.status_code in utils.response_ok:
            _message = "Successfully configured the VMWare integration"
            _status = True
            _changed = True
        else:
            if "already exists" in add_request.json()["result"]:
                _status = True
            _message = f"{add_request.json()['result']}"

        return _message, _status, _changed
