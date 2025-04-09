# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from typing import List, Literal

from pydantic import BaseModel, Field, root_validator

"""Models file is used to create a dictionary that is later used."""


class LACP(BaseModel):
    mode: str = "active"
    interval: Literal["fast", "slow"] = "slow"
    priority: int = 1


class Speed(BaseModel):
    current: str = 0
    permitted: list = None


class PortProperties(BaseModel):
    lacp: LACP = Field(default_factory=LACP)
    port_uuids: List[str]
    speed: Speed = Field(default_factory=Speed)
    switch_uuid: str = None


class LAG(BaseModel):
    name: str = None
    description: str = ""
    type: str = "provisioned"
    port_properties: list = []
    native_vlan: int = 1
    tagged: bool = False
    vlan_group_uuids: list = []
    ungrouped_vlans: str = None
    lacp_fallback: bool = True
    enable_lossless: bool = False
    lag_number: int = 0
    vlan_mode: str = "null"
    status: str = "null"

    @root_validator(pre=True)
    def check_ports(cls, values):
        if not values["port_properties"]:
            raise ValueError("Specified ports do not exist")
        return values


class InternalLAG(BaseModel):
    name: str
    port_properties: List[PortProperties]
    type: str = "internal"
    fabric_uuid: str = None
    mlag: bool = False
    vlan_mode: str = "null"
    vlans: str = ""
    status: str = "null"
    pvlan_shutdown: bool = False
    pvlan_shutdown_reason: str = "null"
    stp_config: str = "null"
    native_vlan: int = 1
    vlan_group_uuids: list = []
    ungrouped_vlans: str = ""


class VlanGroup(BaseModel):
    name: str
    description: str = ""
    vlans: str
