# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Utility functions and classes Overlay management.

This module provides:
- get_overlay: get overlay information and current configuration;
- create_overderlay: create an overlay for the given VRF.
- delete_overderlay: delete the overlay for the given VRF.
"""

from __future__ import annotations

import json

from pyafc.common import utils


class License:
    def __init__(self) -> None:
        """__init__ Init Method."""

    def push_license(self, lic: str) -> tuple:
        """push_license Push a new license on AFC.

        Args:
            lic (str): license key.

        Example:
            afc_instance.push_license(lic=<your_license>)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            uri_license = "/licenses"
            license_request = self.client.post(
                uri_license,
                data=json.dumps(lic),
            )

            if license_request.status_code in utils.response_ok:
                _message = "Successfully pushed the new license"
                _status = True
                _changed = True
            else:
                if "already exists" in license_request.json()["result"]:
                    _status = True
                _message = license_request.json()["result"]
        except Exception as exc:
            _message = f"An exception {exc} occurred"

        return _message, _status, _changed

    def delete_license(self, lic: str) -> tuple:
        """delete_license Delete a license on AFC.

        Args:
            lic (str): license key.

        Example:
            afc_instance.delete_license(lic=<your_license_key>)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            uri_license = f"/licenses/{lic}"
            license_request = self.client.delete(uri_license)

            if license_request.status_code in utils.response_ok:
                _message = "Successfully deleted the license"
                _status = True
                _changed = True
            else:
                if "non-existent license" in license_request.json()["result"]:
                    _status = True
                _message = license_request.json()["result"]
        except Exception as exc:
            _message = f"An exception {exc} occurred"

        return _message, _status, _changed
