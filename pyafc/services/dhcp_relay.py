# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import exceptions, utils
from pyafc.services import models


class DhcpRelay:
    def __init__(self, client, name: str, **kwargs: dict) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the DHCP Relay.

        Returns:
            existing_eg (bool): True if available, False if not.

        """
        self.client = client
        self.uuid = None
        self.name = name
        self.existing_dr = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details hidden function that helps to retrieve UUID.

        Returns:
            Class attributes (Any): DHCP Relay props are set as class attribs.

        """
        dhcp_relay_request = self.client.get("dhcp_relay")
        for relay in dhcp_relay_request.json()["result"]:
            if relay["name"] == self.name:
                self.uuid = relay["uuid"]
                for item, value in relay.items():
                    setattr(self, item, value)
                return True
        return False

    @staticmethod
    def get_dhcp_relay(client, name: str) -> dict | bool:
        """get_dhcp_relay Get existing dhcp relay config.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the dhcp relay configuration.

        Returns:
            JSON data of the DHCP relay config if exists, else False.

        """
        dhcp_relay_request = client.get("dhcp_relay")

        for relay in dhcp_relay_request.json()["result"]:
            if relay["name"] == name:
                return relay
        return False

    def create_dhcp_relay(self, **values: dict) -> tuple:
        """create_dhcp_relay Creates a DHCP Relay.

        Args:
            description (str) = Description
            vlans (str) = Set or range of VLANs
            gateway_address (str, optional) = BOOTP-Gateway Address
            ipv4_dhcp_server_addresses (list, optional) = List of DHCP Servers
                                                IPv4 Addresses
            ipv6_dhcp_server_addresses (list, optional) = List of DHCP Servers
                                                IPv6 Addresses
            ipv6_dhcp_mcast_server_addresses (list, optional) = List of DHCP
                Servers IPv6 MCAST Addresses
            v4relay_option82_policy (str, optional) = One of
                - 'replace'
                - 'drop'
                - 'keep'
                Defaults to 'replace'
            v4relay_option82_validation (bool, optional) = Enable DHCP-Relay
                Option 82 validation
            v4relay_source_interface (bool, optional) = Use configured
                source-interface, suboption-5, and suboption-11
                in DHCP-Relay Option 82
            fabrics (list, optional) = List of Fabrics
            switches (list, optional) = List of Switches

        Example:
            dhcpr_data = {
                "fabrics": ["DC1"],
                "vlans": "252",
                "ipv4_dhcp_server_addresses": ["1.2.3.4"]
            }

            dhcp_relay_instance = dhcp_relay.DhcpRelay(afc_instance.client, name="New_DHCP_Relay")
            dhcp_relay_instance.create_dhcp_relay(**dhcpr_data,)

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_dr:
                _message = (
                    f"The DHCP Relay configuration "
                    f"{self.name} already exists. No action taken."
                )
                _status = True
            else:
                values = utils.populate_list_fabrics_switches(
                    self.client,
                    values,
                )

                if "name" in values:
                    del values["name"]

                data = models.DhcpRelay(name=self.name, **values)

                add_request = self.client.post(
                    "dhcp_relay",
                    data=json.dumps(data.dict(exclude_none=True)),
                )
                if add_request.status_code in utils.response_ok:
                    _message = f"Successfully applied DHCP Relay {self.name}"
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]
        except exceptions.NoDeviceFound as exc:
            _message = f"Device {exc} not found - No action Taken"
        except Exception as exc:
            _message = exc

        return _message, _status, _changed

    def delete_dhcp_relay(self) -> tuple:
        """delete_dhcp_relay Deletes a DHCP Relay.

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_dr:
                delete_request = self.client.delete(f"dhcp_relay/{self.uuid}")

                if delete_request.status_code in utils.response_ok:
                    _message = f"Successfully deleted DHCP Relay {self.name}"
                    _status = True
                    _changed = True
                else:
                    _message = delete_request.json()["result"]

            else:
                _message = (
                    f"The DHCP Relay configuration {self.name} "
                    "does not exist. No action taken."
                )
                _status = True

        except Exception:
            _message = (
                f"An exception occurred while deleting "
                f"DHCP Relay {self.name}"
            )

        return _message, _status, _changed
