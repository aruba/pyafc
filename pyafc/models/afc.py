# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from typing import List

from pydantic import BaseModel

"""Models file is used to create a dictionary that is later used."""


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
