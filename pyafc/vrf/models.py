# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Models file is used to create a dictionary that is later used."""

from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field, root_validator


class ResourcePool(BaseModel):
    """ResourcePool Model for Resources Pools.

    Args:
        None.

    Returns:
        ResourcePool: Returns a ResourcePool object.

    """

    resource_pool_uuid: str


class RouteTarget(BaseModel):
    """RouteTarget Model for a single Route Target.

    Args:
        None.

    Returns:
        RouteTarget: Returns a RouteTarget object.

    """

    as_number: str
    address_family: str
    evpn: bool = None
    route_mode: str


class RouteTargets(BaseModel):
    """RouteTarget Model for a a list of Route Targets.

    Args:
        None.

    Returns:
        RouteTargets: Returns a RouteTargets object.

    """

    primary_route_target: RouteTarget
    secondary_route_targets: List[RouteTarget] = []


class VRF(BaseModel):
    """VRF Base Model allowing to represent a VRF.

    Args:
        None.

    Returns:
        VRF: Returns a VRF object.

    """

    name: str
    fabric_uuid: str
    vni: int = None
    switch_uuids: List[str] = []
    route_target: RouteTargets = {}
    route_distinguisher: str = "loopback1:1"
    max_cps_mode: str = "unlimited"
    max_sessions_mode: str = "unlimited"
    max_sessions: int | None = None
    max_cps: int | None = None
    allow_session_reuse: bool = True
    connection_tracking_mode: bool = False
    description: str = ""


class VRFReapply(BaseModel):
    """VRF Base Model allowing to represent a VRF.

    Args:
        None.

    Returns:
        VRF: Returns a VRF object.

    """

    name: str
    switch_uuid: str
    route_target: RouteTargets = {}
    route_distinguisher: str = "loopback1:1"


class BGPDetails(BaseModel):
    """BGPDetails Base Model allowing to represent a BGP Configuration.

    Args:
        None.

    Returns:
        BGPDetails: Returns a BGPDetails object.

    """

    name: str
    as_number: str
    redistribute_ospf: bool = None
    redistribute_static: bool = None
    redistribute_loopback: bool = None
    keepalive_timer: int = None
    holddown_timer: int = None
    enable: bool = True
    bestpath: bool = True
    fast_external_fallover: bool = True
    trap_enable: bool = True
    log_neighbor_changes: bool = True
    deterministic_med: bool = True
    always_compare_med: bool = True
    maximum_paths: int = 8
    redistribute_connected_route_map: list = None
    redistribute_ospf_route_map: list = None
    redistribute_local_route_map: list = None
    redistribute_static_route_map: list = None
    redistribute_ospf_process_route_map: list = None
    networks: list = []
    neighbors: list = []
    router_id: str = None


class BGPUpdate(BaseModel):
    """BGPUpdate Base Model allowing to represent an update of the BGP Config.

    Args:
        None.

    Returns:
        BGPUpdate: Returns a BGPUpdate object.

    """

    as_number: str = "0"
    description: str = ""
    redistribute_ospf: bool = False
    redistribute_static: bool = False
    redistribute_loopback: bool = False
    redistribute_connected: bool = True
    keepalive_timer: int = 60
    holddown_timer: int = 180
    enable: bool = True
    bestpath: bool = True
    fast_external_fallover: bool = True
    trap_enable: bool = True
    log_neighbor_changes: bool = True
    deterministic_med: bool = True
    always_compare_med: bool = True
    maximum_paths: int = 8

    @root_validator(pre=True)
    def convert_values(cls, values: dict) -> dict:
        """check_redistribute_rm Convert values to expected ones.

        Args:
            cls: Initial instanciation.
            values: Initial values.

        Returns:
            values: Returned values.

        """
        if values.get("as_number"):
            values["as_number"] = str(values["as_number"])
        return values


class BGPUpdateSwitch(BaseModel):
    """BGPUpdateSwitch Base Model allowing to represent an update of the BGP.

    Args:
        None.

    Returns:
        BGPUpdateSwitch: Returns a BGPUpdate object.

    """

    as_number: str = "0"
    description: str = ""
    router_id: str = None
    redistribute_ospf: bool = False
    redistribute_static: bool = False
    redistribute_loopback: bool = False
    redistribute_connected: bool = True
    keepalive_timer: int = 60
    holddown_timer: int = 180
    enable: bool = True
    bestpath: bool = True
    fast_external_fallover: bool = True
    trap_enable: bool = True
    log_neighbor_changes: bool = True
    deterministic_med: bool = True
    always_compare_med: bool = True
    maximum_paths: int = 8
    networks: list = []
    neighbors: list = []

    @root_validator(pre=True)
    def convert_values(cls, values: dict) -> dict:
        """check_redistribute_rm Convert values to expected ones.

        Args:
            cls: Initial instanciation.
            values: Initial values.

        Returns:
            values: Returned values.

        """
        if values.get("as_number"):
            values["as_number"] = str(values["as_number"])
        return values


