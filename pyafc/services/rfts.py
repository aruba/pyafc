# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Utility functions and classes for Remote File Transfer Server management.

A Remote File Transfer Server (RFTS) defines an SFTP/SCP endpoint that HPE
Aruba Networking Fabric Composer uses to transfer files (for instance backup
archives).

This module provides:
- get_rfts: Get a specific Remote File Transfer Server by its name
- create_rfts: Create a Remote File Transfer Server
- update_rfts: Update an existing Remote File Transfer Server
- delete_rfts: Delete a Remote File Transfer Server
"""

from __future__ import annotations

import json

from pydantic import ValidationError

from pyafc.common import exceptions, utils, versioning
from pyafc.services import models


class Rfts:

    # Human-readable feature name used in 'not supported' messages.
    _FEATURE = "Remote file transfer server management"

    # AFC endpoint managing Remote File Transfer Servers.
    _URI = "remote_file_transfer_server"

    # Fields (non-secret) used to decide whether an update is required.
    _COMPARABLE = (
        "name",
        "description",
        "remote_file_server_hostname",
        "protocol",
        "username",
        "location",
    )

    def __init__(self, client, name: str, **kwargs: dict) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the Remote File Transfer Server.

        Returns:
            existing_rfts (bool): True if available, False if not.

        """
        self.client = client
        self.uuid = None
        self.name = name
        self.supported = True
        self.existing_rfts = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details Find the RFTS UUID and details.

        Returns:
            True if found and UUID is set as the class attribute, else False.
            Sets self.supported to False when the RFTS API is not available
            on the running AFC version.

        """
        request = self.client.get(self._URI)
        if not versioning.is_supported_response(request):
            self.supported = False
            return False
        for rfts in request.json()["result"]:
            if rfts["name"] == self.name:
                self.uuid = rfts["uuid"]
                for item, value in rfts.items():
                    setattr(self, item, value)
                return True
        return False

    @staticmethod
    def get_rfts(client, name: str) -> dict | bool:
        """get_rfts Find a Remote File Transfer Server by name.

        Args:
            client (Any): AFC Connection object.
            name (str): Name of the Remote File Transfer Server.

        Returns:
            RFTS data in JSON format if found, else False.

        """
        request = client.get(Rfts._URI)
        versioning.ensure_supported(request, Rfts._FEATURE, client)
        for rfts in request.json()["result"]:
            if rfts["name"] == name:
                return rfts
        return False

    def create_rfts(self, **kwargs: dict) -> tuple:
        """create_rfts Create a Remote File Transfer Server.

        Args:
            description (str, optional) = Description of the RFTS.
            remote_file_server_hostname (str) = Hostname or IP address of the
                remote host.
            protocol (str) = File transfer protocol, one of 'sftp' or 'scp'.
            username (str) = Username of the RFTS.
            password (str) = Password of the RFTS for the above username.
            location (str, optional) = Base folder where files are copied.

        Example:
            rfts_data = {
                "remote_file_server_hostname": "10.100.100.50",
                "protocol": "sftp",
                "username": "backup",
                "password": "backup_password",
                "location": "/backups",
            }

            rfts_instance = rfts.Rfts(afc_instance.client, name="New_RFTS")
            rfts_instance.create_rfts(**rfts_data,)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if not self.supported:
                return (
                    versioning.not_supported_message(
                        self._FEATURE, self.client,
                    ),
                    False,
                    False,
                )

            if self.existing_rfts:
                _message = (
                    f"Remote file transfer server {self.name} already "
                    "exists. No action taken"
                )
                _status = True
            else:
                if "name" in kwargs:
                    del kwargs["name"]

                data = models.Rfts(name=self.name, **kwargs)
                add_request = self.client.post(
                    self._URI,
                    data=json.dumps(data.model_dump(exclude_none=True)),
                )
                versioning.ensure_supported(
                    add_request, self._FEATURE, self.client,
                )
                if add_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully created remote file transfer "
                        f"server {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]

        except exceptions.FeatureNotSupported as exc:
            _message = str(exc)
        except ValidationError as exc:
            _message = f"An exception {exc} occurred"
        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while creating remote "
                f"file transfer server {self.name}"
            )

        return _message, _status, _changed

    def update_rfts(self, **kwargs: dict) -> tuple:
        """update_rfts Update an existing Remote File Transfer Server.

        Only the non-secret fields are used to decide whether an update is
        required. When an update is applied, the password is included in the
        request when provided so that it is not cleared by the full-replace
        PUT operation.

        Args:
            description (str, optional) = Description of the RFTS.
            remote_file_server_hostname (str, optional) = Hostname or IP.
            protocol (str, optional) = 'sftp' or 'scp'.
            username (str, optional) = Username of the RFTS.
            password (str, optional) = Password of the RFTS.
            location (str, optional) = Base folder where files are copied.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if not self.supported:
                return (
                    versioning.not_supported_message(
                        self._FEATURE, self.client,
                    ),
                    False,
                    False,
                )

            if not self.existing_rfts:
                return (
                    f"Remote file transfer server {self.name} does not "
                    "exist. No action taken",
                    False,
                    False,
                )

            changes = {
                field: kwargs[field]
                for field in self._COMPARABLE
                if kwargs.get(field) is not None
                and getattr(self, field, None) != kwargs[field]
            }

            if not changes:
                return (
                    f"Remote file transfer server {self.name} is already "
                    "up to date. No action taken",
                    True,
                    False,
                )

            payload = {
                "name": self.name,
                "remote_file_server_hostname": getattr(
                    self, "remote_file_server_hostname", None,
                ),
                "protocol": getattr(self, "protocol", None),
                "username": getattr(self, "username", None),
                "description": getattr(self, "description", None),
                "location": getattr(self, "location", None),
            }
            payload.update(changes)
            if kwargs.get("password") is not None:
                payload["password"] = kwargs["password"]

            data = models.Rfts(**payload)
            update_request = self.client.put(
                f"{self._URI}/{self.uuid}",
                data=json.dumps(data.model_dump(exclude_none=True)),
            )
            versioning.ensure_supported(
                update_request, self._FEATURE, self.client,
            )
            if update_request.status_code in utils.response_ok:
                _message = (
                    f"Successfully updated remote file transfer "
                    f"server {self.name}"
                )
                _status = True
                _changed = True
            else:
                _message = update_request.json()["result"]

        except exceptions.FeatureNotSupported as exc:
            _message = str(exc)
        except ValidationError as exc:
            _message = f"An exception {exc} occurred"
        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while updating remote "
                f"file transfer server {self.name}"
            )

        return _message, _status, _changed

    def delete_rfts(self) -> tuple:
        """delete_rfts Delete a Remote File Transfer Server.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is deleted, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if not self.supported:
                return (
                    versioning.not_supported_message(
                        self._FEATURE, self.client,
                    ),
                    False,
                    False,
                )

            if self.existing_rfts:
                delete_request = self.client.delete(
                    f"{self._URI}/{self.uuid}",
                )
                versioning.ensure_supported(
                    delete_request, self._FEATURE, self.client,
                )
                if delete_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully deleted remote file transfer "
                        f"server {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = delete_request.json()["result"]
            else:
                _message = (
                    f"Remote file transfer server {self.name} does not "
                    "exist. No action taken"
                )
                _status = True

        except exceptions.FeatureNotSupported as exc:
            _message = str(exc)
        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while deleting remote "
                f"file transfer server {self.name}"
            )

        return _message, _status, _changed
