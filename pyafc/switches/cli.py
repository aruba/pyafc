# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Utility functions and classes for Switch management.

This module provides:
- get_switch_details: Get VRF UUID;
- get_switch_uuid: Get IP Interfaces for the specified VRF
- get_ip_interface: Get IP Interface for the specified VRF
- create_vrf: create a VRF.
- delete_vrf: delete a VRF.
- reapply_vrf: Reapply VRF.
"""

import json

from httpx import Client

from pyafc.common import utils
from pyafc.switches import models


class CLI:
    """Switch Class representing a Switch.

    Attributes:
        client (Any): Client instance to Connect and Authenticate on AFC.

    """

    def __init__(self, client: Client) -> None:
        """__init__ Init Method.

        Args:
            client (Client): Client instance to Connect and Authenticate.

        Returns:
            Returns the AFC Connection object/client.

        """
        self.client = client

    def send_cli(self, data: dict) -> tuple:
        """send_cli Send CLI commands.

        Args:
            switches (list): List of switches to send command to
            commands (list): List of commands to send to switches

        Returns:
            Command outputs are set as the class attribute cli_outputs.

        """
        _status = False
        _message = ""
        _changed = False

        data["switch_uuids"] = utils.consolidate_switches_list(
            self.client,
            data["switches"],
        )

        if False in data["switch_uuids"]:
            _message = "One of the devices is not known by the AFC instance"
            return _message, _status, _changed

        payload = models.CLI(**data)

        send_request = self.client.post(
            "switches/cli_commands",
            data=json.dumps(payload.dict()),
        )

        if send_request.status_code in utils.response_ok:
            _status = True
            _changed = True

        _message = send_request.json()["result"]

        return _message, _status, _changed
