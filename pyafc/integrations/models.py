# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

from typing import List

from pydantic import BaseModel

"""Models file is used to create a dictionary that is later used as the body of the post request."""


class Psm(BaseModel):
    name: str
    description: str = ""
    host: str
    username: str
    password: str
    enabled: bool = True
    fabric_uuid: List[str]
    verify_ssl: bool = False
    orchestrator_uuids: list = []
    auto_decommission_dss: bool = False
    auto_vlan_placement: bool = True


class vSphere(BaseModel):
    name: str
    description: str = ""
    host: str
    username: str
    password: str
    enabled: bool = True
    verify_ssl: bool = False
    auto_discovery: bool = True
    storage_optimization: bool = False
    use_cdp: bool = False
    downlink_vlan_provisioning: bool = False
    downlink_vlan_range: str | None = None
    vlan_provisioning: bool = False
    vlan_range: str | None = None
    pvlan_provisioning: bool = False
    pvlan_range: str | None = None
    endpoint_group_provisioning: bool = False
    cumulative_epg_provisioning: bool = False
