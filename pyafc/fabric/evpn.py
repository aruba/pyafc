# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

import json

from pydantic import ValidationError

from pyafc.common import utils
from pyafc.fabric import models
from pyafc.services import resource_pools


class EVPN:
    def __init__(self) -> None:
        pass

    def get_multisite(self) -> dict:
        """get_multisite is used to get multisite EVPN.

        Returns:
            multi_site VPN data (dict): Multi-site EVPN data.

        """
        get_request = self.client.get("evpn/multi_site")
        return get_request.json()["result"]

    def get_evpns(self) -> dict:
        """get_evpns is used to get EVPNs.

        Returns:
            evpn data (dict): EVPN data.

        """
        get_request = self.client.get("evpn")
        return get_request.json()["result"]

    def create_evpn(self, **kwargs: dict) -> tuple:
        """create_evpn is used to create EVPN.

        Args:
            name_prefix (str): Name of the EVPN workflow
            description (str): Description
            rt_type (str, optional): One of :
                - 'AUTO'
                - 'ASN:VNI'
                - 'ASN:VLAN'
                - 'ASN:NN'
                Defaults to 'AUTO'
            as_number (str, optional): AS Number. Required based on
                selected rt_type.
            vni_base (int): Base VNI for L2VIN creation
            vlans (str): VLANs to be mapped to EVPN
            switches (str, optional): List of switches to apply EVPN.
                If not specified, will be applied on the entire Fabric.
            system_mac_range (str): MAC Range used for Virtual MAC.

        Example:
            fabric_instance.create_evpn(name='EVPN',
                                        'as_number': '65000',
                                        'rt_type': 'ASN:VLAN',
                                        'system_mac_range': 'My MAC Pool',
                                        'vlans': '100-101',
                                        'vni_base': 10000)

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed something.

        """
        _status = False
        _changed = False
        _message = ""

        try:
            mac_pool = resource_pools.Pool.get_resource_pool(
                self.client,
                kwargs["system_mac_range"],
                "MAC",
            )
            if isinstance(mac_pool, dict) and "uuid" in mac_pool:
                kwargs["system_mac_range"] = mac_pool["uuid"]
                if "fabric_uuid" not in kwargs:
                    kwargs["fabric_uuid"] = self.uuid
                else:
                    _message = "Fabric not found"
                    return _message, _status, _changed

                if kwargs.get("switches"):
                    switches_uuid_list = utils.consolidate_switches_list(
                        self.client,
                        kwargs["switches"],
                    )
                    kwargs["switch_uuids"] = switches_uuid_list

                data = models.EVPN(**kwargs)
                data = data.model_dump(exclude_none=True)
                if "description" in kwargs and kwargs["description"] != "":
                    data["description"] = kwargs["description"]
                else:
                    data["description"] = ""
                existing_evpn = self.client.get("evpn").json()["result"]
                evpn_exists = False
                for evpn in existing_evpn:
                    if kwargs["name"] in evpn["name"]:
                        evpn_exists = True
                if evpn_exists:
                    _message = f"EVPN {kwargs['name']} already exists.\
                        No action taken"
                    _status = True
                else:
                    evpn_request = self.client.post(
                        "evpn",
                        data=json.dumps(data),
                    )
                    if evpn_request.status_code in utils.response_ok:
                        _message = (f"EVPN {kwargs['name']} created "
                                    "successfully")
                        _status = True
                        _changed = True
                    else:
                        _message = evpn_request.json()["result"]
            else:
                _message = ("MAC POOL with ID "
                            f"{kwargs['system_mac_range']} not found")
        except ValidationError as exc:
            _message = f"Faced a ValidationError {exc}"
        return _message, _status, _changed

    def delete_evpn(self, name: str) -> tuple:
        """delete_evpn is used to delete EVPN.

        Args:
            name (str): EVPN Name.

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed something.

        """
        _status = False
        _changed = False
        _message = ""

        try:
            evpn_list = self.get_evpns()
            filtered_evpn_list = [
                evpn
                for evpn in evpn_list
                if "name" in evpn and name in evpn["name"]
            ]
            if len(filtered_evpn_list) == 0:
                _message = (f"Input EVPN {name} does not exist. "
                            "No action taken.")
                _status = True
            elif len(filtered_evpn_list) == 1:
                evpn_delete_request = self.client.delete(
                    f"evpn/{filtered_evpn_list[0]['uuid']}",
                )
                if evpn_delete_request.status_code in utils.response_ok:
                    _message = ("Successfully deleted evpn "
                                f"{filtered_evpn_list[0]['name']}")
                    _status = True
                    _changed = True
                else:
                    _message = ("Encountered error while deleting EVPN "
                                f"{filtered_evpn_list[0]['name']}")
            else:
                _message = []
                for evpn in filtered_evpn_list:
                    evpn_delete_request = self.client.delete(
                        f"evpn/{evpn['uuid']}",
                    )
                    if evpn_delete_request.status_code in utils.response_ok:
                        _message.append(
                            f"Successfully deleted evpn {evpn['name']}",
                        )
                        _status = True
                        _changed = True
                    else:
                        if len(_message) != 0 and "Successfully" in _message:
                            _changed = True
                            _status = True
                        _message.append(
                            ("Encountered error while deleting "
                             f"EVPN {evpn['name']}"),
                        )
        except ValidationError as exc:
            _message = f"Faced a ValidationError {exc}"

        return _message, _status, _changed

    def get_evpn_settings(self) -> dict | bool:
        """get_evpn_settings Get the global EVPN Settings of the Fabric.

        Returns:
            evpn settings data (dict): Global EVPN Settings of the Fabric,
                or False if no settings are found for the Fabric.

        """
        settings_request = self.client.get("evpn/settings")
        for settings in settings_request.json()["result"]:
            if settings.get("fabric_uuid") == self.uuid:
                return settings
        return False

    def update_evpn_settings(self, **kwargs: dict) -> tuple:
        """update_evpn_settings Update the global EVPN Settings of the Fabric.

        Args:
            arp_suppression (bool): Enable or disable ARP suppression.
            local_svi (bool, optional): Enable or disable local SVI.
            local_mac (bool, optional): Enable or disable local MAC.
            vxlan_tunnel_bridging_mode (str, optional): One of :
                - 'ibgp-ebgp'
                - 'no-bridging'
            switches (list, optional): List of switches on which to apply the
                settings. If not specified, settings apply to the whole Fabric.

        Example:
            fabric_instance.update_evpn_settings(
                arp_suppression=True,
                local_svi=True,
                local_mac=True,
                vxlan_tunnel_bridging_mode='ibgp-ebgp',
            )

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true if action has changed something.

        """
        _status = False
        _changed = False
        _message = ""

        try:
            current_settings = self.get_evpn_settings()
            if not current_settings:
                _message = (
                    f"EVPN Settings not found for fabric {self.name}. "
                    "No action taken."
                )
                return _message, _status, _changed

            if kwargs.get("switches"):
                kwargs["switch_uuids"] = utils.consolidate_switches_list(
                    self.client,
                    kwargs["switches"],
                )
                del kwargs["switches"]

            comparable_fields = [
                "arp_suppression",
                "local_svi",
                "local_mac",
                "vxlan_tunnel_bridging_mode",
            ]
            change_required = any(
                field in kwargs
                and kwargs[field] != current_settings.get(field)
                for field in comparable_fields
            )

            if not change_required and not kwargs.get("switch_uuids"):
                _message = (
                    f"EVPN Settings for fabric {self.name} are already "
                    "up to date. No action taken."
                )
                _status = True
                return _message, _status, _changed

            model_kwargs = {
                "arp_suppression": kwargs.get(
                    "arp_suppression",
                    current_settings.get("arp_suppression", False),
                ),
                "local_svi": kwargs.get(
                    "local_svi",
                    current_settings.get("local_svi"),
                ),
                "local_mac": kwargs.get(
                    "local_mac",
                    current_settings.get("local_mac"),
                ),
                "vxlan_tunnel_bridging_mode": kwargs.get(
                    "vxlan_tunnel_bridging_mode",
                    current_settings.get("vxlan_tunnel_bridging_mode"),
                ),
            }
            # AFC requires exactly one of 'switch_uuids' (per-switch) or
            # 'fabric_uuid' (fabric-wide) - never both.
            if kwargs.get("switch_uuids"):
                model_kwargs["switch_uuids"] = kwargs["switch_uuids"]
            else:
                model_kwargs["fabric_uuid"] = self.uuid

            data = models.EVPNSettings(**model_kwargs)
            update_request = self.client.put(
                "evpn/settings",
                data=json.dumps(data.model_dump(exclude_none=True)),
            )
            if update_request.status_code in utils.response_ok:
                _message = (
                    f"Successfully updated EVPN Settings for fabric "
                    f"{self.name}"
                )
                _status = True
                _changed = True
            else:
                _message = update_request.json()["result"]
        except ValidationError as exc:
            _message = f"Faced a ValidationError {exc}"

        return _message, _status, _changed
