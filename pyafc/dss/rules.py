# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import exceptions, utils
from pyafc.dss import models


class Rule:
    def __init__(
        self,
        client,
        name: str | None = None,
        **kwargs: dict,
    ) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the Rule.

        Returns:
            existing_rule (bool): True if available, False if not.

        """
        if name:
            self.name = name
        if client:
            self.client = client
        self.uuid = None
        self.existing_rule = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """Rule main class file. Sets class attribute uuid if the Rule exists.

        Returns:
            Class attributes (Any): All rules related attribute.

        """
        rules_request = self.client.get("rules")
        for rule in rules_request.json()["result"]:
            if rule["name"] == self.name:
                self.uuid = rule["uuid"]
                for item, value in rule.items():
                    setattr(self, item, value)
                return True
        return False

    def _get_eg(self, endpoint_group: str) -> str:
        """_get_eg get endoint groups uuid if exists, else raise exception.

        Args:
            endpoint_group (str): Name of the endpoint group

        Returns:
            eg['uuid'] (str): UUID of the endpoint group.

        """
        eg_list = "endpoint_groups"

        eg_request = self.client.get(eg_list)

        for eg in eg_request.json()["result"]:
            if eg["name"] == endpoint_group:
                return eg["uuid"]

        msg = f"Endpoint Group {endpoint_group} is unknown"
        raise exceptions.EndpointGroupUnknown(msg)

    def _get_qualifier(self, qualifier: str) -> str:
        """_get_qualifier get qualifier uuid if exists, else raise exception.

        Args:
            qualifier (str): Name of the qualifier.

        Returns:
            qual['uuid'] (str): UUID of the qualifier.

        """
        qual_request = self.client.get("qualifiers")

        for qual in qual_request.json()["result"]:
            if qual["name"] == qualifier:
                return qual["uuid"]

        msg = f"Service Qualifier {qualifier} is unknown"
        raise exceptions.ServiceQualifierUnknown(msg)

    def _get_application(self, application: str) -> str:
        """_get_application get application uuid if exists, else raise exc.

        Args:
            application (str): Name of the application.

        Returns:
            app['uuid'] (str): UUID of the application.

        """
        app_request = self.client.get("applications")

        for app in app_request.json()["result"]:
            if app["name"] == application:
                return app["uuid"]

        msg = f"Application {application} is unknown"
        raise exceptions.ApplicationUnknown(msg)

    def create_rule(self, **values: dict) -> tuple:
        """create_rule is used to create a DSS rule.

        Args:
            description (str): Rule description
            type (str, optional): One of :
                - 'layer3'
                - 'layer2'
                Defaults to 'layer3'
            source_endpoint_groups (list): List of Endpoints groups as Sources
            destination_endpoint_groups (list): List of Endpoints groups
                as Destinations
            service_qualifiers (list): List of Qualifiers
            applications (list): List of Applications
            action (str, optional): One of :
                - 'allow'
                - 'drop'
                Defaults to 'allow'.

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed something.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if values.get("source_endpoint_groups"):
                new_values = [
                    self._get_eg(item)
                    for item in values["source_endpoint_groups"]
                ]
                values["source_endpoint_groups"] = new_values

            if values.get("destination_endpoint_groups"):
                new_values = [
                    self._get_eg(item)
                    for item in values["destination_endpoint_groups"]
                ]
                values["destination_endpoint_groups"] = new_values

            if values.get("service_qualifiers"):
                new_values = [
                    self._get_qualifier(item)
                    for item in values["service_qualifiers"]
                ]
                values["service_qualifiers"] = new_values

            if values.get("applications"):
                new_values = [
                    self._get_application(item)
                    for item in values["applications"]
                ]
                values["applications"] = new_values

            if self.existing_rule:
                _message = (f"The rule {self.name} already exists. "
                            "No action taken")
                _status = True
            else:
                if values.get("name"):
                    values.pop("name")
                data = models.PsmRule(name=self.name, **values)

                add_request = self.client.post(
                    "rules",
                    data=json.dumps(data.dict(exclude_none=True)),
                )

                if add_request.status_code in utils.response_ok:
                    _message = f"Successfully created rule {self.name}"
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]

        except (
            exceptions.EndpointGroupUnknown,
            exceptions.ServiceQualifierUnknown,
            exceptions.ApplicationUnknown,
        ) as exc:
            _message = (f"An exception {exc} occurred while "
                        "attempting to create rule {self.name}")

        return _message, _status, _changed

    def delete_rule(self) -> tuple:
        """delete_rule is used to delete a DSS rule.

        Returns:
            message (str): Action message.
            status (bool): Status of the action, true or false.
            changed (bool): Set to true of action has changed something.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_rule:
                delete_request = self.client.delete(f"rules/{self.uuid}")

                if delete_request.status_code in utils.response_ok:
                    _message = f"Successfully deleted rule {self.name}"
                    _status = True
                    _changed = True
                else:
                    _message = delete_request.json()["result"]
            else:
                _message = (f"The rule {self.name} does not exist. "
                            "No action taken")
                _status = True

        except (
            exceptions.EndpointGroupUnknown,
            exceptions.ServiceQualifierUnknown,
            exceptions.ApplicationUnknown,
        ) as exc:
            _message = (f"An exception {exc} occurred while "
                        "attempting to create rule {self.name}")

        return _message, _status, _changed