class BGPConfig(BaseModel):
    """BGPConfig Base Model allowing to represent an update of the BGP Config.

    Args:
        None.

    Returns:
        BGPConfig: Returns a BGPConfig object.

    """

    as_number: str
    description: str = ""
    router_id: str = None
    redistribute_ospf: bool = False
    redistribute_static: bool = False
    redistribute_loopback: bool = False
    redistribute_connected: bool = True
    keepalive_timer: int = 60
    holddown_timer: int = 180
    enable: bool = True
    bestpath: bool = True
    fast_external_fallover: bool = True
    trap_enable: bool = True
    log_neighbor_changes: bool = True
    deterministic_med: bool = True
    always_compare_med: bool = True
    maximum_paths: int = 8
    networks: list = []
    neighbors: list = []

    @root_validator(pre=True)
    def convert_values(cls, values: dict) -> dict:
        """check_redistribute_rm Convert values to expected ones.

        Args:
            cls: Initial instanciation.
            values: Initial values.

        Returns:
            values: Returned values.

        """
        values["as_number"] = str(values["as_number"])
        return values


class OspfMetric(BaseModel):
    """OspfMetric Base Model allowing to represent OSPF Metric values.

    Args:
        None.

    Returns:
        OspfMetric: Returns a OspfMetric object.

    """

    router_lsa: bool = True
    include_stub: bool = True
    on_startup: int = 300


class Ospf(BaseModel):
    """Ospf Base Model allowing to represent OSPF.

    Args:
        None.

    Returns:
        Ospf: Returns a Ospf object.

    """

    hello_interval: int = 10
    dead_interval: int = 40
    authentication_type: str = None
    max_metric: OspfMetric
    passive_interface_default: bool = True
    trap_enable: bool = False


class BgpDualASN(BaseModel):
    """BgpDualASN Base Model allowing to represent a Dual ASN architecture.

    Args:
        None.

    Returns:
        BgpDualASN: Returns a BgpDualASN object.

    """

    spine_asn: str
    leaf_asn: str


class BgpMultiASN(BaseModel):
    """BgpMultiASN Base Model allowing to represent a Multi-ASN architecture.

    Args:
        None.

    Returns:
        BgpMultiASN: Returns a BgpMultiASN object.

    """

    starting_sl_asn: str
    starting_bdr_asn: str


class Bgp(BaseModel):
    """Bgp Base Model allowing to represent a BGP Instance.

    Args:
        None.

    Returns:
        Bgp: Returns a Bgp object.

    """

    asn_type: Literal["DUAL", "MULTIPLE"]
    dual_asn: BgpDualASN = None
    multi_asn: BgpMultiASN = None
    keepalive_timer: int = 60
    holddown_timer: int = 180
    activate_ip_routes: bool = True
    allowas_in: bool = True
    auth_password: str = None

    @root_validator(pre=True)
    def check_values(cls, values: dict) -> dict:
        """check_redistribute_rm Convert values to expected ones.

        Args:
            cls: Initial instanciation.
            values: Initial values.

        Returns:
            values: Returned values.

        """
        if not values.get("dual_asn") and not values.get("multi_asn"):
            error_msg = "ASN configuration must be specified"
            raise ValueError(error_msg)
        return values


class Underlay(BaseModel):
    """Underlay Base Model allowing to represent an Underlay Instance.

    Args:
        None.

    Returns:
        Underlay: Returns a Underlay object.

    """

    name: str
    description: str = ""
    underlay_type: Literal["OSPF", "EBGP"]
    bfd: bool = False
    transit_vlan: int
    ipv4_address: ResourcePool
    ospf: Ospf = None
    bgp: Bgp = None

    @root_validator(pre=True)
    def convert_values(cls, values: dict) -> dict:
        """check_redistribute_rm Convert values to expected ones.

        Args:
            cls: Initial instanciation.
            values: Initial values.

        Returns:
            new_values: Returned values.

        """
        new_values = values.copy()
        if values["underlay_type"] == "EBGP" and not values.get("bgp"):
            error_msg = "EBGP configuration is missing"
            raise ValueError(error_msg)
        if not values.get("ospf") and values["underlay_type"] == "OSPF":
            new_values["ospf"] = {}
            new_values["ospf"]["max_metric"] = {}
        if values.get("ipv4_address"):
            new_values["ipv4_address"] = {}
            new_values["ipv4_address"]["resource_pool_uuid"] = values["ipv4_address"]
        return new_values


