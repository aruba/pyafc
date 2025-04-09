# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

import json
import time

from pydantic import ValidationError

from pyafc.common import exceptions, utils
from pyafc.fabric import fabric
from pyafc.integrations import models


class Psm:
    def __init__(self) -> None:
        pass

    def get_psm(self, psm: str) -> dict:
        """get_psm is used the PSM integrations.

        Args:
            client (Any): Client instance to Connect and Authenticate on AFC.
            psm (str): Name of the PSM integration

        Returns:
            PSM data (dict): PSM Integration data.

        """
        psm_request = self.client.get(f"pensando/psms/{psm}")
        return psm_request.json()["result"]

    def create_psm(self, **kwargs: dict) -> tuple:
        """create_psm Create Pensando integration.

        Args:
            name (str) = Integration's name
            description (str) = Integration's description
            host (str) = PSM's IP Address
            username (str) = PSM's Username
            password (str) = PSM's Password
            enabled (bool, optional) = Integration enabled
            fabrics (list) = List of Fabrics
            verify_ssl (bool, optional) = Indicates whether SSL/TLS
                certificates should be validated when connecting to the PSM.
                Defaults to False
            auto_decommission_dss (bool, optional) = When true, automatic
                decommission and removal in PSM of DSS entities (resident on
                switches related to the given fabric) will occur upon removal
                of the related switch from HPE Aruba Networking Fabric
                Composer.
                Defaults to False
            auto_vlan_placement (bool, optional) = When true, ensures that
                when Networks are synchronized to or from PSM, all applicable
                switches in the related fabric have the VLAN statement for the
                VLAN ID specified in the given Network.
                Defaults to True

        Example:
            psm_data = {
                "name": "PSM",
                "password": "<password>",
                "fabrics": [
                    "DC1",
                ],
                "host": "10.14.120.112",
                "username": "admin",
                }
            integration_instance.create_psm(**psm_data)

        Returns:
            message: Message containing the action taken.
            status: True if successful, otherwise False.
            changed: True if successful, otherwise False.

        """
        _message = ""
        _status = False
        _changed = False

        try:

            kwargs["fabric_uuid"] = []
            if kwargs.get("fabrics"):
                for fab in kwargs["fabrics"]:
                    uuid = fabric.Fabric.get_fabric_uuid(self.client, fab)
                    if uuid:
                        kwargs["fabric_uuid"].append(uuid)
                if not kwargs["fabric_uuid"]:
                    raise exceptions.FabricNotFound
            else:
                _message = "No Fabric provided - No action Taken"
                return _message, _status, _changed

            data = models.Psm(**kwargs)

            psm_request = self.client.post(
                "pensando/psms",
                data=json.dumps(data.dict(exclude_none=True)),
            )

            if psm_request.status_code in utils.response_ok:
                psm_details = self.get_psm(psm_request.json()["result"])
                while (
                    psm_details["connection_state"] != "connected"
                    and psm_details["health"]["status"] != "healthy"
                ):
                    time.sleep(2)
                    psm_details = self.get_psm(psm_request.json()["result"])
                _message = "Successfully created PSM integration"
                _status = True
                _changed = True
            else:
                if "already exists" in psm_request.json()["result"]:
                    _status = True
                _message = psm_request.json()["result"]

        except exceptions.FabricNotFound:
            _message = "Fabric not found"

        except ValidationError as exc:
            _message = f"An exception occurred while integrating PSM {exc}"

        return _message, _status, _changed
