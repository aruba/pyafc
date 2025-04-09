# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

from typing import Literal

from pyafc.ports import lag, physical


class PORT(physical.Physical, lag.Lag):
    def __init__(
        self,
        client,
        port_type: Literal["physical", "lag"],
        name: str,
        switches: str | None,
    ) -> None:
        self.client = client
        self.switches = switches
        self.name = name
        if port_type == "physical":
            physical.Physical.__init__(self)
        if port_type == "lag":
            lag.Lag.__init__(self)

    @staticmethod
    def get_port_uuid(client, fabric: str, device: str, name: str) -> str:
        """get_port_uuid Get Port UUID.

        Args:
            fabric (str): Fabric name.
            device (str): Switch IP.
            name (str): port name.

        Returns:
            Port UUID.

        """
