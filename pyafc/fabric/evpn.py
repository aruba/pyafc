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
                data = data.dict(exclude_none=True)
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
