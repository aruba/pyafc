# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

import json
import time

from pydantic import ValidationError

from pyafc.common import utils
from pyafc.common.internal import Internal
from pyafc.fabric import models
from pyafc.services import resource_pools


class VSX(Internal):

    def __init__(self) -> None:
        pass

    def get_vsx(self) -> dict:
        """get_vsx is used to get VSX Configuration.

        Returns:
            vsc config (dict): Dict of VSX data.

        """
        get_request = self.client.get(f"fabrics/{self.uuid}/vsx")
        return get_request.json()["result"]

    @staticmethod
    def check_vsx_membership(
        client,
        fabric_uuid: str,
        device_uuid: str,
    ) -> list:
        """create_vsx Creates VSX configuration.

        Args:
            client (Any): Client instance to Connect on AFC.
            fabric_uuid (dict): Fabric UUID.
            device_uuid (dict): Fabric UUID.

        Returns:
            vsx_information (tuple): VSX Information.

        """
        vsx_found = False

        vsx_information = {"vsx_uuid": "", "vsx_members": []}

        uri_vsx_fabric = f"fabrics/{fabric_uuid}/vsx"

        vsx_request = client.get(uri_vsx_fabric)

        for pair in vsx_request.json()["result"]:
            for peer in pair["vsx_peers"]:
                if peer["switch_uuid"] == device_uuid:
                    vsx_information["vsx_uuid"] = pair["uuid"]
                    vsx_found = True
                    break

        if vsx_found:
            uri_vsx_fabric = (
                f"fabrics/{fabric_uuid}/vsx/{vsx_information['vsx_uuid']}"
            )

            vsx_request = client.get(uri_vsx_fabric)

            for peer in vsx_request.json()["result"]["vsx_peers"]:
                vsx_information["vsx_members"].append(peer["switch_uuid"])

        return vsx_information

    def create_vsx(self, **kwargs: dict) -> tuple:
        """create_vsx Creates VSX configuration.

        Summary:
            Only automated way of configuration is supported.

        Args:
            name (str): Name of the VSX Configuration.
            system_mac_range (str): Name of the MAC Pool used to
                configure System MAC
            keepalive_ip_pool_range (str): Name of the MAC Pool used to
                configure System MAC
            keep_alive_interface_mode (str, optional): One of:
                - 'routed'
                - 'loopback'
                Defaults to 'routed'

        Example:
            fabric_instance.create_vsx(name="Sense_VSX",
                                       system_mac_range="Sense MAC Pool",
                                       keepalive_ip_pool_range="DC1 Underlay IP",
                                       keep_alive_interface_mode="routed"
                                       )

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if not self.uuid:
                _message = "Fabric does not exist. No action taken"
                return _message, _status, _changed

            mac_pool = resource_pools.Pool.get_resource_pool(
                self.client, kwargs["system_mac_range"], "MAC",
            )
            if not mac_pool:
                _message = f'{kwargs["system_mac_range"]} does not exist'
                return _message, _status, _changed
            kwargs["system_mac_range"] = mac_pool["uuid"]

            ipv4_pool = resource_pools.Pool.get_resource_pool(
                self.client, kwargs["keepalive_ip_pool_range"], "IPv4",
            )
            if not ipv4_pool:
                _message = (
                    f'{kwargs["keepalive_ip_pool_range"]} does not exist'
                )
                return _message, _status, _changed
            kwargs["keepalive_ip_pool_range"] = ipv4_pool["uuid"]

            data = models.Vsx(**kwargs)
            data = data.dict(exclude_none=True)

            existing_vsx = self.get_vsx()

            if len(existing_vsx) != 0 and kwargs["name"] in existing_vsx[0]["name"]:
                _message = (
                    "The VSX configuration already exists. No action taken"
                )
                _status = True
            else:
                url_vsx = f"fabrics/{self.uuid}/vsxes"
                vsx_request = self.client.post(
                    url_vsx,
                    data=json.dumps(data),
                )
                if (
                    "Minimum two ports required if KA interface mode is P2P"
                    in vsx_request.json()["result"]
                    or "No new VSX Pairs found" in vsx_request.json()["result"]
                ):
                    repetition = 0
                    while (
                        vsx_request.status_code not in utils.response_ok
                        and repetition < 10  # noqa: PLR2004
                    ):
                        time.sleep(2)
                        vsx_request = self.client.post(
                            url_vsx,
                            data=json.dumps(data),
                        )
                        repetition += 1
                if (
                    vsx_request.status_code in utils.response_ok
                    or "No new VSX Pairs found" in vsx_request.json()["result"]
                ):
                    _message = (
                        "Successfully applied VSX configuration"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = vsx_request.json()["result"]

        except ValidationError as exc:
            _message = f"An exception {exc} occurred while configuring VSX"

        return _message, _status, _changed

    def reapply_vsx(self) -> tuple:
        """reapply_vsx Reapplies VSX configuration to new devices.

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            data = {}
            try:
                data["fabric_uuids"] = [self.uuid]
            except:  # noqa: E722
                _message = "Fabric does not exist"
                return _message, _status, _changed

            url_vsx = "fabrics/vsxes/reapply"
            vsx_request = self.client.post(
                url_vsx,
                data=json.dumps(data),
            )
            if (
                "Minimum two ports required if KA interface mode is P2P"
                in vsx_request.json()["result"]
                or "No new VSX Pairs found" in vsx_request.json()["result"]
            ):
                repetition = 0
                while (
                    vsx_request.status_code not in utils.response_ok
                    and repetition < 10  # noqa: PLR2004
                ):
                    time.sleep(2)
                    vsx_request = self.client.post(
                        url_vsx,
                        data=json.dumps(data),
                    )
                    repetition += 1
            if (
                vsx_request.status_code in utils.response_ok
                or "No new VSX Pairs found" in vsx_request.json()["result"]
            ):
                _message = (
                    "Successfully applied VSX configuration"
                )
                _status = True
                _changed = True
            else:
                _message = vsx_request.json()["result"]

        except ValidationError as exc:
            _message = f"An exception {exc} occurred while configuring VSX"

        return _message, _status, _changed