class UnderlayReapply(BaseModel):
    """Underlay Base Model allowing to represent an Underlay Instance.

    Args:
        None.

    Returns:
        Underlay: Returns a Underlay object.

    """

    name: str
    description: str = ""
    underlay_type: Literal["OSPF", "EBGP"] = "OSPF"
    bfd: bool = False
    transit_vlan: int
    ipv4_address: ResourcePool
    ospf: Ospf
    update: bool = False


class IBGP(BaseModel):
    """IBGP Model for an iBGP configuration.

    Args:
        None.

    Returns:
        IBGP: Returns a IBGP object.

    """

    spine_leaf_asn: str
    rr_server: list
    auth_password: str = ""
    spine_group_name: str = "spine-RR"
    leaf_group_name: str = "leaf"


class EBGP(BaseModel):
    """EBGP Model for an EBGP configuration.

    Args:
        None.

    Returns:
        EBGP: Returns a EBGP object.

    """

    asn_type: str = ""
    dual_asn: BgpDualASN = None
    multi_asn: BgpMultiASN = None
    auth_password: str = ""


class Overlay(BaseModel):
    """Overlay Model for an Overlay configuration.

    Args:
        None.

    Returns:
        Overlay: Returns a Overlay object.

    """

    name: str
    description: str = None
    bgp_type: Literal["internal", "external"]
    ibgp: IBGP = None
    ebgp: EBGP = None
    ipv4_address: ResourcePool
    keepalive_timer: int = 60
    holddown_timer: int = 180

    @root_validator(pre=True)
    def convert_values(cls, values: dict) -> dict:
        """check_redistribute_rm Convert values to expected ones.

        Args:
            cls: Initial instanciation.
            values: Initial values.

        Returns:
            new_values: Returned values.

        """
        new_values = values.copy()
        if values["bgp_type"] == "external" and not values.get("ebgp"):
            error_msg = "EBGP configuration is missing"
            raise ValueError(error_msg)
        if values["bgp_type"] == "internal" and not values.get("ibgp"):
            new_values["ibgp"]: dict = {}
            if values.get("spine_leaf_asn"):
                new_values["ibgp"]["spine_leaf_asn"] = values["spine_leaf_asn"]
            if values.get("rr_server"):
                new_values["ibgp"]["rr_server"] = values["rr_server"]
        if values.get("ipv4_address"):
            new_values["ipv4_address"] = {}
            new_values["ipv4_address"]["resource_pool_uuid"] = values["ipv4_address"]
        return new_values


class OverlayReapply(BaseModel):
    """OverlayReapply Model for a reapply of the Overlay configuration.

    Args:
        None.

    Returns:
        OverlayReapply: Returns a OverlayReapply object.

    """

    name: str
    description: str = None
    bgp_type: Literal["internal", "external"]
    ibgp: IBGP = {}
    ebgp: EBGP = {}
    ipv4_address: ResourcePool
    keepalive_timer: int = 60
    holddown_timer: int = 180
    update: bool = False


class Network(BaseModel):
    """Network Model for a AMD Network.

    Args:
        None.

    Returns:
        Network: Returns a Network object.

    """

    name: str
    vlan_id: int = Field(gt=1, lt=4094)
    max_cps_mode: Literal["enabled", "disabled", "unlimited"] | None = "disabled"
    max_cps: int | None = Field(default=None, gt=1000, lt=1000000)
    max_sessions_mode: Literal["enabled", "disabled", "unlimited"] | None = "disabled"
    max_sessions: int | None = Field(gt=10000, lt=5000000)
    connection_tracking_mode: bool | None = None
    allow_session_reuse: bool | None = None
    service_bypass: bool | None = False


class ActiveGateway(BaseModel):
    """ActiveGateway Model for an Active Gateway.

    Args:
        None.

    Returns:
        ActiveGateway: Returns a ActiveGateway object.

    """

    ipv4_address: str
    mac_address: str


class IPAddress(BaseModel):
    """IPAddress Model for an IP Address.

    Args:
        None.

    Returns:
        IPAddress: Returns a IPAddress object.

    """

    address: str
    prefix_length: int


