# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from pyafc.common import exceptions


class vSwitch:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_vswitch_uuid(client, name: str) -> dict:
        """get_vswitch_uuid Get vswitch UUID.

        Args:
            name (str): vSwitch name.

        Returns:
            vSwitch UUID.

        """
        hosts_uri = "hosts?all_data=true"
        hosts_request = client.get(hosts_uri)

        for host in hosts_request.json()["result"]:
            for vswitch in host["vswitches"]:
                if vswitch["name"] == name:
                    return vswitch["associated_objects"]["vmware"]["uuid"]

        msg = f"vSwitch {name} not found"
        raise exceptions.vSwitchNotFound(msg)

    @staticmethod
    def get_pg_uuid(client, name: str) -> str:
        """get_pg_uuid Get Port Group UUID.

        Args:
            name (str): Port Group name.

        Returns:
            Port Group UUID.

        """
        hosts_uri = "hosts?all_data=true"
        hosts_request = client.get(hosts_uri)

        for host in hosts_request.json()["result"]:
            for vswitch in host["vswitches"]:
                if (
                    vswitch.get("associated_objects")
                    and vswitch["associated_objects"].get("vmware")
                    and vswitch["associated_objects"]["vmware"].get(
                        "portgroups"
                    )
                ):
                    for pg in vswitch["associated_objects"]["vmware"][
                        "portgroups"
                    ]:
                        if pg["name"] == name:
                            return pg["uuid"]

        msg = f"Port Group {name} not found"
        raise exceptions.PortGroupNotFound(msg)
