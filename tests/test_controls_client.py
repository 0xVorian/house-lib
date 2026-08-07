from __future__ import annotations

import json
from pathlib import Path

import httpx
import respx

from house_lib.controls_client import ControlsClient, runtime_settings_payload


@respx.mock
def test_fetch_live_populates_values_and_cache(tmp_path: Path) -> None:
    cache_path = tmp_path / "runtime-settings-cache.json"
    client = ControlsClient(
        "http://house-context.test:8095",
        token="secret",
        cache_path=cache_path,
    )
    respx.get("http://house-context.test:8095/controls").mock(
        return_value=httpx.Response(
            200,
            json={
                "controls": [
                    {"id": "pool_heating.actuation_enabled", "value": False},
                    {"id": "pool_heating.target_guest_c", "value": 27.5},
                    {"id": "hvac.enabled", "value": True},
                ]
            },
        )
    )

    snapshot = client.fetch(prefix="pool_heating")
    assert snapshot.source == "live"
    assert snapshot.values["pool_heating.actuation_enabled"] is False
    assert snapshot.values["pool_heating.target_guest_c"] == 27.5
    assert "hvac.enabled" not in snapshot.values
    assert cache_path.is_file()


@respx.mock
def test_fetch_uses_cache_when_live_unavailable(tmp_path: Path) -> None:
    cache_path = tmp_path / "runtime-settings-cache.json"
    cache_path.write_text(
        json.dumps(
            {
                "fetched_at": "2026-07-31T12:00:00Z",
                "values": {"hvac.actuation_enabled": False},
            }
        ),
        encoding="utf-8",
    )
    client = ControlsClient("http://house-context.test:8095", cache_path=cache_path)
    respx.get("http://house-context.test:8095/controls").mock(
        return_value=httpx.Response(503, json={"detail": "down"})
    )

    snapshot = client.fetch(prefix="hvac")
    assert snapshot.source == "cached"
    assert snapshot.values["hvac.actuation_enabled"] is False


def test_runtime_settings_payload_marks_stale() -> None:
    from house_lib.controls_client import ControlsSnapshot

    payload = runtime_settings_payload(
        ControlsSnapshot(source="cached", fetched_at="2026-07-31T12:00:00Z", age_seconds=900),
        stale_after_seconds=600,
    )
    assert payload["stale"] is True
    assert payload["source"] == "cached"


_CONTROLS_PAYLOAD = {
    "controls": [
        {"id": "pool_heating.actuation_enabled", "value": False},
        {"id": "pool_heating.target_guest_c", "value": 27.5},
        {"id": "hvac.enabled", "value": True},
        {"id": "hvac.target_guest_c", "value": 21.0},
    ]
}


@respx.mock
def test_prefix_fetch_persists_full_cache_not_subset(tmp_path: Path) -> None:
    """Regression A-005: prefix filter must not shrink persisted cache."""
    cache_path = tmp_path / "runtime-settings-cache.json"
    client = ControlsClient("http://house-context.test:8095", cache_path=cache_path)
    route = respx.get("http://house-context.test:8095/controls").mock(
        return_value=httpx.Response(200, json=_CONTROLS_PAYLOAD)
    )

    hvac_snapshot = client.fetch(prefix="hvac")
    assert hvac_snapshot.source == "live"
    assert set(hvac_snapshot.values) == {"hvac.enabled", "hvac.target_guest_c"}

    cached = json.loads(cache_path.read_text(encoding="utf-8"))
    assert set(cached["values"]) == {
        "pool_heating.actuation_enabled",
        "pool_heating.target_guest_c",
        "hvac.enabled",
        "hvac.target_guest_c",
    }

    route.mock(return_value=httpx.Response(200, json=_CONTROLS_PAYLOAD))
    pool_snapshot = client.fetch(prefix="pool_heating")
    assert pool_snapshot.source == "live"
    assert set(pool_snapshot.values) == {
        "pool_heating.actuation_enabled",
        "pool_heating.target_guest_c",
    }


@respx.mock
def test_different_prefix_served_from_full_cache_when_live_down(tmp_path: Path) -> None:
    cache_path = tmp_path / "runtime-settings-cache.json"
    client = ControlsClient("http://house-context.test:8095", cache_path=cache_path)
    route = respx.get("http://house-context.test:8095/controls").mock(
        return_value=httpx.Response(200, json=_CONTROLS_PAYLOAD)
    )

    client.fetch(prefix="hvac")
    route.mock(return_value=httpx.Response(503, json={"detail": "down"}))

    pool_snapshot = client.fetch(prefix="pool_heating")
    assert pool_snapshot.source == "cached"
    assert set(pool_snapshot.values) == {
        "pool_heating.actuation_enabled",
        "pool_heating.target_guest_c",
    }


def test_parse_time_windows_accepts_dicts_and_pairs() -> None:
    from house_lib.controls_client import parse_time_windows

    assert parse_time_windows([{"start_min": 88, "end_min": 418}]) == [
        {"start_min": 88, "end_min": 418}
    ]
    assert parse_time_windows([[100, 200]]) == [{"start_min": 100, "end_min": 200}]


def test_get_bool_default_is_fail_closed() -> None:
    from house_lib.controls_client import ControlsSnapshot

    snapshot = ControlsSnapshot(values={})
    assert snapshot.get_bool("missing.flag") is False
    assert snapshot.get_bool("missing.flag", True) is True


def test_get_bool_coerces_string_false() -> None:
    from house_lib.controls_client import ControlsSnapshot, coerce_bool

    snapshot = ControlsSnapshot(values={"hvac.enabled": "false", "hvac.actuation_enabled": "0"})
    assert snapshot.get_bool("hvac.enabled", True) is False
    assert snapshot.get_bool("hvac.actuation_enabled", True) is False
    assert coerce_bool("true") is True
    assert coerce_bool("yes") is True
    assert coerce_bool(1) is True
    assert coerce_bool(0) is False
