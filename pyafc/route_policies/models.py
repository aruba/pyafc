# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from ipaddress import IPv4Address
from typing import List, Literal

from pydantic import BaseModel, root_validator

"""Models file is used to create a dictionary that is later used."""


class RouteMapEntry(BaseModel):
    description: str = ""
    action: Literal["permit", "deny"]
    seq: int
    route_map_continue: int = None
    match_as_path: str = None
    match_community_list: str = None
    match_extcommunity_list: str = None
    match_local_preference: int = None
    match_interface: str = None
    match_ipv4_next_hop_address: IPv4Address = None
    match_ipv4_prefix_list: str = None
    match_ipv4_next_hop_prefix_list: str = None
    match_ipv4_route_source_prefix_list: str = None
    match_metric: int = None
    match_origin: Literal["egp", "igp", "incomplete"] = None
    match_route_type: Literal["external_type1", "external_type2"] = None
    match_source_protocol: Literal["static", "connected", "ospf", "bgp"] = None
    match_tag: int = None
    match_vni: int = None
    set_as_path_exclude: str = None
    set_as_path_prepend: str = None
    set_community: str = None
    set_evpn_router_mac: str = None
    set_extcommunity_rt: str = None
    set_dampening_half_life: int = None
    set_dampening_max_suppress_time: int = None
    set_dampening_reuse: int = None
    set_dampening_suppress: int = None
    set_next_hop: IPv4Address = None
    set_local_preference: int = None
    set_metric: int = None
    set_metric_typee: Literal["external_type1", "external_type2"] = None
    set_origin: Literal["egp", "igp", "incomplete"] = None
    set_tag: int = None
    set_weight: int = None

    @root_validator(skip_on_failure=True)
    def check_seq(cls, values):
        if (
            values.get("route_map_continue")
            and values["route_map_continue"] < values["seq"]
        ):
            raise ValueError(
                "Continue Sequence must be higher than the Route Map Sequence"
            )
        return values


class RouteMap(BaseModel):
    name: str
    description: str = ""
    fabric_uuids: List[str] = []
    switch_uuids: List[str] = []
    entries: List[RouteMapEntry]


class EntryPrefix(BaseModel):
    address: IPv4Address
    prefix_length: int

    @root_validator(skip_on_failure=True)
    def convert_ip(cls, values):
        values["address"] = str(values["address"])
        return values


class PrefixListEntry(BaseModel):
    description: str = None
    action: Literal["permit", "deny"]
    seq: int
    prefix: Literal["any"]
    ge: int = None
    le: int = None


class PrefixList(BaseModel):
    name: str
    description: str = ""
    fabric_uuids: List[str] = []
    switch_uuids: List[str] = []
    entries: List[PrefixListEntry]
    address_family: str = "ipv4"
    origin: str = "local-prefix-list"


class CommunityListEntry(BaseModel):
    description: str = None
    action: Literal["permit", "deny"]
    seq: int
    match_string: str


class CommunityList(BaseModel):
    name: str
    description: str = ""
    fabric_uuids: List[str] = []
    switch_uuids: List[str] = []
    type: Literal[
        "community-list",
        "community-expanded-list",
        "extcommunity-list",
        "extcommunity-expanded-list",
    ]
    entries: List[CommunityListEntry]


class ASPathListEntry(BaseModel):
    description: str = None
    action: Literal["permit", "deny"]
    seq: int
    regex: str


class ASPathList(BaseModel):
    name: str
    description: str = ""
    fabric_uuids: List[str] = []
    switch_uuids: List[str] = []
    entries: List[ASPathListEntry]
