# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pydantic import ValidationError

from pyafc.common import utils
from pyafc.ports import models, physical
from pyafc.switches import switches


class Lag:
    def __init__(
        self,
        client,
        name: str | None = None,
        switches: list | None = None,
    ) -> None:
        if switches:
            self.switches = switches
        if name:
            self.name = name
        if client:
            self.client = client
        self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details The hidden function helps to check a LAG.

        Returns:
            If found, the UUID is set as a Class attribute.

        """
        lag_request = self.client.get("lags")
        switch_uuid = switches.Switch.get_switch_uuid(
            self.client,
            self.switches,
        )
        if lag_request.json()["result"]:
            for lag in lag_request.json()["result"]:
                if lag["name"] == self.name:
                    for device in lag["port_properties"]:
                        if device["switch_uuid"] == switch_uuid:
                            for item, value in lag.items():
                                setattr(self, item, value)
                            return True
        return False

    @staticmethod
    def configure_lags(client, data: dict) -> tuple:
        """configure_lags function to configure link aggregation group.

        Args:
            lag_name (str) = Name of the LAG
            description (str, optional) = Description of the LAG
            port_properties (list) = Port properties. Check example.
            native_vlan (int, optional) = Native VLAN ID. Default to 1
            tagged (bool, optional): Native VLAN Tagged
            vlan_group_uuids (list, optional) = List of VLAN Groups UUIDs
            ungrouped_vlans (str, optional) = List of VLANs
            lacp_fallback (bool, optional): LACP Fallback enabled
            enable_lossless (bool, optional): Lossless enabled
            lag_id (int, optional): LAG ID
            vlan_mode (str, optional): VLAN Mode
            status (str, optional): Status

        Example:
            lag_data = {
                    "lag_name": "lag10",
                    "lag_id": 10,
                    "ports": [
                        {
                            "switch": "Switch1",
                            "ports": ["1/1/1"],
                        },
                        {
                            "switch": "Switch2",
                            "ports": ["1/1/1"],
                        }],
                    "global_config": {
                        "ungrouped_vlans": "1253-1254",
                        "native_vlan": 1,
                        "lacp_fallback": False,
                    },
                    "lacp_config": {
                        "interval": "fast",
                    },
                }
            ports.PORT.configure_lags(afc_instance.client,
                                      data=lag_data)

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed something.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            data["name"] = data["lag_name"]
            data["lag_number"] = data["lag_id"]
            data["port_properties"] = []

            for device_ports in data["ports"]:
                port_properties = {}
                switch_ip = switches.Switch.consolidate_ip(
                    client,
                    device_ports["switch"],
                )
                switch_uuid = switches.Switch.get_switch_uuid(
                    client,
                    switch_ip,
                )
                if switch_uuid:
                    port_properties["switch_uuid"] = switch_uuid
                    port_properties["port_uuids"] = []
                    for port in device_ports["ports"]:
                        port_instance = physical.Physical(
                            name=port,
                            switches=device_ports["switch"],
                            client=client,
                        )
                        if port_instance.uuid:
                            port_properties["port_uuids"].append(
                                port_instance.uuid,
                            )
                    if data.get("lacp_config"):
                        port_properties["lacp"] = data["lacp_config"]
                    if data.get("speed_config"):
                        port_properties["speed"] = data["speed_config"]
                    port_properties = models.PortProperties(**port_properties)
                    data["port_properties"].append(port_properties.dict())

            data = data | data["global_config"]
            data = models.LAG(**data)

            lag_request = client.post("lags", data=json.dumps(data.dict()))
            if lag_request.status_code in utils.response_ok:
                _message = "Successfully configured LAG as per the input"
                _status = True
                _changed = True
            else:
                _message = lag_request.json()["result"]

        except TypeError as exc:
            _message = f"An exception {exc} occured"
        except ValueError as exc:
            _message = f"An exception {exc} occured"
        except ValidationError as exc:
            _message = f"An exception {exc} occured"

        return _message, _status, _changed

    def __generate_internal_lag(self, data: dict) -> bool:
        """__generate_internal_lag function to create data for internal lag."""
        return models.InternalLAG(**data)
