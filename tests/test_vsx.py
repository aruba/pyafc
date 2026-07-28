# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Unit tests for VSX creation and the management (mgmt) VRF capability.

These tests exercise the deterministic logic of the VSX workflow, in
particular the AFC-version gating of the management-interface / mgmt VRF
keep alive capability (available from AFC 7.3 onwards). They use a fake HTTP
client and do not require a live AFC.

Run with:
    python3 -m unittest tests.test_vsx
"""

from __future__ import annotations

import json
import unittest

# Imported first to avoid a circular import when loading the fabric package.
from pyafc.fabric import fabric  # noqa: F401
from pyafc.common import versioning
from pyafc.fabric import vsx


class FakeResponse:
    def __init__(self, status_code: int, payload) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return {"result": self._payload}


class FakeClient:
    """Minimal stand-in for the httpx client used by pyafc."""

    def __init__(
        self,
        software: str = "7.3.0-15489",
        pools: list | None = None,
        existing_vsx: list | None = None,
    ) -> None:
        # base_url embeds the version so the per-instance version cache in
        # versioning.py does not collide between tests.
        self.base_url = f"https://afc-{software}.example/api/"
        self._software = software
        self._pools = pools if pools is not None else []
        self._existing_vsx = existing_vsx or []
        self.calls: list = []

    def get(self, uri: str) -> FakeResponse:
        self.calls.append(("get", uri))
        if uri == "versions":
            return FakeResponse(200, {"software": self._software})
        if uri.startswith("resource_pool"):
            return FakeResponse(200, self._pools)
        if uri.endswith("/vsx"):
            return FakeResponse(200, self._existing_vsx)
        return FakeResponse(200, [])

    def post(self, uri: str, data=None) -> FakeResponse:
        self.calls.append(("post", uri, data))
        return FakeResponse(200, "Successfully created VSX")


class _Vsx(vsx.VSX):
    """Concrete VSX helper wired to a fake client and fabric UUID."""

    def __init__(self, client, uuid: str = "fab-1") -> None:
        self.client = client
        self.uuid = uuid


MAC_POOL = {"name": "MAC POOL", "uuid": "mac-uuid"}


class TestParseVersion(unittest.TestCase):
    def test_parses_full_version(self):
        self.assertEqual(versioning._parse_version("7.3.0-15489"), (7, 3, 0))

    def test_parses_short_version(self):
        self.assertEqual(versioning._parse_version("7.2"), (7, 2))

    def test_returns_none_on_empty(self):
        self.assertIsNone(versioning._parse_version(None))
        self.assertIsNone(versioning._parse_version(""))


class TestIsVersionAtLeast(unittest.TestCase):
    def test_equal_is_supported(self):
        client = FakeClient(software="7.3.0-15489")
        self.assertTrue(versioning.is_version_at_least(client, "7.3"))

    def test_newer_is_supported(self):
        client = FakeClient(software="7.4.1-20000")
        self.assertTrue(versioning.is_version_at_least(client, "7.3"))

    def test_older_minor_is_not_supported(self):
        client = FakeClient(software="7.2.5-14000")
        self.assertFalse(versioning.is_version_at_least(client, "7.3"))

    def test_older_major_is_not_supported(self):
        client = FakeClient(software="7.1.0-14171")
        self.assertFalse(versioning.is_version_at_least(client, "7.3"))

    def test_unknown_version_fails_open(self):
        client = FakeClient(software="")
        self.assertTrue(versioning.is_version_at_least(client, "7.3"))


class TestMgmtVrfGating(unittest.TestCase):
    def test_management_interface_blocked_below_73(self):
        client = FakeClient(software="7.2.5-14000")
        instance = _Vsx(client)
        message, status, changed = instance.create_vsx(
            name_prefix="Test-VSX",
            system_mac_range="MAC POOL",
            keep_alive_interface_mode="management_interface",
        )
        self.assertFalse(status)
        self.assertFalse(changed)
        self.assertIn("7.3", message)
        # No configuration call should have been attempted.
        self.assertFalse([c for c in client.calls if c[0] == "post"])

    def test_mgmt_vrf_blocked_below_73(self):
        client = FakeClient(software="7.1.0-14171")
        instance = _Vsx(client)
        message, status, changed = instance.create_vsx(
            name_prefix="Test-VSX",
            system_mac_range="MAC POOL",
            keep_alive_interface_mode="routed",
            keep_alive_vrf="mgmt",
        )
        self.assertFalse(status)
        self.assertFalse(changed)
        self.assertIn("7.3", message)

    def test_management_interface_allowed_on_73(self):
        client = FakeClient(software="7.3.0-15489", pools=[MAC_POOL])
        instance = _Vsx(client)
        message, status, changed = instance.create_vsx(
            name_prefix="Test-VSX",
            system_mac_range="MAC POOL",
            keep_alive_interface_mode="management_interface",
            keep_alive_vrf="mgmt",
        )
        self.assertTrue(status)
        self.assertTrue(changed)
        posts = [c for c in client.calls if c[0] == "post"]
        self.assertEqual(len(posts), 1)
        body = json.loads(posts[0][2])
        self.assertEqual(
            body["keep_alive_interface_mode"], "management_interface",
        )
        self.assertEqual(body["keep_alive_vrf"], "mgmt")
        # No IPv4 keep alive pool is required in mgmt mode.
        self.assertNotIn("keepalive_ip_pool_range", body)

    def test_routed_mode_not_gated(self):
        client = FakeClient(
            software="7.2.5-14000",
            pools=[MAC_POOL, {"name": "IP POOL", "uuid": "ip-uuid"}],
        )
        instance = _Vsx(client)
        message, status, changed = instance.create_vsx(
            name_prefix="Test-VSX",
            system_mac_range="MAC POOL",
            keepalive_ip_pool_range="IP POOL",
            keep_alive_interface_mode="routed",
        )
        self.assertTrue(status)
        self.assertTrue(changed)


if __name__ == "__main__":
    unittest.main()
