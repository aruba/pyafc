# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0
from __future__ import annotations

import json

from pyafc.common import utils
from pyafc.services import models


class Pool:
    def __init__(self, client, name: str, **kwargs: dict) -> None:
        """__init__ Class init function.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            name (str): Name of the Resource Pool.

        Returns:
            existing_eg (bool): True if available, False if not.

        """
        self.client = client
        self.uuid = None
        self.name = name
        self.existing_pool = self.__instantiate_details()

    def __instantiate_details(self) -> bool:
        """__instantiate_details Find Resource Pool UUID.

        Returns:
            Returns True if resource pool is found and sets the UUID as class \
                attribute, false if not found.

        """
        pool_request = self.client.get("resource_pool")
        for pool in pool_request.json()["result"]:
            if pool["name"] == self.name:
                self.uuid = pool["uuid"]
                for item, value in pool.items():
                    setattr(self, item, value)
                return True
        return False

    @staticmethod
    def get_resource_pool(client, name: str, rp_type: str | None = None):
        """get_resource_pool Find Resource Pool.

        Args:
            client (Any): AFC Connection object.
            name (str): Resource Pool name.
            rp_type (str): Resource Pool type - Must be either 'MAC' or 'IPv4'.

        Returns:
            Returns the resource pool JSON data if found else False.

        """
        uri_pool = "resource_pool"
        if rp_type:
            uri_pool = "resource_pool?resource_type=" + rp_type

        pool_request = client.get(uri_pool)

        for pool in pool_request.json()["result"]:
            if pool["name"] == name:
                return pool
        return False

    def create_pool(self, **values: dict) -> tuple:
        """create_pool Create a resource pool.

        Args:
            description (str, optional) = Description
            type (str): One of:
                - 'MAC'
                - 'IPv4'
            pool_ranges (str) = IPv4 Network

        Example:
            pool = resource_pools.Pool(afc_instance.client, name="New_MAC_Pool")
            pool.create_pool(type="MAC",
                             pool_ranges="02:00:00:00:00:01-02:00:00:00:00:FF")

            pool = resource_pools.Pool(afc_instance.client, name="New_IP_Pool")
            pool.create_pool(type="IPv4",
                             pool_ranges="10.10.10.0/24")

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is applied, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_pool:
                _message = (
                    f"The resource pool {self.name} already exists. "
                    "No action taken"
                )
                _status = True
            else:
                data = models.ResourcesPool(**values)
                add_request = self.client.post(
                    "resource_pool",
                    data=json.dumps(data.dict()),
                )

                if add_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully created the resource pool {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = add_request.json()["result"]
        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while creating the "
                f"resource pool {self.name}"
            )

        return _message, _status, _changed

    def delete_pool(self) -> tuple:
        """delete_pool Delete a resource pool.

        Returns:
            message: Action message.
            status: Status of the action, True or False.
            changed: True if the configuration is deleted, else False.

        """
        _message = ""
        _status = False
        _changed = False

        try:
            if self.existing_pool:
                delete_request = self.client.delete(
                    f"resource_pool/{self.uuid}",
                )
                if delete_request.status_code in utils.response_ok:
                    _message = (
                        f"Successfully deleted the resource pool {self.name}"
                    )
                    _status = True
                    _changed = True
                else:
                    _message = delete_request.json()["result"]
            else:
                _message = (
                    f"The resource pool {self.name} does not exist. "
                    "No action taken."
                )
                _status = True
        except Exception as exc:
            _message = (
                f"An exception {exc} occurred while deleting the "
                f"resource pool {self.name}"
            )

        return _message, _status, _changed
