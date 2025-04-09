# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0



class PVLAN:
    def __init__(self) -> None:
        pass

    def get_pvlan(self) -> dict:
        """get_pvlan Get PVLAN details for that Fabric.

        Returns:
            PVLAN Object details in JSON format.

        """
        get_request = self.client.get(f"fabrics/{self.uuid}/pvlans")
        return get_request.json()["result"]

    @staticmethod
    def get_pvlan_overall(
        client
    ) -> dict:
        """get_pvlan_overall Get overall PVLAN details.

        Returns:
            PVLAN Object details in JSON format.

        """
        get_request = client.get("fabrics/pvlans")
        return get_request.json()["result"]
