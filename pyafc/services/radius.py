# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pydantic import ValidationError

from pyafc.common import utils
from pyafc.services import models


class Radius:
    def __init__(self, client, name: str, **kwargs: dict) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the Radius.

        Returns:
            existing_eg (bool): True if available, False if not.

        """
        self.client = client
        self.uuid = None
        self.name = name
        self.existing_radius = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details Find Radius Config UUID.

        Args:
            client (Any): AFC Connection object.

        Returns:
            True if found and UUID is set as the class attribute, else False.

        """
        radius_request = self.client.get("auth/sources?type=radius")
        for srv in radius_request.json()["result"]:
            if srv["name"] == self.name:
                self.uuid = srv["uuid"]
                for item, value in srv.items():
                    setattr(self, item, value)
                return True
        return False

    @staticmethod
    def get_radius(client, name: str, type: str | None) -> dict | bool:
        """get_radius Get RADIUS configuration.

        Args:
            client (Any): AFC Connection object.
            name (str): RADIUS configuration name.
            type (str): Radius configuration type.

        Returns:
            Returns radius configuration if found or False if not found.

        """
        radius_request = client.get("auth/sources?type=radius")

        for srv in radius_request.json()["result"]:
            if srv["name"] == name:
                return srv
        return False

    def create_radius(self, **kwargs: dict) -> tuple:
        """create_radius Create RADIUS configuration.

        Args:
            description (str, optional) = Description
            fabrics (list, optional) = List of Fabrics
            switches (list, optional) = List of Switches
            config (dict) = Radius Config. Check example

        Example:
            radius_data = {
                "fabrics": ["DC1"],
                "config": {
                            "secret": "Test",
                            "server": "192.16.56.12",
                            "port": 1812,
                        }
                    }

            radius_instance = radius.Radius(afc_instance.client, name="New_RADIUS")
            radius_instance.create_radius(**radius_data,)

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_radius:
                _message = (
                    f"Radius configuration {self.name} already"
                    " exists. No action taken"
                )
                _status = True
            else:
                if "name" in kwargs:
                    del kwargs["name"]

                data = models.RadiusSource(name=self.name, **kwargs)

                add_request = self.client.post(
                    "auth/sources/radius",
                    data=json.dumps(data.dict(exclude_none=True)),
                )
                if add_request.status_code in utils.response_ok:
                    _message = (
                        "Successfully added the "
                        f"Radius configuration {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]
        except ValidationError:
            _message = (
                "An exception occurred while creating radius "
                f"configuration {self.name} - Check your data"
            )
        except Exception:
            _message = (
                "An exception occurred while creating "
                f"radius configuration {self.name}"
            )

        return _message, _status, _changed

    def delete_radius(self) -> tuple:
        """delete_radius Delete RADIUS configuration.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if not self.existing_radius:
                _message = (
                    f"Radius configuratoin {self.name} does "
                    "not exist. No action taken."
                )
                _status = True
            else:
                delete_request = self.client.delete(
                    f"auth/sources/{self.uuid}",
                )

                if delete_request.status_code in utils.response_ok:
                    _message = (
                        "Successfully deleted the RADIUS "
                        f"configuration {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = delete_request.json()["result"]

        except Exception as exc:
            _message = (
                f"An exceoption {exc} occurred while deleting "
                f"RADIUS configuration {self.name}"
            )

        return _message, _status, _changed

    def apply_radius(self, **kwargs: dict) -> tuple:
        """apply_radius Apply RADIUS configuration.

        Args:
            kwargs (dict): RADIUS configuration data and targets.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False
        values = kwargs

        try:
            if self.existing_radius:
                values["radius_uuid"] = self.uuid

                values = utils.populate_list_fabrics_switches(
                    self.client,
                    values,
                )

                data = models.ApplyRadius(**values)

                add_request = self.client.post(
                    "radius",
                    data=json.dumps(data.dict(exclude_none=True)),
                )
                if add_request.status_code in utils.response_ok:
                    _message = (
                        "Successfully applied RADIUS configuration "
                        f"{self.name} on all the switches"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]
            else:
                _message = (
                    "The radius configuration "
                    f"{self.name} does not exist. Cannot apply"
                )

        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while "
                f"applying radius configuraiton {self.name}"
            )

        return _message, _status, _changed
