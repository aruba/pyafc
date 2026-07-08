# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from ipaddress import IPv4Address, IPv6Address
from typing import Literal

from pydantic import BaseModel, model_validator

"""Models file is used to create a dictionary that is later used."""

Days_Of_The_Week = {
    "sunday": "0",
    "monday": "1",
    "thursday": "2",
    "wednesday": "3",
    "tuesday": "4",
    "friday": "5",
    "saturday": "6",
}


class ResourcesPool(BaseModel):
    name: str
    description: str = ""
    type: Literal["MAC", "IPv4"]
    pool_ranges: str = ""

    @model_validator(mode="before")
    @classmethod
    def convert_to_str(cls, values):
        if isinstance(values, dict) and values.get("pool_ranges") is not None:
            values["pool_ranges"] = str(values["pool_ranges"])
        return values


class NtpEntry(BaseModel):
    server: str
    burst_mode: Literal["burst", "iburst"] = None
    prefer: bool = True


class Ntp(BaseModel):
    name: str
    description: str = ""
    fabric_uuids: list[str] = []
    switch_uuids: list[str] = []
    entry_list: list[NtpEntry]

    @model_validator(mode="before")
    @classmethod
    def convert_servers(cls, values):
        if values.get("servers"):
            values["entry_list"] = values["servers"]
        else:
            raise ValueError("Servers are missing")
        return values


class Dns(BaseModel):
    name: str
    description: str = ""
    domain_name: str
    name_servers: list[str] = []
    domain_list: list[str] = []
    management_software: bool = False
    fabric_uuids: list[str] = []
    switch_uuids: list[str] = []

    @model_validator(mode="before")
    @classmethod
    def check_domains(cls, values):
        if not values.get("domain_name") and not values.get("domain_list"):
            raise ValueError("Domain Name or Domain List must be specified")
        return values


class Checkpoint(BaseModel):
    name: str
    description: str = ""
    checkpoint_type: Literal["One-Time", "System"] = "One-Time"
    fabric_uuids: list[str] = []
    switch_uuids: list[str] = []

    @model_validator(mode="before")
    @classmethod
    def check_domains(cls, values):
        if not values.get("fabric_uuids") and not values.get("switch_uuids"):
            raise ValueError("Fabrics or Switches must be specified")
        return values


class ScheduleRule(BaseModel):
    hour: str = "*"
    name: str = ""
    year: str = "*"
    month: str = "*"
    minute: str = "*"
    day_of_week: str = "*"
    day_of_month: str = "*"

    @model_validator(mode="before")
    @classmethod
    def convert_days_week(cls, values):
        if values.get("day_of_week"):
            values["day_of_week"] = Days_Of_The_Week[values["day_of_week"]]
        return values


class CheckpointRule(BaseModel):
    start_time: int = 0
    rule: ScheduleRule


class ScheduledCheckpoint(BaseModel):
    name_prefix: str
    description: str = ""
    scheduler_operation: Literal["START", "STOP"] = "START"
    checkpoint_rule: CheckpointRule

    @model_validator(mode="before")
    @classmethod
    def convert_values(cls, values):
        if values.get("enable"):
            values["scheduler_operation"] = (
                "START" if values["enable"] else "STOP"
            )
        return values


class RollbackConfig(BaseModel):
    checkpoint: str = None
    snapshots: list[str] = None
    overwrite_startup_config: bool = True


class RollbackValues(BaseModel):
    config: RollbackConfig


class Rollback(BaseModel):
    rollback_type: Literal["Config", "Image", "Config_Image"] = "Config"
    rollback: RollbackValues

    @model_validator(mode="before")
    @classmethod
    def convert_type(cls, values):
        if values.get("rollback_type"):
            values["rollback_type"] = values["rollback_type"].title()
        return values


class RadiusSourceConfig(BaseModel):
    port: int
    server: str
    secret: str


class RadiusSource(BaseModel):
    name: str
    description: str = ""
    config: RadiusSourceConfig


class ApplyRadius(BaseModel):
    radius_uuid: str
    fabric_uuids: list[str] = None
    switch_uuids: list[str] = None

    @model_validator(mode="before")
    @classmethod
    def check_uuids(cls, values):
        if not values.get("fabric_uuids") and not values.get("switch_uuids"):
            raise ValueError("Fabrics or Switch must be specified")
        if values.get("fabric_uuids") and values.get("switch_uuids"):
            raise ValueError(
                "Fabrics and Switches cannot be used in the same request"
            )
        return values


