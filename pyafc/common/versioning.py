# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

"""Helpers to detect AFC feature / API support based on the AFC version.

Some features are only available from a given AFC software version. When an
API endpoint used by pyafc is not available on the running AFC version, AFC
answers with an HTTP 404 (endpoint absent) or 406 (requested API version not
acceptable). These helpers turn that low-level condition into a clean,
uniform message for the user, both in pyafc and in the Ansible collection.
"""

from __future__ import annotations

from pyafc.common import exceptions

# HTTP status codes returned by AFC when an endpoint / feature is not
# available on the running version (endpoint absent, or the requested API
# version is refused).
UNSUPPORTED_STATUS = (404, 406)

# Cache of the AFC software version, keyed by the client base URL so we do
# not query the "versions" endpoint on every call.
_version_cache: dict = {}


def get_software_version(client) -> str | None:
    """Return the AFC software version string (e.g. "7.3.0-15489").

    The value is cached per AFC instance (client base URL). Returns None if
    the version cannot be determined.
    """
    key = str(getattr(client, "base_url", ""))
    if key not in _version_cache:
        try:
            result = client.get("versions").json().get("result") or {}
            _version_cache[key] = result.get("software")
        except Exception:
            _version_cache[key] = None
    return _version_cache[key]


def _parse_version(version: str | None) -> tuple[int, ...] | None:
    """Parse an AFC software version string into a comparable tuple.

    Examples:
        "7.3.0-15489" -> (7, 3, 0)
        "7.2" -> (7, 2)

    Returns None when the version cannot be parsed.
    """
    if not version:
        return None
    base = version.split("-")[0].split("+")[0]
    parts: list[int] = []
    for token in base.split("."):
        digits = "".join(ch for ch in token if ch.isdigit())
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts) if parts else None


def is_version_at_least(client, minimum: str) -> bool:
    """Return True when the running AFC version is >= ``minimum``.

    Args:
        client: AFC client used to query the running software version.
        minimum (str): Minimum version required, e.g. "7.3".

    Returns:
        bool: True if the running version is greater than or equal to
        ``minimum``. When the running version cannot be determined, this
        returns True (fail open) so a version-detection failure does not
        block an otherwise valid request.
    """
    current = _parse_version(get_software_version(client))
    target = _parse_version(minimum)
    if target is None:
        return True
    if current is None:
        return True
    length = max(len(current), len(target))
    current += (0,) * (length - len(current))
    target += (0,) * (length - len(target))
    return current >= target


def not_supported_message(
    feature: str,
    client=None,
    version: str | None = None,
) -> str:
    """Build a clean, uniform 'feature not supported' message."""
    if version is None and client is not None:
        version = get_software_version(client)
    version = version or "the running version"
    return (
        f"{feature} is not supported by AFC {version}. "
        "Please upgrade AFC to a version that provides this feature."
    )


def is_supported_response(response) -> bool:
    """Return False if the response indicates the feature is not available."""
    return response.status_code not in UNSUPPORTED_STATUS


def ensure_supported(response, feature: str, client=None) -> None:
    """Raise FeatureNotSupported when the endpoint / feature is unavailable.

    Args:
        response: The httpx response returned by an AFC API call.
        feature (str): Human-readable feature name used in the message.
        client: Optional AFC client, used to enrich the message with the
            running AFC version.

    Raises:
        exceptions.FeatureNotSupported: When the response status indicates the
            feature is not available on the running AFC version.
    """
    if not is_supported_response(response):
        raise exceptions.FeatureNotSupported(
            not_supported_message(feature, client=client),
        )
