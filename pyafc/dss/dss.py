# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

from typing import Literal

from pyafc.common import exceptions
from pyafc.dss import endpoint_groups, policies, qualifiers, rules, vnic_moves


class DSS(
    rules.Rule,
    policies.Policy,
    endpoint_groups.EndpointGroup,
    qualifiers.Qualifier,
    vnic_moves.VnicMove,
):
    def __init__(
        self,
        client,
        name: str,
        fw_item: Literal[
            "endpoint_groups",
            "rule",
            "policy",
            "qualifier",
            "application",
            "vnic_move",
        ] = "unset",
        **kwargs: dict,
    ) -> None:
        """Primary class file for DSS related tasks.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): DSS object name.
            fw_item (list): List of DSS Object types.

        Returns:
            Class attributes (Any): Updated class attributes.

        """
        self.client = client
        self.name = name
        if fw_item == "endpoint_groups":
            endpoint_groups.EndpointGroup.__init__(self, **kwargs)
        elif fw_item == "rule":
            rules.Rule.__init__(self, **kwargs)
        elif fw_item == "policy":
            policies.Policy.__init__(self, **kwargs)
        elif fw_item == "qualifier":
            qualifiers.Qualifier.__init__(self, **kwargs)
        elif fw_item == "vnic_move":
            vnic_moves.VnicMove.__init__(self, **kwargs)
        else:
            msg = "Firewall Item has not been specified or is not a valid one"
            raise exceptions.PolicyTypeNotValid(msg)

    @staticmethod
    def get_dsses(client) -> list:
        """get_dsses a static class method used to get pensando dss items.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.

        Returns:
            Pensando DSS Objects (list): List of Pensando dss items.

        """
        uri_dss = "pensando/dss"
        dss_request = client.get(uri_dss)

        return dss_request.json()["result"]

    @staticmethod
    def get_dsm(client) -> list:
        """get_dsm a static class method used to get switches/dsm items.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.

        Returns:
            DSS Objects (list): List of dss items under switches.

        """
        uri_dsm = "switches/dsm"
        dsm_request = client.get(uri_dsm)

        return dsm_request.json()["result"]

    @staticmethod
    def get_policies(client, statictics_timeframe: str = "last") -> list:
        """get_policies a static class method used to get the DSS policies.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.

        Returns:
            DSS Policies (list): List of DSS policies.

        """
        if statictics_timeframe not in [
            "last",
            "5m",
            "10m",
            "30m",
            "1h",
            "4h",
            "24h",
        ]:
            msg = ("Not a valid statistics Timeframe - Should be one of : "
                    "last, 5m, 10m, 30m, 1h, 4h, 24h")
            raise exceptions.TimeframeNotValid(msg)

        uri_policies = f"policies?include_enforcers=true&include_rules=\
                true&include_health_details=true&include_statistics=true&\
                rule_statistics_type={statictics_timeframe}"
        policies_request = client.get(uri_policies)

        return policies_request.json()["result"]

    @staticmethod
    def get_rules(client) -> list:
        """get_dsses a static class method used to get the DSS rules.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.

        Returns:
            DSS Rules (list): List of DSS rules.

        """
        uri_rules = "rules?include_endpoint_groups=true&\
                    include_service_qualifiers=true&include_applications=true"
        rules_request = client.get(uri_rules)

        return rules_request.json()["result"]

    @staticmethod
    def get_endpoint_groups(client) -> list:
        """get_dsses a static class method used to get the DSS endpoint groups.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.

        Returns:
            DSS endpoint groups (list): List of DSS endpoint groups.

        """
        uri_eg = "endpoint_groups?tags=true"
        eg_request = client.get(uri_eg)

        return eg_request.json()["result"]

    @staticmethod
    def get_applications(client) -> list:
        """get_dsses a static class method used to get the applications.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.

        Returns:
            DSS applications (list): List of DSS applications.

        """
        uri_app = "applications?include_qualifiers=true"
        eg_request = client.get(uri_app)

        return eg_request.json()["result"]

    @staticmethod
    def get_qualifiers(client) -> list:
        """get_dsses a static class method used to get the qualifiers.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.

        Returns:
            DSS qualifiers (list): List of DSS qualifiers.

        """
        uri_qual = "qualifiers?tags=true"
        eg_request = client.get(uri_qual)

        return eg_request.json()["result"]
