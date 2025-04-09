# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from typing import List, Literal

from pydantic import BaseModel, root_validator

"""Models file is used to create a dictionary."""


class PsmRule(BaseModel):
    name: str
    description: str = ""
    type: Literal["layer3", "layer2"] = "layer3"
    source_endpoint_groups: List[str] = []
    destination_endpoint_groups: List[str] = []
    service_qualifiers: List[str] = []
    applications: List[str] = []
    action: Literal["allow", "drop"] = "allow"

    @root_validator(pre=True)
    def convert_int_to_str(cls, values):
        if values.get("rule_type"):
            values["type"] = values["rule_type"]
            values.pop("rule_type")
        else:
            values.pop("type")
        return values


class PolicyEnforcer(BaseModel):
    enforcer_type: Literal["network", "vrf"]
    direction: Literal["egress", "ingress"]
    pdt_type: Literal["leaf", "borderleaf"] = "leaf"
    uuid: str


class PsmPolicies(BaseModel):
    name: str
    description: str = ""
    policy_subtype: Literal["layer3", "layer2", "firewall"] = "firewall"
    priority: int = 1
    rules: List[str] = []
    rules_disabled: List[str] = []
    enforcers: List[PolicyEnforcer] = []
    object_type: str = "policy"

    @root_validator(pre=True)
    def convert_int_to_str(cls, values):
        if values.get("eg_type"):
            values["type"] = values["eg_type"]
            values.pop("eg_type")
        else:
            values.pop("type")
        if values.get("policy_type"):
            values["policy_subtype"] = values["policy_type"]
            values.pop("policy_type")
        return values


class Endpoints(BaseModel):
    ipv4_range: str
    type: Literal["endpoint_group_endpoint_ip"] = "endpoint_group_endpoint_ip"
    vm_name: str = None
    vm_tag: str = None
    vmkernel_adapter_name: str = None
    vnic_name: str = None
    host_name: str = None
    vsphere_uuid: str = None


class PsmEndpointGroups(BaseModel):
    name: str
    description: str = ""
    type: Literal["layer3", "layer2", "firewall"] = "firewall"
    sub_type: Literal["ip_collection", "ip_address"] = "ip_address"
    endpoints: List[Endpoints] = []

    @root_validator(pre=True)
    def convert_int_to_str(cls, values):
        if values.get("eg_type"):
            values["type"] = values["eg_type"]
            values.pop("eg_type")
        else:
            values.pop("type")
        return values


class Qualifier(BaseModel):
    type: Literal["port_protocol_pair"] = "port_protocol_pair"
    src_port: str = None
    dst_port: str = None
    ip_protocol: str = None

    @root_validator(pre=True)
    def convert_int_to_str(cls, values):
        if values.get("src_port"):
            values["src_port"] = str(values["src_port"])
        if values.get("dst_port"):
            values["dst_port"] = str(values["dst_port"])
        if values.get("ip_protocol"):
            values["ip_protocol"] = str(values["ip_protocol"])
        return values


class PsmQualifiers(BaseModel):
    name: str
    description: str = ""
    qualifier_type: Literal["layer3"] = "layer3"
    protocol_identifier: List[Qualifier] = []


class Icmp(BaseModel):
    type: int
    code: int


class Dns(BaseModel):
    drop_multi_question_packets: bool = False
    drop_large_domain_name_packets: bool = False
    drop_long_label_packets: bool = False
    max_message_length: int = 512
    query_response_timeout: str = "60s"


class Ftp(BaseModel):
    allow_mismatch_ip_address: bool = False


class SunRPC(BaseModel):
    program_id: str


class Msrpc(BaseModel):
    program_uuid: str


class Alg(BaseModel):
    type: Literal["icmp", "dns", "ftp", "sunrpc", "msrpc", "tftp", "rtsp"] = (
        None
    )
    icmp: Icmp = None
    dns: Dns = None
    ftp: Ftp = None
    sunrpc: SunRPC = None
    msrpc: Msrpc = None

    @root_validator(pre=True)
    def native_integration(cls, values):
        if values["type"] == "ftp" and not values.get("ftp"):
            values["ftp"] = Ftp()
        if values["type"] == "dns" and not values.get("dns"):
            values["dns"] = Dns()
        return values


class PsmApplications(BaseModel):
    name: str
    description: str = ""
    qualifier_uuids: List[str] = []
    alg: Alg = None


class VnicMove(BaseModel):
    vnic_uuids: List[str]
    portgroup_uuid: str


class MoveVnic(BaseModel):
    vnics: List[VnicMove]
