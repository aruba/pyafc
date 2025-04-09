# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from __future__ import annotations

from asyncio import run as aiorun
from typing import Any

import httpx

from pyafc.afc import backups, licenses
from pyafc.common import exceptions, utils


class Afc(backups.Backup, licenses.License):

    afc_connected: dict = {}

    def __init__(self, data: dict | None = None):
        """__init__ Instantiate the AFC Class.

        Args:
            ip (str): AFC IP Address.
            username (str): AFC username
            password (str): AFC password

        Example:
            afc_instance = afc.Afc(ip=10.10.10.10,
                                   username='admin',
                                   password='password')

        Returns:
            None

        """
        self.afc_data = data
        self.connect_client = {}
        timeout = httpx.Timeout(20.0, read=60, connect=60.0)
        afc_url = f"https://{self.afc_data['ip']}/api/"
        self.client = httpx.Client(
            verify=False, base_url=afc_url, timeout=timeout,
        )
        self.connect()
        if self.afc_connected:
            aiorun(self.connect_async())
            self.__instantiate_details()

    def connect(self) -> None:
        """Connect Triggers a connection to AFC.

        Args:
            None.

        Returns:
            If successful, the header and the auth_token
            are set as Class attributes.

        """
        if "username" in list(self.afc_data.keys()) and "password" in list(
            self.afc_data.keys(),
        ):
            header = {
                "Accept": "application/json, version=1.0",
                "Content-Type": "application/json",
                "X-Auth-Username": self.afc_data["username"],
                "X-Auth-Password": self.afc_data["password"],
            }
            try:
                auth_request = self.client.post("auth/token", headers=header)
                header = {
                    "Accept": "application/json, version=1.0",
                    "Content-Type": "application/json",
                    "Authorization": f'{auth_request.json()["result"]}',
                }
                if auth_request.status_code in utils.response_ok:
                    self.auth_token = f'{auth_request.json()["result"]}'
                    self.client.headers = header
                    self.afc_connected = True
                    self.connect_client["client"] = self.client
                else:
                    self.afc_connected = False
                    raise exceptions.AuthenticationIssue(
                        auth_request.json()["result"]
                    )
            except exceptions.AuthenticationIssue:
                self.client = False
            except Exception:
                self.client = False
        else:
            try:
                header = {
                    "Accept": "application/json, version=1.0",
                    "Content-Type": "application/json",
                    "Authorization": f"{self.afc_data['auth_token']}",
                }
                self.auth_token = f"{self.afc_data['auth_token']}"
                self.client.headers = header
                self.afc_connected = True
                self.connect_client["client"] = self.client
            except exceptions.AuthenticationIssue:
                self.client = False
            except Exception:
                self.client = False

    async def connect_async(self) -> None:
        """connect_async Triggers a connection to AFC using Async method.

        Args:
            None.

        Returns:
            If successful, the header and the auth_token
            are set as Class attributes.

        """
        timeout = httpx.Timeout(20.0, read=60, connect=60.0)
        afc_url = f"https://{self.afc_data['ip']}/api/"
        self.async_client = httpx.AsyncClient(
            verify=False, base_url=afc_url, timeout=timeout,
        )
        if "username" in list(self.afc_data.keys()) and "password" in list(
            self.afc_data.keys()
        ):
            header = {
                "Accept": "application/json, version=1.0",
                "Content-Type": "application/json",
                "X-Auth-Username": self.afc_data["username"],
                "X-Auth-Password": self.afc_data["password"],
            }
            auth_request = await self.async_client.post(
                "auth/token", headers=header,
            )
            if auth_request.json()["result"]:
                header = {
                    "Accept": "application/json, version=1.0",
                    "Content-Type": "application/json",
                    "Authorization": f'{auth_request.json()["result"]}',
                }
                self.async_client.headers = header
                self.connect_client["async_client"] = self.async_client
        else:
            header = {
                "Accept": "application/json, version=1.0",
                "Content-Type": "application/json",
                "Authorization": f"{self.afc_data['auth_token']}",
            }
            self.async_client.headers = header
            self.connect_client["async_client"] = self.async_client

    def __instantiate_details(self):
        """__instantiate_details checks whether the AFC instance created.

        Args:
            None.

        Returns:
            If successful, the header and the auth_token
            are set as Class attributes.

        """
        afc_system_request = self.client.get("system")
        afc_version_request = self.client.get("versions")
        afc_system_data = afc_system_request.json()["result"]
        afc_version_data = afc_version_request.json()["result"]
        system_data = {**afc_system_data, **afc_version_data}

        for item, value in system_data.items():
            setattr(self, item, value)
        return True

    def ping(self):
        """Ping function is used to check if the AFC instance is pingable.

        Args:
            None.

        Returns:
            If successful, returns True else False.

        """
        afc_request = self.client.get("ping")
        return afc_request.status_code in [204]

    def get_request(self, uri: str):
        """get_request is a generic function to get details from a URI.

        Args:
            uri (str): URI to be used for the get request.

        Returns:
            If successful, returns the contents.

        """
        getRequest = self.client.get(uri)
        return getRequest.json()["result"]

    def post_request(self, uri: str, payload: Any):
        """post_request (placeholder) against any given URI.

        Args:
            uri (str): URI to be used for the post request.
            payload (dict): Payload required for the post request.

        Returns:
            None.

        """
        return True

    def put_request(self, uri: str, payload: Any):
        """put_request (placeholder) against any given URI.

        Args:
            uri (str): URI to be used for the put request.
            payload (dict): Payload required for the put request.

        Returns:
            None.

        """
        return True

    def patch_request(self, uri: str, payload: Any):
        """patch_request (placeholder) against any given URI.

        Args:
            uri (str): URI to be used for the patch request.
            payload (dict): Payload required for the patch request.

        Returns:
            None.

        """
        return True

    def delete_request(self, uri: str):
        """delete_request (placeholder) against any given URI.

        Args:
            uri (str): URI to be used for the delete request.

        Returns:
            None.

        """
        return True

    def disconnect(self):
        """Disconnect function is used to disconnect the AFC session.

        Args:
            None.

        Returns:
            None.

        """
        self.client.delete("auth/token")
        self.client.close()
