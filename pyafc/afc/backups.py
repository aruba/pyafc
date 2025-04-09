# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Utility functions and classes Overlay management.

This module provides:
- create_backup: create backup;
- create_scheduled_backup: create scheduled backup.
"""

from __future__ import annotations

import json

from pyafc.afc import models
from pyafc.common import utils


class Backup:

    def __init__(self) -> None:
        """__init__ Init Method."""

    def create_backup(self, **kwargs: dict) -> tuple:
        """create_backup Create an AFC Backup.

        Args:
            name (str): backup name.
            retention_hours (int): between 0 and 8760. Defaults to 0
            retention_unit (str): One of :
                - "hour"
                - "day"
                - "week"
                - "month"
                Defaults to "hours
            include_psm_snapshot (bool): Defaults to True

        Example:
            backup_instance = backups.Backup(afc_instance.client, name="New_Backup")
            backup_instance.create_backup()

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            data = models.Backup(**kwargs)
            uri_backup = "/backups"
            backup_request = self.client.post(
                uri_backup,
                data=json.dumps(data.dict(exclude_none=True)),
            )

            if backup_request.status_code in utils.response_ok:
                _message = "Successfully launch Backup Creation"
                _status = True
                _changed = True
            else:
                _message = backup_request.json()["result"]
        except Exception as exc:
            _message = f"An exception {exc} occurred"

        return _message, _status, _changed

    def create_scheduled_backup(self, **kwargs: dict) -> tuple:
        """create_scheduled_backup Create a Scheduled AFC Backup.

        Args:
            name (str): backup name.
            description (str): backup description
            rules (dict): backup rule. Please check example.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            kwargs["rules"] = [kwargs["rules"]]
            data = models.ScheduledBackup(**kwargs)

            uri_backup = "/backups/schedules"
            backup_request = self.client.post(
                uri_backup,
                data=json.dumps(data.dict(exclude_none=True)),
            )

            if backup_request.status_code in utils.response_ok:
                _message = "Successfully Scheduled Backup"
                _status = True
                _changed = True
            else:
                _message = backup_request.json()["result"]
        except Exception as exc:
            _message = f"An exception {exc} occurred"

        return _message, _status, _changed
