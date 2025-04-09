# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import exceptions, utils
from pyafc.dss import models
from pyafc.fabric import fabric as fab
from pyafc.vrf import networks
from pyafc.vrf import vrf as vr


class Policy:
    def __init__(self, client, name: str | None = None, **kwargs: dict) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the Policy.

        Returns:
            existing_policy (bool): True if available, False if not.

        """
        if name:
            self.name = name
        if client:
            self.client = client
        self.uuid = None
        self.existing_policy = self.__instantiate_details()

    def __instantiate_details(self) -> None:
        """__instantiate_details class attribute uuid is set.

        Returns:
            existing_policy (bool): If the input Policy is found.

        """
        policies_request = self.client.get("policies")
        for policy in policies_request.json()["result"]:
            if policy["name"] == self.name:
                self.uuid = policy["uuid"]
                for item, value in policy.items():
                    setattr(self, item, value)
                return True
        return False

    def _get_rules(self, rule: str) -> str:
        """_get_rules hidden function is used to get the rules and return.

        Args:
            rule (str): Name of the Rule.

        Returns:
            Rule UUID (str): Return the UUID of the rule.

        """
        rules_request = self.client.get("rules")

        for ru in rules_request.json()["result"]:
            if ru["name"] == rule:
                return ru["uuid"]

        msg = f"Rule {rule} is unknown"
        raise exceptions.RuleUnknown(msg)

    def _get_enforcer(
        self, fabric: str, vrf: str, network: str = None
    ) -> dict:
        """_get_enforcer hidden function is used to get the enforcer details.

        Args:
            fabric (str): Name of the fabric.
            vrf (str): Name of the VRF.
            network (:obj:`str`, optional): Name of the Network.

        Returns:
            Enforcer Details (dict): Return the enforcer details.

        """
        fabric_uuid = fab.Fabric.get_fabric_uuid(self.client, fabric)
        if not fabric_uuid:
            msg = f"Fabric {fabric} not found"
            raise exceptions.FabricNotFound(msg)

        enforcer_uuid = vr.Vrf.get_vrf_uuid(self.client, vrf, fabric_uuid)
        if not enforcer_uuid:
            msg = f"VRF {vrf} not found in Fabric {fabric}"
            raise exceptions.VrfNotFound(msg)

        if network:
            network_uuid = networks.Network.get_network_uuid(
                self.client, network, enforcer_uuid
            )
            if not network_uuid:
                msg = f"Network {network} not found in VRF {vrf}"
                raise exceptions.NetworkNotFound(msg)
            enforcer_uuid = network_uuid

        return enforcer_uuid

    def create_policy(self, **values: dict) -> tuple:
        """create_policy is used to create policy.

        Args:
            description (str): Endpoint Group description.
            policy_subtype (str, optional): One of :
                - 'layer3'
                - 'layer2'
                - 'firewall'.
                Defaults to 'firewall'
            priority (int, optional): Policy Priority.
                Defaults to 1
            rules (list): List of rules names.
            rules_disabled (list): List of disabled rules names.
            enforcers (list): List of enforcers.
                Check examples.
            object_type (str): Set to "policy".

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed something.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if values.get("rules"):
                new_values = []
                new_values = [
                    self._get_rules(item) for item in values["rules"]
                ]
                values["rules"] = new_values

            if values.get("enforcers"):
                for enforcer in values["enforcers"]:
                    enforcer["uuid"] = self._get_enforcer(**enforcer)

            if self.existing_policy:
                _message = (f"The policy {self.name} already exists. "
                            "No action taken.")
                _status = True
            else:
                if values.get("name"):
                    values.pop("name")
                data = models.PsmPolicies(name=self.name, **values)

                add_request = self.client.post(
                    "policies",
                    data=json.dumps(data.dict(exclude_none=True)),
                )

                if add_request.status_code in utils.response_ok:
                    _message = f"Successfully created policy {self.name}"
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]

        except (
            exceptions.FabricNotFound,
            exceptions.VrfNotFound,
            exceptions.NetworkNotFound,
        ) as exc:
            _message = (f"An exception {exc} occurred while creating "
                        "policy {self.name}")

        return _message, _status, _changed

    def delete_policy(self) -> tuple:
        """delete_policy is used to delete policy.

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed something.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_policy:
                delete_request = self.client.delete(f"policies/{self.uuid}")

                if delete_request.status_code in utils.response_ok:
                    _message = f"Successfully deleted policy {self.name}"
                    _status = True
                    _changed = True
                else:
                    _message = delete_request.json()["result"]
            else:
                _message = (f"The policy {self.name} does not exist. "
                            "No action taken.")
                _status = True

        except (
            exceptions.FabricNotFound,
            exceptions.VrfNotFound,
            exceptions.NetworkNotFound,
        ) as exc:
            _message = (f"An exception {exc} occurred while "
                        "deleting policy {self.name}")

        return _message, _status, _changed
