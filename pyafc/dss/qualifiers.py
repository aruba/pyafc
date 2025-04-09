# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import utils
from pyafc.dss import models


class Qualifier:
    def __init__(
        self,
        client,
        name: str | None = None,
        **kwargs: dict,
    ) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the Qualifier.

        Returns:
            existing_qualifier (bool): True if available, False if not.

        """
        if name:
            self.name = name
        if client:
            self.client = client
        self.uuid = None
        self.existing_qualifier = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details Instantiate Qualifier details.

        Returns:
            existing_qualifier (bool): If the input Qualifier is found.

        """
        qualifier_request = self.client.get("qualifiers")
        for qualifier in qualifier_request.json()["result"]:
            if qualifier["name"] == self.name:
                self.uuid = qualifier["uuid"]
                for item, value in qualifier.items():
                    setattr(self, item, value)
                return True
        return False

    def create_qualifier(self, **values: dict) -> tuple:
        """create_qualifier is used to create qualifier.

        Args:
            src_port (str): Source Port
            dst_port (str): Destination Port
            ip_protocol (str): IP Protocol.

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed something.

        """
        _message = ""
        _status = False
        _changed = False

        if self.existing_qualifier:
            _message = (f"The qualifer {self.name} already exists. "
                        "No action taken.")
            _status = True
        else:
            if values.get("name"):
                values.pop("name")

            data = models.PsmQualifiers(name=self.name, **values)

            add_request = self.client.post(
                "qualifiers",
                data=json.dumps(data.dict(exclude_none=True)),
            )

            if add_request.status_code in utils.response_ok:
                _message = f"Successfully created qualifier {self.name}"
                _status = True
                _changed = True
            else:
                _message = add_request.json()["result"]

        return _message, _status, _changed

    def delete_qualifier(self) -> tuple:
        """delete_qualifier is used to delete qualifier.

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed something.

        """
        _message = ""
        _status = False
        _changed = False

        if self.existing_qualifier:
            delete_request = self.client.delete(f"qualifiers/{self.uuid}")

            if delete_request.status_code in utils.response_ok:
                _message = f"Successfully deleted qualifier {self.name}"
                _status = True
                _changed = True
            else:
                _message = delete_request.json()["result"]
        else:
            _message = (f"The qualifer {self.name} does not exist. "
                        "No action taken.")
            _status = True

        return _message, _status, _changed
