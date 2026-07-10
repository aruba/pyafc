# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Unit tests for the Remote File Transfer Server (RFTS) service.

These tests exercise the deterministic logic of the RFTS service (payload
building, idempotency of create / update / delete and the version-support
handling) using a fake HTTP client. They do not require a live AFC.

Run with:
    python3 -m unittest tests.test_rfts
"""

from __future__ import annotations

import json
import unittest

from pyafc.services import models, rfts


class FakeResponse:
    def __init__(self, status_code: int, payload) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return {"result": self._payload}


class FakeClient:
    """Minimal stand-in for the httpx client used by pyafc."""

    base_url = "https://afc.example/api/"

    def __init__(self, rftss: list | None = None) -> None:
        self._rftss = rftss or []
        self.calls: list = []

    def get(self, uri: str) -> FakeResponse:
        self.calls.append(("get", uri, None))
        if uri == "versions":
            return FakeResponse(200, {"software": "7.3.0-15489"})
        return FakeResponse(200, self._rftss)

    def post(self, uri: str, data=None) -> FakeResponse:
        self.calls.append(("post", uri, data))
        return FakeResponse(200, "new-uuid")

    def put(self, uri: str, data=None) -> FakeResponse:
        self.calls.append(("put", uri, data))
        return FakeResponse(200, "updated-uuid")

    def delete(self, uri: str) -> FakeResponse:
        self.calls.append(("delete", uri, None))
        return FakeResponse(200, "deleted")


class FakeUnsupportedClient:
    """Simulates an AFC version where the RFTS API is not available (404)."""

    base_url = "https://afc.example/api/"

    def __init__(self) -> None:
        self.calls: list = []

    def get(self, uri: str) -> FakeResponse:
        self.calls.append(("get", uri, None))
        if uri == "versions":
            return FakeResponse(200, {"software": "7.1.0-14171"})
        return FakeResponse(404, None)

    def post(self, uri: str, data=None) -> FakeResponse:
        self.calls.append(("post", uri, data))
        return FakeResponse(404, None)

    def put(self, uri: str, data=None) -> FakeResponse:
        self.calls.append(("put", uri, data))
        return FakeResponse(404, None)

    def delete(self, uri: str) -> FakeResponse:
        self.calls.append(("delete", uri, None))
        return FakeResponse(404, None)


EXISTING = {
    "uuid": "rfts-1",
    "name": "Existing",
    "description": "old",
    "remote_file_server_hostname": "10.0.0.1",
    "protocol": "sftp",
    "username": "user1",
    "location": "/backups",
}


class TestRftsModel(unittest.TestCase):
    def test_minimal_valid(self):
        model = models.Rfts(
            name="srv",
            remote_file_server_hostname="host",
            protocol="sftp",
            username="user",
            password="secret",
        )
        dumped = model.model_dump(exclude_none=True)
        self.assertEqual(dumped["name"], "srv")
        self.assertNotIn("location", dumped)

    def test_invalid_protocol(self):
        with self.assertRaises(Exception):
            models.Rfts(
                name="srv",
                remote_file_server_hostname="host",
                protocol="ftp",
                username="user",
                password="secret",
            )


class TestCreateRfts(unittest.TestCase):
    def test_create_new(self):
        client = FakeClient()
        instance = rfts.Rfts(client, name="NewSrv")
        message, status, changed = instance.create_rfts(
            remote_file_server_hostname="10.0.0.2",
            protocol="sftp",
            username="user",
            password="secret",
        )
        self.assertTrue(status)
        self.assertTrue(changed)
        posts = [c for c in client.calls if c[0] == "post"]
        self.assertEqual(len(posts), 1)
        body = json.loads(posts[0][2])
        self.assertEqual(body["remote_file_server_hostname"], "10.0.0.2")
        self.assertEqual(body["password"], "secret")

    def test_create_existing_is_idempotent(self):
        client = FakeClient([EXISTING])
        instance = rfts.Rfts(client, name="Existing")
        message, status, changed = instance.create_rfts(
            remote_file_server_hostname="10.0.0.1",
            protocol="sftp",
            username="user1",
            password="secret",
        )
        self.assertTrue(status)
        self.assertFalse(changed)
        self.assertIn("already", message)
        self.assertFalse([c for c in client.calls if c[0] == "post"])


class TestUpdateRfts(unittest.TestCase):
    def test_update_no_change_is_idempotent(self):
        client = FakeClient([EXISTING])
        instance = rfts.Rfts(client, name="Existing")
        message, status, changed = instance.update_rfts(
            remote_file_server_hostname="10.0.0.1",
            protocol="sftp",
            username="user1",
            description="old",
            location="/backups",
        )
        self.assertTrue(status)
        self.assertFalse(changed)
        self.assertIn("up to date", message)
        self.assertFalse([c for c in client.calls if c[0] == "put"])

    def test_update_with_change(self):
        client = FakeClient([EXISTING])
        instance = rfts.Rfts(client, name="Existing")
        message, status, changed = instance.update_rfts(
            remote_file_server_hostname="10.9.9.9",
            password="newsecret",
        )
        self.assertTrue(status)
        self.assertTrue(changed)
        puts = [c for c in client.calls if c[0] == "put"]
        self.assertEqual(len(puts), 1)
        body = json.loads(puts[0][2])
        self.assertEqual(body["remote_file_server_hostname"], "10.9.9.9")
        # unchanged fields are preserved from current state
        self.assertEqual(body["username"], "user1")
        self.assertEqual(body["password"], "newsecret")

    def test_update_missing(self):
        client = FakeClient()
        instance = rfts.Rfts(client, name="Absent")
        message, status, changed = instance.update_rfts(
            remote_file_server_hostname="10.0.0.9",
        )
        self.assertFalse(status)
        self.assertFalse(changed)
        self.assertIn("does not exist", message)


class TestDeleteRfts(unittest.TestCase):
    def test_delete_existing(self):
        client = FakeClient([EXISTING])
        instance = rfts.Rfts(client, name="Existing")
        message, status, changed = instance.delete_rfts()
        self.assertTrue(status)
        self.assertTrue(changed)
        deletes = [c for c in client.calls if c[0] == "delete"]
        self.assertEqual(deletes[0][1], "remote_file_transfer_server/rfts-1")

    def test_delete_missing_is_idempotent(self):
        client = FakeClient()
        instance = rfts.Rfts(client, name="Absent")
        message, status, changed = instance.delete_rfts()
        self.assertTrue(status)
        self.assertFalse(changed)
        self.assertIn("does not exist", message)


class TestFeatureNotSupported(unittest.TestCase):
    def test_create_not_supported(self):
        client = FakeUnsupportedClient()
        instance = rfts.Rfts(client, name="Srv")
        self.assertFalse(instance.supported)
        message, status, changed = instance.create_rfts(
            remote_file_server_hostname="10.0.0.2",
            protocol="sftp",
            username="user",
            password="secret",
        )
        self.assertFalse(status)
        self.assertFalse(changed)
        self.assertIn("not supported", message)
        self.assertFalse([c for c in client.calls if c[0] == "post"])

    def test_update_not_supported(self):
        client = FakeUnsupportedClient()
        instance = rfts.Rfts(client, name="Srv")
        message, status, changed = instance.update_rfts(
            remote_file_server_hostname="10.0.0.2",
        )
        self.assertFalse(status)
        self.assertIn("not supported", message)

    def test_delete_not_supported(self):
        client = FakeUnsupportedClient()
        instance = rfts.Rfts(client, name="Srv")
        message, status, changed = instance.delete_rfts()
        self.assertFalse(status)
        self.assertIn("not supported", message)


if __name__ == "__main__":
    unittest.main()
