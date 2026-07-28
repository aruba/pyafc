# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Unit tests for the global EVPN Settings management.

These tests exercise the deterministic logic of the EVPN settings methods
(``get_evpn_settings`` / ``update_evpn_settings``) - payload building and
idempotency - using a fake HTTP client. They do not require a live AFC.

Run with:
    python3 -m unittest tests.test_evpn_settings
"""

from __future__ import annotations

import json
import unittest

# Importing the fabric module first ensures the fabric sub-package is
# initialised in the correct order (pyafc.common.utils imports
# pyafc.fabric.fabric, so importing a single fabric mixin first would
# trigger a circular import).
from pyafc.fabric import fabric  # noqa: F401
from pyafc.fabric import evpn, models

FABRIC_UUID = "1c35f445-0e2c-4d0a-b8fd-dae75924567e"
OTHER_UUID = "99999999-0e2c-4d0a-b8fd-dae759245999"


class FakeResponse:
    def __init__(self, status_code: int, payload) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return {"result": self._payload}


class FakeClient:
    """Minimal stand-in for the httpx client used by pyafc."""

    base_url = "https://afc.example/api/"

    def __init__(self, settings: list | None = None) -> None:
        self._settings = settings if settings is not None else []
        self.calls: list = []

    def get(self, uri: str) -> FakeResponse:
        self.calls.append(("get", uri, None))
        return FakeResponse(200, self._settings)

    def put(self, uri: str, data=None) -> FakeResponse:
        self.calls.append(("put", uri, data))
        return FakeResponse(200, "updated")


def _make_evpn(client) -> evpn.EVPN:
    instance = evpn.EVPN()
    instance.client = client
    instance.uuid = FABRIC_UUID
    instance.name = "DC1"
    return instance


def _default_settings(**overrides) -> dict:
    settings = {
        "fabric_uuid": FABRIC_UUID,
        "arp_suppression": False,
        "local_svi": False,
        "local_mac": False,
        "vxlan_tunnel_bridging_mode": "ibgp-ebgp",
    }
    settings.update(overrides)
    return settings


class TestEVPNSettingsModel(unittest.TestCase):
    def test_model_excludes_none(self):
        data = models.EVPNSettings(
            fabric_uuid=FABRIC_UUID,
            arp_suppression=True,
        )
        dumped = data.model_dump(exclude_none=True)
        self.assertEqual(dumped["fabric_uuid"], FABRIC_UUID)
        self.assertTrue(dumped["arp_suppression"])
        self.assertNotIn("vxlan_tunnel_bridging_mode", dumped)


class TestGetEVPNSettings(unittest.TestCase):
    def test_returns_settings_for_fabric(self):
        client = FakeClient([_default_settings()])
        instance = _make_evpn(client)
        result = instance.get_evpn_settings()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["fabric_uuid"], FABRIC_UUID)

    def test_returns_false_when_fabric_absent(self):
        client = FakeClient([_default_settings(fabric_uuid=OTHER_UUID)])
        instance = _make_evpn(client)
        self.assertFalse(instance.get_evpn_settings())

    def test_returns_false_when_empty(self):
        instance = _make_evpn(FakeClient([]))
        self.assertFalse(instance.get_evpn_settings())


class TestUpdateEVPNSettings(unittest.TestCase):
    def test_no_settings_found_is_noop(self):
        client = FakeClient([])
        instance = _make_evpn(client)
        message, status, changed = instance.update_evpn_settings(
            arp_suppression=True,
        )
        self.assertFalse(status)
        self.assertFalse(changed)
        self.assertIn("not found", message)
        self.assertNotIn(("put", "evpn/settings", None), client.calls)

    def test_idempotent_when_unchanged(self):
        client = FakeClient([_default_settings(arp_suppression=True)])
        instance = _make_evpn(client)
        message, status, changed = instance.update_evpn_settings(
            arp_suppression=True,
        )
        self.assertTrue(status)
        self.assertFalse(changed)
        self.assertIn("up to date", message)
        self.assertFalse(any(c[0] == "put" for c in client.calls))

    def test_applies_change(self):
        client = FakeClient([_default_settings(arp_suppression=False)])
        instance = _make_evpn(client)
        message, status, changed = instance.update_evpn_settings(
            arp_suppression=True,
        )
        self.assertTrue(status)
        self.assertTrue(changed)
        self.assertIn("Successfully updated", message)
        put_calls = [c for c in client.calls if c[0] == "put"]
        self.assertEqual(len(put_calls), 1)
        payload = json.loads(put_calls[0][2])
        self.assertEqual(payload["fabric_uuid"], FABRIC_UUID)
        self.assertTrue(payload["arp_suppression"])

    def test_preserves_current_values_on_partial_update(self):
        client = FakeClient(
            [
                _default_settings(
                    arp_suppression=False,
                    local_svi=True,
                    vxlan_tunnel_bridging_mode="ibgp-ebgp",
                ),
            ],
        )
        instance = _make_evpn(client)
        message, status, changed = instance.update_evpn_settings(
            arp_suppression=True,
        )
        self.assertTrue(changed)
        put_calls = [c for c in client.calls if c[0] == "put"]
        payload = json.loads(put_calls[0][2])
        # arp_suppression changed, other values preserved from current
        self.assertTrue(payload["arp_suppression"])
        self.assertTrue(payload["local_svi"])
        self.assertEqual(payload["vxlan_tunnel_bridging_mode"], "ibgp-ebgp")

    def test_handles_null_current_values(self):
        # AFC returns null for unset optional fields; reinjecting those
        # current values must not raise a ValidationError (regression).
        client = FakeClient(
            [
                _default_settings(
                    arp_suppression=True,
                    local_svi=None,
                    local_mac=None,
                    vxlan_tunnel_bridging_mode=None,
                ),
            ],
        )
        instance = _make_evpn(client)
        message, status, changed = instance.update_evpn_settings(
            arp_suppression=False,
        )
        self.assertTrue(status)
        self.assertTrue(changed)
        self.assertNotIn("ValidationError", message)
        put_calls = [c for c in client.calls if c[0] == "put"]
        self.assertEqual(len(put_calls), 1)
        payload = json.loads(put_calls[0][2])
        self.assertFalse(payload["arp_suppression"])
        # None-valued optional fields are excluded from the payload
        self.assertNotIn("local_svi", payload)
        self.assertNotIn("local_mac", payload)
        self.assertNotIn("vxlan_tunnel_bridging_mode", payload)


class TestPerSwitchUpdate(unittest.TestCase):
    def test_switch_scoped_payload_excludes_fabric_uuid(self):
        # AFC requires exactly one of switch_uuids or fabric_uuid. When
        # switches are targeted, fabric_uuid must not be present.
        client = FakeClient([_default_settings(local_svi=None)])
        instance = _make_evpn(client)
        message, status, changed = instance.update_evpn_settings(
            local_svi=True,
            switch_uuids=["uuid-a", "uuid-b"],
        )
        self.assertTrue(status)
        self.assertTrue(changed)
        put_calls = [c for c in client.calls if c[0] == "put"]
        self.assertEqual(len(put_calls), 1)
        payload = json.loads(put_calls[0][2])
        self.assertEqual(payload["switch_uuids"], ["uuid-a", "uuid-b"])
        self.assertNotIn("fabric_uuid", payload)
        self.assertTrue(payload["local_svi"])


if __name__ == "__main__":
    unittest.main()
