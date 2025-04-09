# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from typing import List, Literal

from pydantic import BaseModel, root_validator

"""Models file is used to create a dictionary that is later used."""


class ResourcePool(BaseModel):
    resource_pool_uuid: str


class Fabric(BaseModel):
    name: str
    timezone: str
    fabric_class: Literal["Data", "Management"] = "Data"


class EVPN(BaseModel):
    fabric_uuid: str
    name_prefix: str = "NEW EVPN"
    switch_uuids: List[str] = []
    description: str = ""
    as_number: str = None
    rt_type: Literal["AUTO", "ASN:VNI", "ASN:VLAN", "ASN:NN"] = "AUTO"
    system_mac_range: ResourcePool
    vlans: str
    vni_base: int

    @root_validator(pre=True)
    def convert_values(cls, values):
        new_values = values.copy()
        if values.get("name"):
            new_values["name_prefix"] = values["name"]
        if values.get("system_mac_range"):
            new_values["system_mac_range"] = {}
            new_values["system_mac_range"]["resource_pool_uuid"] = values[
                "system_mac_range"
            ]
        return new_values


class Vsx(BaseModel):
    name_prefix: str
    system_mac_range: ResourcePool = None
    keepalive_ip_pool_range: ResourcePool = None
    keep_alive_interface_mode: str

    @root_validator(pre=True)
    def convert_pools(cls, values):
        new_values = values.copy()
        if values.get("system_mac_range"):
            new_values["system_mac_range"] = {}
            new_values["system_mac_range"]["resource_pool_uuid"] = values[
                "system_mac_range"
            ]
        if values.get("keepalive_ip_pool_range"):
            new_values["keepalive_ip_pool_range"] = {}
            new_values["keepalive_ip_pool_range"]["resource_pool_uuid"] = (
                values["keepalive_ip_pool_range"]
            )
        return new_values


class L3LS(BaseModel):
    name_prefix: str
    fabric_uuid: str
    description: str = ""
    leaf_spine_ip_pool_range: ResourcePool = None


class EVPNSettings(BaseModel):
    fabric_uuid: str
    arp_suppression: bool = False
    local_svi: bool = False
    local_mac: bool = False
    vxlan_tunnel_bridging_mode: str = None
    switch_uuids: List[str] = []


class GlobalRT(BaseModel):
    rt_type: Literal["NN:VLAN", "NN:VNI"]
    administrative_number: int


class VLANStretching(BaseModel):
    fabric_uuids: List[str]
    stretched_vlans: str
    global_route_targets: List[GlobalRT]


class RemoteFabric(BaseModel):
    fabric_uuid: str
    border_leader_uuid: str
    asn: str
    ipv4_address_A: str


class MultiFabrics(BaseModel):
    name: str
    description: str = ""
    border_leader: str
    l3_ebgp_borders: List[str]
    remote_fabrics: List[RemoteFabric]
    bgp_auth_password: str = ""
    uplink_to_uplink: bool = None