class IPInterface(BaseModel):
    """IPInterface Model for an IP Interface.

    Args:
        None.

    Returns:
        IPInterface: Returns a IPInterface object.

    """

    name: str = None
    enable: bool = True
    if_type: Literal["vlan", "routed", "loopback", "evpn"]
    description: str = ""
    switch_uuid: str
    lag_uuid: str = None
    vlan: int = None
    loopback_type: Literal["generic", "evpn_vtep"] = None
    loopback_name: str = None
    vsx_shutdown_on_split: bool = False
    vsx_active_forwarding: bool = False
    active_gateway: ActiveGateway = None
    ipv4_primary_address: IPAddress
    ipv4_secondary_addresses: IPAddress = []
    local_proxy_arp_enabled: bool = False

    @root_validator(pre=True)
    def convert_values(cls, values: dict) -> dict:
        """convert_values Convert values to expected ones.

        Args:
            cls: Initial instanciation.
            values: Initial values.

        Returns:
            new_values: Returned values.

        """
        if values["if_type"] == "loopback" and not values.get("loopback_type"):
            values["loopback_type"] = "generic"
        if values["if_type"] == "loopback" and not values.get("loopback_name"):
            values["loopback_name"] = values["name"]
        if values["if_type"] != "loopback" and not values.get("name"):
            raise ValueError("Name is mandatory")
        return values


class OspfRedistribute(BaseModel):
    """OspfRedistribute Model for a Redistribution with OSPF.

    Args:
        None.

    Returns:
        OspfRedistribute: Returns a OspfRedistribute object.

    """

    redistribute_static: bool = False
    redistribute_connected: bool = True
    redistribute_local: bool = True
    redistribute_bgp: bool = False


class OspfRedistributeRouteMap(BaseModel):
    """OspfRedistributeRouteMap Model for Redistribution Route Map with OSPF.

    Args:
        None.

    Returns:
        OspfRedistributeRouteMap: Returns a OspfRedistributeRouteMap object.

    """

    redistribute_connected_route_map: str = ""
    redistribute_local_route_map: str = ""


class OspfProcessRedistributeRouteMap(BaseModel):
    """OspfProcessRedistributeRouteMap Model for a Redistribution Route Map.

    Args:
        None.

    Returns:
        OspfProcessRedistributeRouteMap: Returns an object.

    """

    process_id: int
    route_map: str


class OspfRouter(BaseModel):
    """OspfRouter Model for an OSPF Router.

    Args:
        None.

    Returns:
        OspfRouter: Returns a OspfRouter object.

    """

    name_prefix: str
    description: str = ""
    switch_uuids: List[str]
    enable: bool = True
    id: int = 1
    redistribute: OspfRedistribute = None
    redistribute_route_map: OspfRedistributeRouteMap = None
    maximum_paths: int = 8
    max_metric_router_lsa: bool = True
    max_metric_include_stub: bool = True
    max_metric_on_startup: int | None = None
    passive_interface_default: bool = True
    trap_enable: bool = True
    gr_ignore_lost_interface: bool = False
    gr_restart_interval: int | None = None
    distance: int | None = None
    default_metric: int | None = None
    default_information: Literal["disable", "originate", "always_originate"] | None = "disable"

    @root_validator(skip_on_failure=True)
    def check_redistribute_rm(cls, values: dict) -> dict:
        """check_redistribute_rm Check if Restribution Route Map is present.

        Args:
            cls: Initial instanciation.
            values: Initial values.

        Returns:
            values: Returned values.

        """
        if not values["redistribute_route_map"]:
            values["redistribute_route_map"] = {
                "redistribute_connected_route_map": "",
                "redistribute_local_route_map": "",
            }
        return values


class OspfArea(BaseModel):
    """OspfArea Model for an OSPF Area.

    Args:
        None.

    Returns:
        OspfArea: Returns a OspfArea object.

    """

    name: str
    description: str = ""
    area_id: int = 0
    area_type: Literal[
        "standard",
        "nssa",
        "stub",
        "stub_no_summary",
        "nssa_no_summary",
    ] = "standard"


class OspfInterface(BaseModel):
    """OspfInterface Model for an OSPF Interface.

    Args:
        None.

    Returns:
        OspfInterface: Returns a OspfInterface object.

    """

    if_uuid: str
    priority: int = 1
    hello_interval: int = 10
    dead_interval: int = 40
    mtu_size: int = 1500
    ignore_mtu_mismatch: bool = False
    passive_mode: bool = False
    authentication_value: str = ""
    md5_list: List[str] = []
    authentication_type: Literal["simple-text", "message-digest"] = "null"
    network_type: Literal[
        "ospf_iftype_pointopoint",
        "ospf_iftype_broadcast",
        "ospf_iftype_loopback",
        "ospf_iftype_none",
    ]
    bfd: int = False


