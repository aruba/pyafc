# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from typing import Literal

from pydantic import BaseModel, model_validator

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
    switch_uuids: list[str] = []
    description: str = ""
    as_number: str = None
    rt_type: Literal["AUTO", "ASN:VNI", "ASN:VLAN", "ASN:NN"] = "AUTO"
    system_mac_range: ResourcePool
    vlans: str
    vni_base: int

    @model_validator(mode="before")
    @classmethod
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

    @model_validator(mode="before")
    @classmethod
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
    fabric_uuid: str | None = None
    arp_suppression: bool = False
    local_svi: bool | None = None
    local_mac: bool | None = None
    vxlan_tunnel_bridging_mode: str | None = None
    switch_uuids: list[str] | None = None


class GlobalRT(BaseModel):
    rt_type: Literal["NN:VLAN", "NN:VNI"]
    administrative_number: int


class VLANStretching(BaseModel):
    fabric_uuids: list[str]
    stretched_vlans: str
    global_route_targets: list[GlobalRT]


class VlanEntry(BaseModel):
    vlan_id: str
    vlan_name: str | None = None
    strict_firewall_bypass_enabled: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def convert_vlan_id(cls, values):
        if isinstance(values, dict) and values.get("vlan_id") is not None:
            values["vlan_id"] = str(values["vlan_id"])
        return values


class VlanTable(BaseModel):
    vlans: list[VlanEntry]
    vlan_scope: dict


class RemoteFabric(BaseModel):
    fabric_uuid: str
    border_leader_uuid: str
    asn: str
    ipv4_address_A: str


class MultiFabrics(BaseModel):
    name: str
    description: str = ""
    border_leader: str
    l3_ebgp_borders: list[str]
    remote_fabrics: list[RemoteFabric]
    bgp_auth_password: str = ""
    uplink_to_uplink: bool = None
