# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pydantic import ValidationError

from pyafc.common import exceptions, utils
from pyafc.fabric import fabric, models, vsx
from pyafc.vrf import vrf


class MultiFabrics:
    def __init__(self) -> None:
        pass

    def get_multifabrics(
        self,
    ) -> dict:
        """get_multifabrics Get multi hop vxlan details.

        Returns:
            The object details in JSON format.

        """
        get_request = self.client.get(f"fabrics/{self.uuid}/multi_hop_vxlan")
        return get_request.json()["result"]

    @staticmethod
    def get_multifabrics_overall(client):
        """get_multifabrics_overall Get overall multi hop vxlan details.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.

        Returns:
            The object details in JSON format.

        """
        get_request = client.get("fabrics/multi_hop_vxlan")
        return get_request.json()["result"]

    def __generate_remote_values(self, values: dict) -> dict | bool:
        """__generate_remote_values Hidden function to generate remote UUID.

        Args:
            values (dict): Dictionary containing the names of components

        Returns:
            Returns the updated values

        """
        try:

            fabric_instance = fabric.Fabric(self.client, name=values["fabric"])
            if not fabric_instance.uuid:
                raise exceptions.FabricNotFound
            values["fabric_uuid"] = fabric_instance.uuid

            border_uuid = utils.consolidate_switches_list(
                self.client,
                values["border_leader"],
            )
            if not border_uuid:
                raise exceptions.NoDeviceFound

            vsx_information = vsx.VSX.check_vsx_membership(
                self.client,
                fabric_instance.uuid,
                border_uuid[0],
            )
            values["border_leader_uuid"] = (
                vsx_information["vsx_uuid"]
                if vsx_information["vsx_uuid"]
                else border_uuid[0]
            )

            vrf_uuid = vrf.Vrf.get_vrf_uuid(
                self.client, name="default", fabric=fabric_instance.uuid,
            )
            bgp_request = self.client.get(
                f"vrfs/{vrf_uuid}/bgp/{border_uuid[0]}",
            )
            values["asn"] = bgp_request.json()["result"]["as_number"]

            intf_request = self.client.get(f"vrfs/{vrf_uuid}/ip_interfaces")
            if vsx_information["vsx_uuid"]:
                for intf in intf_request.json()["result"]:
                    if (
                        intf["name"] == values["peering_ip"]
                        and intf["switch_uuid"]
                        == vsx_information["vsx_members"][0]
                    ):
                        values["ipv4_address_A"] = intf[
                            "ipv4_primary_address"
                        ]["address"]
                        break
                for intf in intf_request.json()["result"]:
                    if (
                        intf["name"] == values["peering_ip"]
                        and intf["switch_uuid"]
                        == vsx_information["vsx_members"][1]
                    ):
                        values["ipv4_address_B"] = intf[
                            "ipv4_primary_address"
                        ]["address"]
                        break
            else:
                for intf in intf_request.json()["result"]:
                    if (
                        intf["name"] == values["peering_ip"]
                        and intf["switch_uuid"] == border_uuid[0]
                    ):
                        values["ipv4_address_A"] = intf[
                            "ipv4_primary_address"
                        ]["address"]
                        break

            return values

        except TypeError:
            return False

    def create_multi_fabrics(self, name: str, **kwargs: dict) -> tuple:
        """create_multi_fabrics Create multifabric configuraiton.

        Args:
            name (str): Name of the Multifabric configuration.
            description (str): Description
            border_leader (str): Border Leader name or IP Address
            l3_ebgp_borders (list): List of eBGP Borders
            remote_fabrics (list): List of Remote Fabrics
            bgp_auth_password (str): BGP Authentication password
            uplink_to_uplink (bool): Enable the Uplink to Uplink Capability
                on Aruba 10000.
                Defaults to False

        Example:
            fabric_instance.create_multi_fabrics(name="DC2-MF",
                                                border_leader="10.149.1.20",
                                                remote_fabrics=[
                                                    {
                                                    "fabric": "Sense-DC1",
                                                    "border_leader": "10.149.2.100",
                                                    "peering_ip": "loopback0",
                                                    },
                                                    ])

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            border_uuid = utils.consolidate_switches_list(
                self.client,
                kwargs["border_leader"],
            )
            if not border_uuid:
                raise exceptions.NoDeviceFound
            vsx_information = vsx.VSX.check_vsx_membership(
                self.client,
                self.uuid,
                border_uuid[0],
            )

            kwargs["border_leader"] = (
                vsx_information["vsx_uuid"]
                if vsx_information["vsx_uuid"]
                else border_uuid[0]
            )
            kwargs["l3_ebgp_borders"] = (
                vsx_information["vsx_members"]
                if vsx_information["vsx_members"]
                else [border_uuid[0]]
            )

            remote_fabrics = []
            for remote in kwargs["remote_fabrics"]:
                remote_fabric_values = self.__generate_remote_values(remote)
                if not remote_fabric_values:
                    raise exceptions.NoBGPonRemoteBorderException
                remote_fabrics.append(remote_fabric_values)
            kwargs["remote_fabrics"] = remote_fabrics

            data = models.MultiFabrics(name=name, **kwargs)
            data.uplink_to_uplink = None

            uri_multi_fabrics = f"fabrics/{self.uuid}/multi_hop_vxlan"

            multi_fabrics_request = self.client.post(
                uri_multi_fabrics,
                data=json.dumps(data.dict(exclude_none=True)),
            )

            if multi_fabrics_request.status_code in utils.response_ok:
                _message = "Successfully created MultFabrics configuration"
                _status = True
                _changed = True
            else:
                if "already exists" in multi_fabrics_request.json()["result"]:
                    _status = True
                _message = multi_fabrics_request.json()["result"]
        except exceptions.NoDeviceFound:
            _message = "Border not found"
        except exceptions.NoBGPonRemoteBorderException:
            _message = "BGP is not configured on remote Border"
        except ValidationError as exc:
            _message = exc

        return _message, _status, _changed

    def create_vlan_stretching(self, **kwargs: dict) -> tuple:
        """create_vlan_stretching Creates VLAN stretching configuration.

        Args:
            stretched_vlans (str): VLANs to be stretched
            global_route_targets (list): List of Global RTs. Check examples

        Example:
            fabric_instance.create_vlan_stretching(fabrics=[
                                                        "Sense-DC1",
                                                        "Sense-DC2",
                                                    ],
                                                    stretched_vlans="100-101",
                                                    global_route_targets=[
                                                        {
                                                        "rt_type": "NN:VLAN",
                                                        "administrative_number": 1,
                                                        },
                                                    ],
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
            kwargs = utils.populate_list_fabrics_switches(self.client, kwargs)

            data = models.VLANStretching(**kwargs)
            uri_stretching = "/evpn/multi_site"
            stretching_request = self.client.post(
                uri_stretching,
                data=json.dumps(data.dict()),
            )

            if stretching_request.status_code in utils.response_ok:
                _message = "Successfully created VLAN stretching"
                _status = True
                _changed = True
            elif "already" in stretching_request.json()["result"]:
                _message = "VLAN already stretched"
                _status = True
            else:
                _message = stretching_request.json()["result"]

        except ValidationError as exc:
            _message = exc

        return _message, _status, _changed