class NetworkAddress(BaseModel):
    """NetworkAddress Model for a Network Address.

    Args:
        None.

    Returns:
        NetworkAddress: Returns a NetworkAddress object.

    """

    address: str
    prefix_length: int

    @root_validator(pre=True)
    def convert_values(cls, values: dict) -> dict:
        """check_redistribute_rm Convert values to expected ones.

        Args:
            cls: Initial instanciation.
            values: Initial values.

        Returns:
            values: Returned values.

        """
        values["ipv4_address"] = {}
        values["ipv4_address"]["resource_pool_uuid"] = values["ipv4_address"]
        return values


class StaticRoute(BaseModel):
    """StaticRoute Model for a StaticRoute.

    Args:
        None.

    Returns:
        StaticRoute: Returns a StaticRoute object.

    """

    destination: NetworkAddress | IPAddress
    next_hop: str
    name: str
    description: str = ""
    distance: int | None = Field(default=None, gt=0, lt=256)
    tag: int | None = Field(default=None, gt=0, lt=4294967295)
    switch_uuids: List[str]
    type: Literal["forward", "nullroute"] | None = "forward"


class BgpNetwork(BaseModel):
    """BgpNetwork Base Model allowing to represent a BGP Network.

    Args:
        None.

    Returns:
        BgpNetwork: Returns a BgpNetwork object.

    """

    network: NetworkAddress
    name: str
    description: str = ""
    route_map: str


class BgpNeighbor(BaseModel):
    """BgpNeighbor Base Model allowing to represent a BGP Neighbor.

    Args:
        None.

    Returns:
        BgpNeighbor: Returns a BgpNeighbor object.

    """

    uuid: str = None
    name: str
    description: str = ""
    neighbor_as_number: str
    neighbor_ip_address: str
    route_reflector_client: bool = False
    soft_reconfiguration_inbound: bool = False
    weight: int = 0
    auth_password: str = None
    keepalive_timer: int = 60
    holddown_timer: int = 180
    neighbor_type: Literal["ibgp", "ebgp"] = None
    address_families: List[Literal["evpn", "ipv4", "ipv6", "vpnv4"]]
    external_bgp_multihop: int = None
    update_source_address: str = None
    update_source_interface: str = None
    default_originate: int = None
    admin_state_enable: bool = True
    fall_over: bool = True
    local_as: str = ""
    remove_private_as: bool = False
    bfd_enable: bool = False
    allowas_in: int = 1
    route_map_in: str = ""
    route_map_out: str = ""
    route_map_in_ip: str = None
    route_map_out_ip: str = None
    send_community_ip: Literal["standard", "extended", "both"] = None
    send_community_evpn: Literal["standard", "extended", "both"] = None


class BgpConfig(BaseModel):
    """BgpConfig Base Model allowing to represent a BGP Config.

    Args:
        None.

    Returns:
        BgpConfig: Returns a BgpConfig object.

    """

    switch_uuid: str
    name: str
    description: str = ""
    networks: List[BgpNetwork] = []
    redistribute_static: bool = False
    redistribute_ospf: bool = False
    redistribute_connected: bool = True
    redistribute_loopback: bool = False
    enable: bool = True
    bestpath: bool = True
    fast_external_fallover: bool = True
    trap_enable: bool = False
    log_neighbor_changes: bool = True
    deterministic_med: bool = True
    always_compare_med: bool = True
    router_id: str
    keepalive_timer: int = 60
    holddown_timer: int = 180
    neighbors: List[BgpNeighbor] = []
    as_number: str
    maximum_paths: int = 8
    redistribute_connected_route_map: str = ""
    redistribute_ospf_route_map: str = None
    redistribute_local_route_map: str = None
    redistribute_static_route_map: str = None
    redistribute_ospf_process_route_map: List[OspfProcessRedistributeRouteMap] = []

    @root_validator(pre=True)
    def convert_values(cls, values: dict) -> dict:
        """check_redistribute_rm Convert values to expected ones.

        Args:
            cls: Initial instanciation.
            values: Initial values.

        Returns:
            values: Returned values.

        """
        if values.get("as_number"):
            values["as_number"] = str(values["as_number"])
        return values


class BgpSwitchConfigList(BaseModel):

    switches: List[BgpConfig]
