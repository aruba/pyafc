# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from typing import List, Literal

from pydantic import BaseModel, Field, root_validator

"""Models file is used to create a dictionary needed for request."""


class HealthIssues(BaseModel):
    description_id: str
    description: str
    resolution: str


class Health(BaseModel):
    status: str
    health_issues: List[HealthIssues]


class Afc(BaseModel):
    uuid: str
    name: str = None
    description: str = None
    health: Health
    software: str
    qualified_cx_api_versions: List[str]


class Backup(BaseModel):

    name_prefix: str
    retention_hours: int | None = Field(default=0, lt=8760)
    retention_unit: Literal["hour", "day", "week", "month"] | None = "hour"
    include_psm_snapshot: bool | None = True

    @root_validator(pre=True)
    def convert_values(cls, values: dict) -> dict:
        """convert_values Convert values to expected ones.

        Args:
            cls: Initial instanciation.
            values: Initial values.

        Returns:
            new_values: Returned values.

        """
        if values.get("name"):
            values["name_prefix"] = values["name"]
        return values


class BackupRule(BaseModel):

    name: str
    minute: str
    hour: str
    day_of_month: str
    month: str
    day_of_week: str
    year: str
    retention_hours: int | None = Field(default=0, lt=8760)
    retention_unit: Literal["hour", "day", "week", "month"] | None = "hour"
    include_psm_snapshot: bool | None = True

    @root_validator(pre=True)
    def convert_values(cls, values: dict) -> dict:
        """convert_values Convert values to expected ones.

        Args:
            cls: Initial instanciation.
            values: Initial values.

        Returns:
            new_values: Returned values.

        """

        values["minute"] = (
            str(values["minute"]) if values.get("minute") else "*"
        )
        values["hour"] = str(values["hour"]) if values.get("hour") else "*"
        values["day_of_week"] = (
            str(values["day_of_week"]) if values.get("day_of_week") else "*"
        )
        values["month"] = str(values["month"]) if values.get("month") else "*"
        values["day_of_month"] = (
            str(values["day_of_month"]) if values.get("day_of_month") else "*"
        )
        values["year"] = str(values["year"]) if values.get("year") else "*"
        return values


class ScheduledBackup(BaseModel):

    name: str
    description: str | None = ""
    rules: List[BackupRule]
