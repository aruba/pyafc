# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import utils
from pyafc.route_policies import models


class RouteMap:

    def __init__(
        self,
        client,
        name: str | None = None,
        **kwargs: dict
    ) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of Route Map.

        Returns:
            existing_eg (bool): True if available, False if not.

        """
        if name:
            self.name = name
        if client:
            self.client = client
        self.uuid = None
        self.existing_rm = self.__instantiate_details()

    def __instantiate_details(self) -> None:
        """__instantiate_details Find Route Map UUID.

        Returns:
            If found, the UUID is set as a Class attribute

        """
        rm_request = self.client.get("route_maps")
        for rm in rm_request.json()["result"]:
            if rm["name"] == self.name:
                self.uuid = rm["uuid"]
                for item, value in rm.items():
                    setattr(self, item, value)
                return True
        return False

    @staticmethod
    def get_routemap(client, name: str) -> dict | bool:
        """get_routemap Find and return the route map.

        Args:
            client (Any): AFC Connection object.
            name (str): Route map name.

        Returns:
            If found, returns the route map, else returns false

        """
        uri_rm = "route_maps"

        rm_request = client.get(uri_rm)

        for rm in rm_request.json()["result"]:
            if rm["name"] == name:
                return rm
        return False

    def create_routemap(self, **values: dict) -> tuple:
        """create_routemap Create route map.

        Args:
            description (str): Description of the Route Map
            fabric (list) = List of Fabrics
            switches (list) = List of Switches
            entries (list) = List of Route Map entries. Check example.

        Example:
            rm_data = {
                "switches": ["10.149.2.100-10.149.2.101"],
                "entries": [
                    {
                    "seq": 10,
                    "action": "deny",
                    "route_map_continue": 20,
                    "match_vni": 10100,
                    "set_origin": "igp"
                    },
                    {
                    "seq": 10,
                    "action": "deny",
                    "match_tag": 100,
                    },
                ]
                }
            route_map_instance = route_maps.RouteMap(afc_instance.client, name="New_Route_Map")
            message, status, changed = route_map_instance.create_routemap(**data)


        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_rm:
                _message = f"The route map {self.name} already exists.\
                    No action taken"
                _status = True
            else:
                values = utils.populate_list_fabrics_switches(
                    self.client, values,
                )

                if values.get("name"):
                    values.pop("name")

                data = models.RouteMap(name=self.name, **values)

                add_request = self.client.post(
                    "route_maps",
                    data=json.dumps(data.dict(exclude_none=True)),
                )
                if add_request.status_code in utils.response_ok:
                    _message = f"Successfully created route map {self.name}"
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]
        except Exception as exc:
            _message = (f"An exception {exc} occurred while "
                        f"creating route map {self.name}")

        return _message, _status, _changed

    def delete_routemap(self) -> tuple:
        """delete_routemap Delete route map.

        Args:
            client (Any): AFC Connection object.

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_rm:
                delete_request = self.client.delete(f"route_maps/{self.uuid}")

                if delete_request.status_code in utils.response_ok:
                    _message = f"Successfully deleted route map {self.name}"
                    _status = True
                    _changed = True
                else:
                    _message = delete_request.json()["result"]

            else:
                _message = (f"The route map {self.name} does not exist. "
                            "No action taken.")
                _status = True

        except Exception as exc:
            _message = (f"An exception {exc} occurred while "
                        f"deleting route map {self.name}")

        return _message, _status, _changed

    def add_route_map_entry(self, **values: dict) -> bool:
        """add_route_map_entry Create route map entry.

        Args:
            description (str) = Description
            action (str) = One of:
                - 'permit'
                - 'deny'
            seq (int) = Sequence Number
            route_map_continue (int, optional) = Sequence to continue
            match_as_path (str, optional) = AS Path List name
            match_community_list (str, optional) = Community List name
            match_extcommunity_list (str, optional) = Extended Community List name
            match_local_preference (int, optional) = Local Preference
            match_interface (str, optional) = Interface name
            match_ipv4_next_hop_address (str, optional) = Next Hop IP Address
            match_ipv4_prefix_list (str, optional) = Prefix List name
            match_ipv4_next_hop_prefix_list (str, optional) = Next Hop Prefix List name
            match_ipv4_route_source_prefix_list (str, optional) = Route Source Prefix
                                                        List name
            match_metric (int, optional) = Metric
            match_origin (str, optional) = One of:
                - 'egp'
                - 'igp'
                - 'incomplete'
            match_route_type (str, optional) = One of:
                - 'external_type1'
                - 'external_type2'
            match_source_protocol (str, optional) = One of:
                - 'static'
                - 'connected'
                - 'ospf'
                - 'bgp'
            match_tag (int, optional) = Tag
            match_vni (int, optional) = VNI
            set_as_path_exclude (str, optional) = AS Path List to exclude
            set_as_path_prepend (str, optional) = AS Path List to prepend
            set_community (str, optional) = Community to set
            set_evpn_router_mac (str, optional) = EVPN Router MAC to set
            set_extcommunity_rt (str, optional) = Extended Community to set
            set_dampening_half_life (int, optional) = Dampening Half Life
                to set
            set_dampening_max_suppress_time (int, optional) = Dampening Max
                Suppress Time to set
            set_dampening_reuse (int, optional) = Dampening Reuse to set
            set_dampening_suppress (int, optional) = Dampening Suppress to set
            set_next_hop (str, optional) = Next Hop IP Address to set
            set_local_preference (int, optional) = Local Preference to set
            set_metric (int, optional) = Metric to set
            set_metric_typee (str, optional) = One of:
                - 'external_type1'
                - 'external_type2'
            set_origin (str, optional) = One of:
                - 'egp'
                - 'igp'
                - 'incomplete'
            set_tag (int, optional) = Tag
            set_weight (int, optional) = Weight

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            data = models.RouteMapEntry(**values)

            add_request = self.client.post(
                f"route_maps/{self.uuid}/route_map_entries",
                data=json.dumps(data.dict(exclude_none=True)),
            )
            if add_request.status_code in utils.response_ok:
                _message = "Successfully added route map entry"
                _status = True
                _changed = True
            else:
                _message = add_request.json()["result"]

        except Exception as exc:
            _message = (f"An exception {exc} occurred while adding route map "
                        f"entry to {self.name}")

        return _message, _status, _changed
