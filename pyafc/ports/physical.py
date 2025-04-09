# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import utils
from pyafc.switches import switches as sw


class Physical:
    def __init__(self, client, name: str | None, switches: str | None) -> None:
        if switches:
            self.switches = switches
        if name:
            self.name = name
        if client:
            self.client = client
        self.port_label = self.name.replace("/", "%2F")
        switch_instance = sw.Switch(self.client, self.switches)
        self.switch_uuid = switch_instance.uuid
        self.__instantiate_details()

    def __instantiate_details(self) -> None:
        """__instantiate_details hidden function that helps to retrieve UUID.

        Args:
            None

        Returns:
            Class attributes (Any): Port properties are set as class attributes.

        """
        port_request = self.client.get(
            f"ports?port_label={self.port_label}&switches={self.switch_uuid}",
        )
        if port_request.json()["result"]:
            for item, value in port_request.json()["result"][0].items():
                setattr(self, item, value)
            return True
        return False

    def configure_single_physical_port(self, **kwargs: dict) -> bool:
        """configure_single_physical_port function to change single port.

        Args:
            kwargs (dict): Values with which ports need to be configured.

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed something.

        """
        global_change = []
        if self.switch_uuid and self.uuid:
            change_payload = {"uuids": [self.uuid], "patch": []}
            for item, item_value in kwargs.items():
                if item == "speed":
                    item = "speed/configure"
                change_payload["patch"].append(
                    {"path": f"/{item}", "value": item_value, "op": "replace"},
                )
            global_change.append(change_payload)
            port_request = self.client.patch(
                "ports",
                data=json.dumps(global_change),
            )
            return port_request.status_code in utils.response_ok

        return False

    @staticmethod
    def configure_multiple_physical_port(client, devices_list: dict) -> tuple:
        """configure_multiple_physical_port function to configure multi-ports.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            devices_list (list): List of Ports changes. Check Example

        Example:
            update_data = [
                        {
                            "switch": "10.149.1.20",
                            "ports_config": [{
                                "name": "1/1/3",
                                "speed": 10000,
                                }]
                        }
                    ]
            ports.PORT.configure_multiple_physical_port(afc_instance.client,
                                                        update_data)

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed something.

        """
        _message = ""
        _status = False
        _changed = False

        global_change = []

        for switch in devices_list:

            switch_instance = sw.Switch(client, switch["switch"])
            switch_uuid = switch_instance.uuid

            if switch_uuid:
                for port in switch["ports_config"]:
                    port_instance = Physical(
                        name=port["name"],
                        switches=switch["switch"],
                        client=client,
                    )
                    if port_instance.uuid:
                        change_payload = {
                            "uuids": [port_instance.uuid],
                            "patch": [],
                        }
                        del port["name"]
                        for item, item_value in port.items():
                            if item == "speed":
                                item = "speed/configure"
                            change_payload["patch"].append(
                                {
                                    "path": f"/{item}",
                                    "value": item_value,
                                    "op": "replace",
                                },
                            )
                        global_change.append(change_payload)

        if len(global_change) > 0:
            port_request = client.patch(
                "ports", data=json.dumps(global_change),
            )

            if port_request.status_code in utils.response_ok:
                _message = "Successfully configured ports according to input"
                _status = True
                _changed = True
            else:
                _message = port_request.json()["result"]

        else:
            _message = "Nothing to configure"

        return _message, _status, _changed
