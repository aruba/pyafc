# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Utility functions and classes OSPF management.

This module provides:
- get_ospf_switch_details: get OSPF details for a given switch
- get_ospf_routers: get OSPF Routers for a given switch
- get_ospf_router: get information for a specific OSPF Router for a switch.
- get_ospf_router_and_area: get info for a specific OSPF Router and Area.
- create_ospf_router: Create an OSPF Router
- create_ospf_area: Create an OSPF Area
- create_ospf_interface: Create an OSPF Interface
"""

from __future__ import annotations

import json

from pydantic import ValidationError

from pyafc.common import exceptions, utils
from pyafc.switches import switches
from pyafc.vrf import models


class OSPF:
    def __init__(self) -> None:
        """__init__ Init Method."""

    def get_ospf_switch_details(self, switch: str) -> dict | bool:
        """get_ospf_switch_details Find OSPF Switch details.

        Args:
            switch (str): IP Address of the switch.

        Returns:
            OSPF router details are saved as class attribute.

        """
        self.get_switch_uuid(switch)
        self.get_vrf_uuid("default")
        ospf_switch_request = self.client.get(
            f"vrfs/{self.vrf_uuid}/ospf_routers",
            headers=self.header,
        )
        self.ospf_switch_details = None
        for router in ospf_switch_request.json()["result"]:
            if router["switch_uuid"] == self.switch_uuid:
                self.ospf_switch_details = router
        return False

    def get_ospf_routers(self, switch: str, process: int = 1) -> dict | bool:
        """get_ospf_routers Find OSPF Routers.

        Args:
            switch (str): IP Address of the switch.
            process (int): OSPF Process ID.

        Returns:
            OSPF routers' details in JSON format and False if not found.

        """
        uri = f"vrfs/{self.uuid}/ospf_routers"
        request_ospf_routers = self.client.get(uri)
        switch_uuid = switches.Switch.get_switch_uuid(self.client, switch)
        if request_ospf_routers.json()["result"]:
            for router in request_ospf_routers.json()["result"]:
                if (
                    router["switch_uuid"] == switch_uuid
                    and router["id"] == process
                ):
                    return router
        return False

    def get_ospf_router(self, switch: str, name: str) -> dict | bool:
        """get_ospf_router Find specific OSPF router Config.

        Args:
            name (str): Name of the OSPF Router config.
            switch (str): IP Address of the switch.

        Returns:
            OSPF router details in JSON format and False if not found.

        """
        uri = f"vrfs/{self.uuid}/ospf_routers"
        request_ospf_routers = self.client.get(uri)

        switch_ip = switches.Switch.consolidate_ip(self.client, switch)
        switch_instance = switches.Switch(self.client, switch_ip)

        if request_ospf_routers.json()["result"]:
            for router in request_ospf_routers.json()["result"]:
                if (
                    router["switch_uuid"] == switch_instance.uuid
                    and router["name"] == f"{name}-{switch_instance.name}"
                ):
                    return router
        return False

    def create_ospf_router(self, **kwargs: dict) -> tuple:
        """create_ospf_router Create an OSPF Router.

        Args:
            name (str) = OSPF Router Name.
            description (str) = OSPF Router Description.
            switches (list) = List of Switches
            enable (bool) = Enable OSPF Router. Default to True
            id (int) = OSPF Router ID. Default to 1
            redistribute (dict) = OSPF Redistribution. Check Example
            redistribute_route_map (dict) = OSPF Redistribution Route Map.
                                            Check Example
            maximum_paths (int) - OSPF Max Paths. Default to 8
            max_metric_router_lsa (bool) = Advertise Router-LSAs with maximum
                                           metric value.
                                           Default to True
            max_metric_include_stub (bool) = Advertise Router-LSAs with
                                             maximum metric value for stub
                                             links.
                                             Default to True
            max_metric_on_startup (int) = Specify the time period in seconds
                                          up to which the Router-LSAs are
                                          advertised with maximum metric after
                                          system startup.
            passive_interface_default(bool) = Configure all OSPF enabled
                                              interfaces to be passive.
                                              Default to True
            trap_enable(bool) = Enable OSPF SNMP Traps.
                                Default to True
            gr_ignore_lost_interface(bool) = Enable the restarting router to
                                             ignore lost ospfinterfaces during
                                             a graceful restart process.
                                             Default to False
            gr_restart_interval (int) = Set the maximum interval in seconds
                                        that another router should wait.
            distance (int) = Configure OSPF administrative distance
            default_metric (int) = Configure default metric of
                                   redistributed routes
            default_information (str) = One of "disable", "originate",
                                        "always_originate"
                                        Default to "disable"

        Example:
            ospf_router_data = {
                "instance": "DC1 OSPF Router Border",
                "switches": "10.149.2.100",
                "id": 1,
                "redistribute": {
                    "redistribute_bgp": True,
                },
                }

            vrf_instance.create_ospf_router(name="DC1 OSPF Router Border",
                                            **ospf_router_data)


        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            kwargs["name_prefix"] = kwargs["name"]
            kwargs["switch_uuids"] = utils.consolidate_switches_list(
                self.client,
                kwargs["switches"],
            )

            data = models.OspfRouter(**kwargs)

            uri_ospf_router = f"vrfs/{self.uuid}/ospf_routers"

            ospf_router_request = self.client.post(
                uri_ospf_router,
                data=json.dumps(data.dict(exclude_none=True)),
            )

            if ospf_router_request.status_code in utils.response_ok:
                _message = "Successfully created ospf router as per inputs"
                _status = True
                _changed = True
            elif "already exists" in ospf_router_request.json()["result"]:
                _message = ospf_router_request.json()["result"]
                _status = True
            else:
                _message = ospf_router_request.json()["result"]

        except ValidationError as exc:
            _message = f"An exception {exc} occurred"

        return _message, _status, _changed

    def create_ospf_area(self, **kwargs: dict) -> tuple:
        """create_ospf_router Create an OSPF Area.

        Args:
            name (str): OSPF are name.
            description (str) = OSPF Area Description.
            area_id (int) = Area ID. Default to 0
            area_type (str) = One of "standard", "nssa",
                              "stub", "stub_no_summary",
                              "nssa_no_summary".
                              Default to "standard"

        Example:
            ospf_area_data ={
                "ospf_router": "DC1 OSPF Router Border",
                "switches": ["10.149.2.100"],
                "area_id": "0",
                }

            vrf_instance.create_ospf_area(name="DC1 OSPF Area 0",
                                          **ospf_area_data)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False
        _router_details = []

        _router_details = [
            self.get_ospf_router(switch=switch, name=kwargs["ospf_router"])
            for switch in kwargs["switches"]
        ]

        if len(_router_details) == len(kwargs["switches"]):
            for router in _router_details:
                try:
                    data = models.OspfArea(**kwargs)
                    uri_ospf_area = f"vrfs/{self.uuid}/ospf_routers/{router['instance_uuid']}/areas"
                    ospf_area_request = self.client.post(
                        uri_ospf_area,
                        data=json.dumps(data.dict(exclude_none=True)),
                    )
                    if ospf_area_request.status_code in utils.response_ok:
                        _message = "Successfully configured OSPF Area"
                        _status = True
                        _changed = True
                    elif "Duplicate" in ospf_area_request.json()["result"]:
                        _message = ("The OSPF area with ID already exists. "
                                    "No action taken")
                        _status = True
                    else:
                        _message = ospf_area_request.json()["result"]

                except ValidationError as exc:
                    _message = (
                        f"An exception {exc} occurred while creating OSPF area"
                    )

        else:
            _message = "One of the device has no OSPF Router"

        return _message, _status, _changed

    def get_ospf_router_and_area(
        self,
        switch: str,
        area: str = "0.0.0.0",  # noqa: S104
        process: int = 1,
    ) -> tuple | bool:
        """get_ospf_router_and_area Find OSPF router and area.

        Args:
            switch (str): IP address of the switch.
            area (str): Name of the OSPF Area.
            process (int): Process, defaults to 1.

        Returns:
            OSPF Router and Area details else False.

        """
        uri = f"vrfs/{self.uuid}/ospf_routers?areas=true"
        request_ospf_routers = self.client.get(uri)
        switch_ip = switches.Switch.consolidate_ip(self.client, switch)
        switch_uuid = switches.Switch.get_switch_uuid(self.client, switch_ip)

        if request_ospf_routers.json()["result"]:
            for router in request_ospf_routers.json()["result"]:
                if (
                    router["switch_uuid"] == switch_uuid
                    and router["id"] == process
                ):
                    for ar in router["areas"]:
                        if ar["area_id"] == area:

                            return router, ar
        return False

    def __get_ip_interface(self, switch: str, name: str) -> dict | bool:
        """__get_ip_interface Find IP interface.

        Args:
            name (str): Name of the IP Interface.
            switch (str): Switch IP address.

        Returns:
            IP Interface config data in JSON format and False if not found.

        """
        switch_ip = switches.Switch.consolidate_ip(self.client, switch)
        switch_uuid = switches.Switch.get_switch_uuid(self.client, switch_ip)

        ip_intf_request = self.client.get(f"vrfs/{self.uuid}/ip_interfaces")
        lag_uuid = None
        lag_request = self.client.get("lags?type=internal")
        for lag in lag_request.json()["result"]:
            if (
                lag["name"] == f"LAG#{name}"
                and lag["port_properties"][0]["switch_uuid"] == switch_uuid
            ):
                lag_uuid = lag["uuid"]

        for intf in ip_intf_request.json()["result"]:
            if intf["switch_uuid"] == switch_uuid:
                if intf["if_type"] == "vlan" and intf["name"] == name:
                    return intf
                if (
                    intf["lag_uuid"] == lag_uuid
                    and "loopback" not in intf["if_type"]
                ):
                    return intf

        return False

    def create_ospf_interface(self, **kwargs: dict) -> tuple:
        """create_ospf_interface Create an OSPF interface.

        Args:
            if_uuid: str
            priority (int, optional) = OSPF Priority.
                Defaults to 1
            hello_interval (int, optional) = Interval period for hello
                messages in seconds.
                Defaults to 10
            dead_interval (int, optional) = Dead period for hello
                messages in seconds.
                Defaults to 40
            mtu_size (int, optional) = OSPF MTU size in bytes.
                Defaults to 1500
            ignore_mtu_mismatch (bool, optional) = Ignore MTU Mismatch.
                Defaults to False
            passive_mode (bool, optional) = Enable OSPF Passive Interface.
                Defaults to False
            authentication_value (str, optional) = simple-text authentication
                value.
            md5_list (list, optional) = md5 authentication key value pairs
            authentication_type (str, optional) = One of:
                - "simple-text"
                - "message-digest"
                Defaults to null
            network_type (str) = One of:
                - "ospf_iftype_pointopoint"
                - "ospf_iftype_broadcast",
                - "ospf_iftype_loopback"
                - "ospf_iftype_none".
            bfd (bool, optional) = Enable Bidirectional Forwarding Detection.
                Defaults to False

        Example:
            ospf_interface = {
                "router": "10.149.2.100",
                "area": "0.0.0.0",
                "interface": "VLAN 1254",
                "network_type": "ospf_iftype_broadcast",
                }

            vrf_instance.create_ospf_interface(**ospf_interface)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            try:
                ip_intf_values = self.__get_ip_interface(
                    switch=kwargs["router"],
                    name=kwargs["interface"],
                )
                if not ip_intf_values:
                    raise exceptions.InterfaceNotFound
            except TypeError:
                raise exceptions.InterfaceNotFound

            kwargs["if_uuid"] = ip_intf_values["uuid"]
            process = kwargs.get("process", 1)
            try:
                router, area = self.get_ospf_router_and_area(
                    switch=kwargs["router"],
                    area=kwargs["area"],
                    process=process,
                )
            except TypeError:
                raise exceptions.RouterAreaNotFound

            data = models.OspfInterface(**kwargs)
            uri_ospf_intf = f"vrfs/{self.uuid}/ospf_routers/{router['instance_uuid']}/areas/{area['area_uuid']}/interfaces"

            ospf_intf_request = self.client.post(
                uri_ospf_intf,
                data=json.dumps(data.dict()),
            )

            if ospf_intf_request.status_code in utils.response_ok:
                _message = "Successfully configured the OSPF interface"
                _status = True
                _changed = True
            else:
                if "already exists" in ospf_intf_request.json()["result"]:
                    _status = True
                _message = ospf_intf_request.json()["result"]

        except ValidationError as exc:
            _message = (
                f"An exception {exc} occurred while creating OSPF interface"
            )

        except exceptions.InterfaceNotFound:
            _message = ("Routable interface not found. Cannot "
                        "create OSPF interface")

        except exceptions.RouterAreaNotFound:
            _message = ("Router or Area not found. Cannot "
                        "create OSPF interface")

        return _message, _status, _changed
