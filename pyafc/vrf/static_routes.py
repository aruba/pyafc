# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Utility functions and classes OSPF management.

This module provides:
- get_ospf_switch_details: get OSPF details for a given switch
- get_ospf_routers: get OSPF Routers for a given switch
- get_ospf_router: get information for a specific OSPF Router for a switch.
- get_ospf_router_and_area: get info for a OSPF Router and Area for a switch.
- create_ospf_router: Create an OSPF Router
- create_ospf_area: Create an OSPF Area
- create_ospf_interface: Create an OSPF Interface
"""

from __future__ import annotations

import json

from pydantic import ValidationError

from pyafc.common import utils
from pyafc.vrf import models


class StaticRoute:
    def __init__(self) -> None:
        """__init__ Init Method."""

    def create_static_route(self, **kwargs: dict) -> tuple:
        """create_static_route Create a Static Route.

        Args:
            name (str): Static Route name.
            description (str, optional) = Route's description
            destination (str) = Network or IPv4 Address
            next_hop (str) = Next Hop Address.
                A next hop of 0.0.0.0 signifies that the destination
                network in the static route should use the default route.
                A next hop of null indicates traffic matching the destination
                network will be discarded and is used to prevent routing
                loops.
            distance (int, optional) = Administrative distance of the static
                route
            tag (int, optional) = Static route tag, used to control
                redistribution
            type (str, optional) = Type of IP Static route.
                One of :
                - "forward"
                - "nullroute"
                Defaults to "forward"
            switches (list) = List of switches

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if kwargs.get("switches"):
                kwargs["switch_uuids"] = utils.consolidate_switches_list(
                    self.client,
                    kwargs["switches"],
                )

            data = models.StaticRoute(**kwargs)

            uri_static_route = f"vrfs/{self.uuid}/ip_static_routes"
            static_route_request = self.client.post(
                uri_static_route,
                data=json.dumps([data.dict(exclude_none=True)]),
            )
            if static_route_request.status_code in utils.response_ok:
                _message = "Successfully created static route as per inputs"
                _status = True
                _changed = True
            elif "already exists" in static_route_request.json()["result"]:
                _message = "The Static Route already exists. No action taken"
                _status = True
            else:
                _message = static_route_request.json()["result"]

        except ValidationError as exc:
            _message = f"An exception {exc} occurred"

        return _message, _status, _changed