class SyslogEntry(BaseModel):
    host: IPv4Address
    port: int
    severity: Literal[
        "EMERG", "ALERT", "CRIT", "ERROR", "WARNING", "NOTICE", "INFO", "DEBUG"
    ] = "INFO"
    include_auditable_events: bool = True
    unsecure_tls_renegotiation: bool = True
    tls_auth_mode: Literal["certificate", "subject-name"] = None
    transport: Literal["udp", "tcp", "tls"] = "udp"

    @model_validator(mode="after")
    def convert_ip(self):
        self.host = str(self.host)
        return self


class SyslogPersistentStorage(BaseModel):
    severity: Literal[
        "EMERG", "ALERT", "CRIT", "ERROR", "WARNING", "NOTICE", "INFO", "DEBUG"
    ] = "INFO"
    enable: bool = True


class Syslog(BaseModel):
    name: str
    description: str = ""
    entry_list: list[SyslogEntry]
    fabric_uuids: list[str] = []
    switch_uuids: list[str] = []
    management_software: bool = False
    facility: Literal[
        "LOCAL0",
        "LOCAL1",
        "LOCAL2",
        "LOCAL3",
        "LOCAL4",
        "LOCAL5",
        "LOCAL6",
        "LOCAL7",
    ] = "LOCAL7"
    logging_persistent_storage: SyslogPersistentStorage = (
        SyslogPersistentStorage()
    )


class Sflow(BaseModel):
    name: str
    description: str = ""
    fabric_uuids: list[str] = []
    switch_uuids: list[str] = []
    enable_sflow: bool = True
    polling_interval: int = 20
    sampling_rate: int = 20000
    source_ip_address: str = None
    source_namespace: str = "management"
    collectors: list[dict] = []


class Stp(BaseModel):
    name: str
    description: str = ""
    config_type: Literal["mstp", "rpvst"] = "mstp"
    configuration: dict = {}


class SnmpUsers(BaseModel):
    name: str
    level: Literal["noauth", "auth", "priv"]
    auth_type: Literal["SHA", "MD5"] = "SHA"
    priv_type: Literal["AES", "DES"] = "AES"
    context: str = None
    auth_pass: str = None
    priv_pass: str = None


class SnmpTrapServer(BaseModel):
    address: IPv4Address
    community: str

    @model_validator(mode="after")
    def convert_ip(self):
        self.address = str(self.address)
        return self


class Snmp(BaseModel):
    name: str
    description: str = ""
    enable: bool = True
    location: str = None
    contact: str = None
    community: str = None
    agent_port: int | None = 161
    trap_port: int = None
    users: list[SnmpUsers] | None = None
    trap_sink: list[SnmpTrapServer] | None = None
    fabric_uuids: list[str] = []
    switch_uuids: list[str] = []


class DhcpRelay(BaseModel):
    name: str
    description: str = ""
    vlans: str
    gateway_address: str = None
    ipv4_dhcp_server_addresses: list[IPv4Address] = []
    ipv6_dhcp_server_addresses: list[IPv6Address] = []
    ipv6_dhcp_mcast_server_addresses: list[IPv6Address] = []
    v4relay_option82_policy: Literal["replace", "drop", "keep"] = "replace"
    v4relay_option82_validation: bool = False
    v4relay_source_interface: bool = False
    fabric_uuids: list[str] = []
    switch_uuids: list[str] = []

    @model_validator(mode="after")
    def convert_ip(self):
        if self.ipv4_dhcp_server_addresses:
            self.ipv4_dhcp_server_addresses = [
                str(ip) for ip in self.ipv4_dhcp_server_addresses
            ]
        if self.ipv6_dhcp_server_addresses:
            self.ipv6_dhcp_server_addresses = [
                str(ip) for ip in self.ipv6_dhcp_server_addresses
            ]
        if self.ipv6_dhcp_mcast_server_addresses:
            self.ipv6_dhcp_mcast_server_addresses = [
                str(ip) for ip in self.ipv6_dhcp_mcast_server_addresses
            ]
        return self
