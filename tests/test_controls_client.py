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
