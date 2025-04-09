# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pydantic import ValidationError

from pyafc.common import utils
from pyafc.fabric import models
from pyafc.services import resource_pools


class LS:
    def __init__(self) -> None:
        pass

    def get_subleaf(self) -> dict:
        """get_subleaf is used to get specific subleaf configuration.

        Returns:
            subleaf data (dict): Specific subleaf configuration data.

        """
        get_request = self.client.get(f"fabrics/{self.uuid}/subleaf_leaf")
        return get_request.json()["result"]

    @staticmethod
    def get_subleaf_overall(client) -> dict:
        """get_subleaf is used to get overall subleaf configuration.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.

        Returns:
            subleaf data (dict): Overall subleaf configuration data.

        """
        get_request = client.get("fabrics/subleaf_leaf")
        return get_request.json()["result"]

    def create_l3ls(self, name: str, **kwargs: dict) -> tuple:
        """create_l3ls creates leaf-spine configuration.

        Args:
            name (str): leap-spine configuration name
            description (str, optional): Description
            pool_ranges (str): Name of the IP Pool range used to
                configure IP Interfaces

        Example:
            fabric_instance.create_l3ls('name': 'DC1_l3ls',
                                        'pool_ranges': 'DC1 Underlay IP')

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed something.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            ipv4_pool = resource_pools.Pool.get_resource_pool(
                self.client,
                kwargs["pool_ranges"],
                "IPv4",
            )
            if not ipv4_pool:
                _message = f'{kwargs["pool_ranges"]} does not exist'
                return _message, _status, _changed
            kwargs["leaf_spine_ip_pool_range"] = {}
            kwargs["leaf_spine_ip_pool_range"]["resource_pool_uuid"] = (
                ipv4_pool["uuid"]
            )
            data = models.L3LS(
                name_prefix=name, fabric_uuid=self.uuid, **kwargs
            )
            uri_l3ls = f"/fabrics/{self.uuid}/leaf_spine_workflow"
            l3ls_request = self.client.post(
                uri_l3ls,
                data=json.dumps(data.dict(exclude_none=True)),
            )
            if l3ls_request.status_code in utils.response_ok:
                _message = "Successfully created L3 Leaf Spine configuration"
                _status = True
                _changed = True
            else:
                if (
                    "No new leaf spine Pairs found"
                    in l3ls_request.json()["result"]
                ):
                    _message = (
                        "No new leaf spine Pairs found. No action taken."
                    )
                    _status = True
                else:
                    _message = l3ls_request.json()["result"]

        except ValidationError as exc:
            _message = f"An exception {exc} occurred"

        return _message, _status, _changed

    def create_subleaf(self, **kwargs: dict) -> tuple:
        """create_subleaf.

        Check if some devices have the role "sub_leaf" and
        launch the related workflow in AFC.

        Args:
            name_prefix (str): Subleaf configuration name.

        Example:
            fabric_instance.create_subleaf(name="SubLeaf DC1")

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed something.

        """
        _message = ""
        _status = False
        _changed = False

        payload_subleaf = {"name_prefix": f"{kwargs['name']}", "type": "L2"}
        sub_leaf_request = self.client.post(
            f"fabrics/{self.uuid}/subleaf_leaf",
            data=json.dumps(payload_subleaf),
        )
        if sub_leaf_request.status_code in utils.response_ok:
            _message = "Successfully configured sub-leaf"
            _status = True
            _changed = True
        else:
            if (
                "Subleaf Leaf configuration exist"
                in sub_leaf_request.json()["result"]
            ):
                _message = "Subleaf Leaf configuration exist. No action taken."
                _status = True
            else:
                _message = sub_leaf_request.json()["result"]

        return _message, _status, _changed

    def reapply_l3ls(self, name: str, **kwargs: dict) -> tuple:
        """reapply_l3ls Triggers reapply leaf spine workflow.

        Args:
            name (str): Leaf and Spine configuration name
            pool_ranges (str): Name of the IP Pool range used to
                configure IP Interfaces

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed something.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            payload_l3ls = {"fabric_uuid": self.uuid, "name_prefix": name}
            ipv4_pool = resource_pools.Pool.get_resource_pool(
                self.client, kwargs["pool_ranges"], "IPv4",
            )
            if not ipv4_pool:
                _message = f'{kwargs["pool_ranges"]} does not exist'
                return _message, _status, _changed
            kwargs["leaf_spine_ip_pool_range"] = {}
            kwargs["leaf_spine_ip_pool_range"]["resource_pool_uuid"] = (
                ipv4_pool["uuid"]
            )
            url_l3ls = f"fabrics/{self.uuid}/leaf_spine_workflow"
            l3ls_request = self.client.post(
                url_l3ls,
                data=json.dumps(payload_l3ls),
            )
            if l3ls_request.status_code in utils.response_ok:
                _message = ("Successfully reapplied the L3 Leaf-Spine "
                            "configuration")
                _status = True
                _changed = True
            elif (
                l3ls_request.status_code in [400]
                and "No new leaf spine Pairs found"
                in l3ls_request.json()["result"]
            ):
                _message = ("No new Leaf Spine pair")
                _status = True
            else:
                _message = l3ls_request.json()["result"]

        except ValidationError as exc:
            _message = (f"An exception occurred {exc} while reapplying L3 "
                        "Leaf-Spine")

        return _message, _status, _changed
