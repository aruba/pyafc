# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.integrations import psm, vmware


class Integration(vmware.Vsphere, psm.Psm):
    def __init__(self, client) -> None:
        self.client = client

    def get_integrations(
        self
    ) -> dict:
        """get_integrations Get available integrations.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.

        Returns:
            integraion data (dict): All the available integrations in JSON.

        """
        get_request = self.client.get("integrations")
        return get_request.json()["result"]
