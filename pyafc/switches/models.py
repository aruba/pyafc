# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Models file is used to create a dictionary that is later used."""

from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel


class Switch(BaseModel):
    """Switch Model for a Switch.

    Args:
        None.

    Returns:
        Switch: Returns a Switch object.

    """

    description: str | None = None
    name: str | None = None
    exclude_from_dsm: bool | None = None
    fabric: str | None = None
    role: str | None = None
    hostname: str | None = None
    auto_save_interval: int | None = None
    icmp_redirect_disable: bool | None = None
    profile: (
        Literal[
            "Leaf",
            "Spine",
            "L3-agg",
            "L3-core",
            "Core-Spine",
            "Leaf-Extended",
            "Aggregation-Leaf",
            "Basic",
        ]
        | None
    ) = None
    uplink_to_uplink: bool | None = None


class SwitchDiscovery(BaseModel):
    """SwitchDiscovery Model for a Switch Discovery.

    Args:
        None.

    Returns:
        SwitchDiscovery: Returns a SwitchDiscovery object.

    """

    switches: List[str]
    admin_passwd: str
    afc_admin_passwd: str


class CLI(BaseModel):
    """CLI Model for CLI on Switch.

    Args:
        None.

    Returns:
        CLI: Returns a CLI object.

    """

    switch_names: List[str] = []
    switch_uuids: List[str] = []
    commands: List[str]


class FirmwareSwitchesGroup(BaseModel):
    """FirmwareSwitchesGroup Model for Switches Upgrades.

    Args:
        None.

    Returns:
        FirmwareSwitchesGroup: Returns a FirmwareSwitchesGroup object.

    """

    uuid: str
    boot_partition: Literal["primary", "secondary"]


class FirmwareSwitches(BaseModel):
    """FirmwareSwitches Model for a list of Switches to upgrade.

    Args:
        None.

    Returns:
        FirmwareSwitches: Returns a FirmwareSwitches object.

    """

    switches: List[FirmwareSwitchesGroup]


class FirmwareStaging(BaseModel):
    """FirmwareStaging Model for firmware staging on a group of Switches.

    Args:
        None.

    Returns:
        FirmwareStaging: Returns a FirmwareStaging object.

    """

    groups: List[FirmwareSwitches]
    upgrade_type: Literal["immediate", "sequenced"] = "immediate"


class Reboot(BaseModel):
    """Reboot Model for Switches reboot.

    Args:
        None.

    Returns:
        Reboot: Returns a Reboot object.

    """

    uuid: str
    boot_partition: Literal["primary", "secondary"] = "primary"


class RebootSwitches(BaseModel):
    """RebootSwitches Root Model for Switches reboot.

    Args:
        None.

    Returns:
        RebootSwitches: Returns a RebootSwitches object.

    """

    switches: List[Reboot]


class ReconcileSwitches(BaseModel):
    """ReconcileSwitches Root Model for Switches Reconciliation.

    Args:
        None.

    Returns:
        ReconcileSwitches: Returns a ReconcileSwitches object.

    """

    switches: List[str]


class SaveConfigSwitches(BaseModel):
    """SaveConfigSwitches Root Model for Switches to save config on.

    Args:
        None.

    Returns:
        SaveConfigSwitches: Returns a SaveConfigSwitches object.

    """

    switches: List[str]
