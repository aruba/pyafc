# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations


from pyafc.common import utils


class Vxlan:
    def __init__(self) -> None:
        pass

    def get_vxlan_tunnels(self, switches: dict | None = None) -> dict:
        """get_vxlan_tunnels Get vxlan tunnel details.

        Args:
            switches (dict): IP address of the switches.

        Returns:
            JSON data of the VXLAN Tunnels.

        """
        uri = f"fabrics/vxlan_tunnels?fabrics={self.uuid}"
        if switches:
            switches_uuid = utils.get_switches_uuid_from_list(
                self.client, switches
            )
            if switches_uuid:
                switches = ",".join(switches_uuid)
            uri += f"&switches={switches}"

        get_request = self.client.get(uri)
        return get_request.json()["result"]

    @staticmethod
    def get_vxlan_tunnels_overall(
        client, switches: dict | None = None, fabrics: dict | None = None
    ) -> dict:
        """get_vxlan_tunnels_overall Get overall VXLAN Tunnel details.

        Args:
            switches (dict): IP address of the switches.

        Returns:
            JSON data of the VXLAN Tunnels.

        """
        uri = "fabrics/vxlan_tunnels"
        if switches:
            switches_uuid = utils.get_switches_uuid_from_list(client, switches)
            if switches_uuid:
                switches = ",".join(switches_uuid)
            uri += f"?switches={switches}"

        get_request = client.get(uri)
        return get_request.json()["result"]
