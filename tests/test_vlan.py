# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Unit tests for the fabric VLAN management mixin.

These tests exercise the deterministic logic of the VLAN mixin (payload
building, VLAN range expansion, UUID resolution and the create / update /
delete flows) using a fake HTTP client. They do not require a live AFC.

Run with:
    python3 -m unittest tests.test_vlan
"""

from __future__ import annotations

import json
import unittest
from unittest import mock

# Importing the fabric module first ensures the fabric sub-package is
# initialised in the correct order (pyafc.common.utils imports
# pyafc.fabric.fabric, so importing a single fabric mixin first would
# trigger a circular import).
from pyafc.fabric import fabric  # noqa: F401
from pyafc.common import exceptions, versioning
from pyafc.fabric import models, vlan


class FakeResponse:
    def __init__(self, status_code: int, payload) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return {"result": self._payload}


class FakeClient:
    """Minimal stand-in for the httpx client used by pyafc."""

    def __init__(self, vlans: list | None = None) -> None:
        self._vlans = vlans or []
        self.calls: list = []

    def get(self, uri: str) -> FakeResponse:
        self.calls.append(("get", uri, None))
        return FakeResponse(200, self._vlans)

    def post(self, uri: str, data=None) -> FakeResponse:
        self.calls.append(("post", uri, data))
        return FakeResponse(200, "created")

    def patch(self, uri: str, data=None) -> FakeResponse:
        self.calls.append(("patch", uri, data))
        return FakeResponse(200, "updated")

    def delete(self, uri: str) -> FakeResponse:
        self.calls.append(("delete", uri, None))
        return FakeResponse(200, "deleted")


class VlanFixture(vlan.Vlan):
    """Concrete Vlan mixin bound to a fake client and fabric UUID."""

    def __init__(self, client: FakeClient) -> None:
        self.client = client
        self.uuid = "fabric-uuid"


class FakeUnsupportedClient:
    """Simulates an AFC version where the VLAN API is not available (404)."""

    base_url = "https://afc.example/api/"

    def __init__(self) -> None:
        self.calls: list = []

    def get(self, uri: str) -> FakeResponse:
        self.calls.append(("get", uri, None))
        return FakeResponse(404, None)

    def post(self, uri: str, data=None) -> FakeResponse:
        self.calls.append(("post", uri, data))
        return FakeResponse(404, None)

    def patch(self, uri: str, data=None) -> FakeResponse:
        self.calls.append(("patch", uri, data))
        return FakeResponse(404, None)

    def delete(self, uri: str) -> FakeResponse:
        self.calls.append(("delete", uri, None))
        return FakeResponse(404, None)


class TestVlanRangeExpansion(unittest.TestCase):
    def test_single(self):
        self.assertEqual(vlan.Vlan._expand_vlan_range("10"), [10])

    def test_int_input(self):
        self.assertEqual(vlan.Vlan._expand_vlan_range(10), [10])

    def test_comma_list(self):
        self.assertEqual(vlan.Vlan._expand_vlan_range("10,20,30"), [10, 20, 30])

    def test_range(self):
        self.assertEqual(vlan.Vlan._expand_vlan_range("10-12"), [10, 11, 12])

    def test_mixed_and_whitespace(self):
        self.assertEqual(
            vlan.Vlan._expand_vlan_range("10, 20-22 , 30"),
            [10, 20, 21, 22, 30],
        )


class TestVlanModel(unittest.TestCase):
    def test_vlan_id_int_is_stringified(self):
        entry = models.VlanEntry(vlan_id=100)
        self.assertEqual(entry.vlan_id, "100")
        self.assertIsNone(entry.strict_firewall_bypass_enabled)

    def test_strict_firewall_bypass_omitted_when_not_set(self):
        table = models.VlanTable(
            vlans=[{"vlan_id": 10, "vlan_name": "v10"}],
            vlan_scope={"switch_uuids": ["sw-1"]},
        )
        dumped = table.model_dump(exclude_none=True)
        self.assertNotIn(
            "strict_firewall_bypass_enabled", dumped["vlans"][0],
        )

    def test_strict_firewall_bypass_kept_when_set(self):
        table = models.VlanTable(
            vlans=[{
                "vlan_id": 10,
                "vlan_name": "v10",
                "strict_firewall_bypass_enabled": True,
            }],
            vlan_scope={"switch_uuids": ["sw-1"]},
        )
        dumped = table.model_dump(exclude_none=True)
        self.assertTrue(
            dumped["vlans"][0]["strict_firewall_bypass_enabled"],
        )

    def test_vlan_table_coerces_entries(self):
        table = models.VlanTable(
            vlans=[{"vlan_id": 10, "vlan_name": "v10"}],
            vlan_scope={"switch_uuids": ["sw-1"]},
        )
        dumped = table.model_dump(exclude_none=True)
        self.assertEqual(dumped["vlans"][0]["vlan_id"], "10")
        self.assertEqual(dumped["vlan_scope"], {"switch_uuids": ["sw-1"]})


class TestCreateVlan(unittest.TestCase):
    def test_create_with_switches(self):
        client = FakeClient()
        fixture = VlanFixture(client)
        with mock.patch.object(
            vlan.utils,
            "consolidate_switches_list",
            return_value=["sw-1", "sw-2"],
        ):
            message, status, changed = fixture.create_vlan(
                vlan_id="10,20-21",
                vlan_name="Prod",
                switches=["Leaf-1", "Leaf-2"],
            )
        self.assertTrue(status)
        self.assertTrue(changed)
        method, uri, data = client.calls[-1]
        self.assertEqual(method, "post")
        self.assertEqual(uri, "fabrics/fabric-uuid/vlans")
        body = json.loads(data)
        self.assertEqual(body["vlan_scope"], {"switch_uuids": ["sw-1", "sw-2"]})
        self.assertEqual(body["vlans"][0]["vlan_id"], "10,20,21")
        self.assertEqual(body["vlans"][0]["vlan_name"], "Prod")

    def test_create_with_fabric_scope(self):
        client = FakeClient()
        fixture = VlanFixture(client)
        message, status, changed = fixture.create_vlan(
            vlan_id="10",
            fabric_scope="exclude_spine",
        )
        self.assertTrue(status)
        body = json.loads(client.calls[-1][2])
        self.assertEqual(body["vlan_scope"], {"fabric_scope": "exclude_spine"})

    def test_create_without_scope_is_rejected(self):
        client = FakeClient()
        fixture = VlanFixture(client)
        message, status, changed = fixture.create_vlan(vlan_id="10")
        self.assertFalse(status)
        self.assertFalse(changed)
        self.assertIn("No action taken", message)
        self.assertEqual(client.calls, [])

    def test_create_with_unknown_device_is_rejected(self):
        client = FakeClient()
        fixture = VlanFixture(client)
        with mock.patch.object(
            vlan.utils, "consolidate_switches_list", return_value=[],
        ):
            message, status, changed = fixture.create_vlan(
                vlan_id="10", switches=["ghost"],
            )
        self.assertFalse(status)
        self.assertIn("No matching device", message)

    def test_create_existing_vlan_is_idempotent(self):
        client = FakeClient([{"uuid": "vlan-10", "vlan_id": 10}])
        fixture = VlanFixture(client)
        message, status, changed = fixture.create_vlan(
            vlan_id="10", fabric_scope="include_spine",
        )
        self.assertTrue(status)
        self.assertFalse(changed)
        self.assertIn("already exist", message)
        self.assertFalse(any(call[0] == "post" for call in client.calls))

    def test_create_only_creates_missing_vlans(self):
        client = FakeClient([{"uuid": "vlan-10", "vlan_id": 10}])
        fixture = VlanFixture(client)
        message, status, changed = fixture.create_vlan(
            vlan_id="10,11", fabric_scope="include_spine",
        )
        self.assertTrue(status)
        self.assertTrue(changed)
        body = json.loads(client.calls[-1][2])
        self.assertEqual(body["vlans"][0]["vlan_id"], "11")


class TestUpdateVlan(unittest.TestCase):
    def _fixture(self):
        vlans = [
            {"uuid": "vlan-10", "vlan_id": 10},
            {"uuid": "vlan-20", "vlan_id": 20},
        ]
        return VlanFixture(FakeClient(vlans))

    def test_update_assign_and_rename(self):
        fixture = self._fixture()
        with mock.patch.object(
            vlan.utils, "consolidate_switches_list", return_value=["sw-9"],
        ):
            message, status, changed = fixture.update_vlan(
                vlan_id="10",
                vlan_name="Renamed",
                switches=["Leaf-9"],
            )
        self.assertTrue(status)
        self.assertTrue(changed)
        method, uri, data = fixture.client.calls[-1]
        self.assertEqual(method, "patch")
        body = json.loads(data)
        self.assertEqual(body[0]["uuids"], ["vlan-10"])
        ops = {(p["op"], p["path"]): p["value"] for p in body[0]["patch"]}
        self.assertEqual(ops[("add", "/switch_uuids")], ["sw-9"])
        self.assertEqual(ops[("replace", "/vlan_name")], "Renamed")

    def test_update_unknown_vlan_is_rejected(self):
        fixture = self._fixture()
        message, status, changed = fixture.update_vlan(vlan_id="999")
        self.assertFalse(status)
        self.assertIn("not found", message)

    def test_update_without_changes_is_noop(self):
        fixture = self._fixture()
        message, status, changed = fixture.update_vlan(vlan_id="10")
        self.assertTrue(status)
        self.assertFalse(changed)
        self.assertIn("Nothing to update", message)


class TestDeleteVlan(unittest.TestCase):
    def _fixture(self):
        vlans = [
            {"uuid": "vlan-10", "vlan_id": 10},
            {"uuid": "vlan-20", "vlan_id": 20},
        ]
        return VlanFixture(FakeClient(vlans))

    def test_delete_entirely(self):
        fixture = self._fixture()
        message, status, changed = fixture.delete_vlan(vlan_id="10,20")
        self.assertTrue(status)
        self.assertTrue(changed)
        method, uri, _ = fixture.client.calls[-1]
        self.assertEqual(method, "delete")
        self.assertIn("vlan_uuids=vlan-10,vlan-20", uri)
        self.assertNotIn("switches=", uri)

    def test_delete_deassign_from_switches(self):
        fixture = self._fixture()
        with mock.patch.object(
            vlan.utils, "consolidate_switches_list", return_value=["sw-9"],
        ):
            message, status, changed = fixture.delete_vlan(
                vlan_id="10", switches=["Leaf-9"],
            )
        self.assertTrue(status)
        method, uri, _ = fixture.client.calls[-1]
        self.assertIn("vlan_uuids=vlan-10", uri)
        self.assertIn("switches=sw-9", uri)
        self.assertIn("unassigned", message)

    def test_delete_unknown_vlan_is_noop(self):
        fixture = self._fixture()
        message, status, changed = fixture.delete_vlan(vlan_id="999")
        self.assertTrue(status)
        self.assertFalse(changed)
        self.assertIn("not found", message)


class TestFeatureNotSupported(unittest.TestCase):
    """The VLAN API returns 404 on AFC versions that do not support it."""

    def setUp(self):
        versioning._version_cache.clear()

    def test_create_returns_clean_message(self):
        fixture = VlanFixture(FakeUnsupportedClient())
        message, status, changed = fixture.create_vlan(
            vlan_id="10", fabric_scope="include_spine",
        )
        self.assertFalse(status)
        self.assertFalse(changed)
        self.assertIn("not supported", message)

    def test_update_returns_clean_message(self):
        fixture = VlanFixture(FakeUnsupportedClient())
        message, status, changed = fixture.update_vlan(
            vlan_id="10", switches=["Leaf-1"],
        )
        self.assertFalse(status)
        self.assertFalse(changed)
        self.assertIn("not supported", message)

    def test_delete_returns_clean_message(self):
        fixture = VlanFixture(FakeUnsupportedClient())
        message, status, changed = fixture.delete_vlan(vlan_id="10")
        self.assertFalse(status)
        self.assertFalse(changed)
        self.assertIn("not supported", message)

    def test_get_vlans_raises_feature_not_supported(self):
        fixture = VlanFixture(FakeUnsupportedClient())
        with self.assertRaises(exceptions.FeatureNotSupported):
            fixture.get_vlans()


if __name__ == "__main__":
    unittest.main()
