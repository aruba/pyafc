# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import utils
from pyafc.fabric import fabric
from pyafc.services import models
from pyafc.switches import switches


class Checkpoint:
    def __init__(self, client, name: str, **kwargs: dict) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the checkpoint.

        Returns:
            existing_eg (bool): True if available, False if not.

        """
        self.client = client
        self.uuid = None
        self.name = name
        self.existing_cp = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details Find checkpoint UUID.

        Returns:
            If found, the UUID is set as a Class attribute, else false.

        """
        checkpoint_request = self.client.get("switches/checkpoint")
        for checkpoint in checkpoint_request.json()["result"]:
            if checkpoint["name"] == self.name:
                self.uuid = checkpoint["uuid"]
                for item, value in checkpoint.items():
                    setattr(self, item, value)
                return True
        return False

    @staticmethod
    def get_checkpoint(
        client, name: str, type: str | None = None
    ) -> dict | bool:
        """get_checkpoint Get checkoint.

        Args:
            client (Any): AFC Connection object.
            name (str): Checkpoint name.
            type (str): Checkpoint type.

        Returns:
            If found, return checkpoint name else false.

        """
        uri_checkpoint = "switches/checkpoint"

        checkpoint_request = client.get(uri_checkpoint)

        for pool in checkpoint_request.json()["result"]:
            if pool["name"] == name:
                return pool
        return False

    def create_checkpoint(self, **kwargs: dict) -> tuple:
        """create_checkpoint Creates a Checkpoint either scheduled or now.

        Args:
            description: str = ""
            checkpoint_type (str, optional) = One of:
                - 'One-Time'
                - 'System'
                Defaults to 'One-Time'
            fabrics (list, optional) = List of Fabrics
            switches (list, optional) = List of Switches

        Example:
            checkpoint_data = {
                "fabrics": ["DC1"],
            }

            checkpoint_instance = checkpoints.Checkpoint(afc_instance.client, name="New_CP")
            checkpoint_instance.create_checkpoint(**checkpoint_data,)

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed something.

        """
        _message = ""
        _status = False
        _changed = False

        if kwargs.get("rule"):
            _message, _status, _changed = self._create_scheduled_checkpoint(
                kwargs,
            )
        else:
            _message, _status, _changed = self._create_checkpoint(
                kwargs,
            )

        return _message, _status, _changed

    def _create_checkpoint(self, values: dict) -> tuple:
        """_create_checkpoint Creates a Checkpoint immediately.

        Args:
            values (dict): Checkpoint data.

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        if values.get("fabrics"):
            values["fabric_uuids"] = []
            for fab in values["fabrics"]:
                fab_uuid = fabric.Fabric.get_fabric_uuid(self.client, fab)
                values["fabric_uuids"].append(fab_uuid)

        if values.get("switches"):
            values["switch_uuids"] = []
            for switch in values["fabrics"]:
                switch_uuid = switches.Switch.get_switch_uuid(
                    self.client,
                    switch,
                )
                values["switch_uuids"].append(switch_uuid)

        try:
            if self.existing_cp:
                _message = (f"Checkpoint {self.name} already exists."
                            "No action taken")
                _status = True
            else:
                if "name" in values:
                    del values["name"]

                data = models.Checkpoint(name=self.name, **values)

                add_request = self.client.post(
                    "switches/checkpoint",
                    data=json.dumps(data.dict()),
                )
                if add_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully created the checkpoint {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]
        except Exception:
            _message = (
                f"An exception occurred while creating checkpoint {self.name}"
            )

        return _message, _status, _changed

    def _create_scheduled_checkpoint(self, values: dict) -> tuple:
        """_create_scheduled_checkpoint Creates a scheduled Checkpoint.

        Args:
            values (dict): Checkpoint data with schedule.

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_cp:
                _message = (f"Checkpoint {self.name} already exists."
                            "No action taken")
                _status = True
            else:
                rule = models.ScheduleRule(**values["rule"])
                crule = models.CheckpointRule(rule=rule)
                data = models.ScheduledCheckpoint(
                    name_prefix=self.name, **values, checkpoint_rule=crule
                )

                add_request = self.client.post(
                    "switches/checkpoint/schedules",
                    data=json.dumps(data.dict(exclude_none=True)),
                )
                if add_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully created the scheduled "
                        f"checkpoint {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]
        except Exception:
            _message = (
                f"An exception occurred while creating scheduled "
                f"checkpoint {self.name}"
            )

        return _message, _status, _changed

    def rollback_checkpoint(self, **kwargs: dict) -> tuple:
        """rollback_checkpoint Rolls back a Checkpoint.

        Args:
            checkpoint (str, optional) = Name of the checkpoint
            snapshots (list, optional) = List of snapshots
            overwrite_startup_config (bool, optional) = Save config
                once injected.
                Defaults to True

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        if kwargs.get("snapshots"):
            snapshots_list = []
            for device, device_values in kwargs["snapshots"].items():
                switch_uuid = switches.Switch.get_switch_uuid(
                    self.client,
                    device,
                )
                fab_uuid = fabric.Fabric.get_fabric_uuid(
                    self.client,
                    device_values["fabric"],
                )
                snapshot_request = self.client.get(
                    "switches/checkpoint/snapshot",
                )
                for checkpoint in snapshot_request.json()["result"]:
                    if checkpoint["checkpoint_uuid"] == self.uuid:
                        snapshots_list = [
                            snapshot["snapshot_uuid"]
                            for snapshot in checkpoint["config_snapshots"]
                            if (snapshot["fabric_uuid"] == fab_uuid)
                            and (snapshot["switch_uuid"] == switch_uuid)
                        ]
            config = models.RollbackConfig(snapshots=snapshots_list)
        else:
            config = models.RollbackConfig(checkpoint=self.uuid)

        rollback = models.RollbackValues(config=config)
        data = models.Rollback(rollback=rollback)

        add_request = self.client.post(
            "switches/checkpoint/rollback",
            data=json.dumps(data.dict(exclude_none=True)),
        )
        if add_request.status_code in utils.response_ok:
            _message = f"Successfully rolled back the checkpoint {self.name}"
            _status = True
            _changed = True
        else:
            _message = add_request.json()["result"]

        return _message, _status, _changed
