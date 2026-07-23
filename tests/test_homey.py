from __future__ import annotations

import pytest
import respx

from house_lib.homey import AsyncHomeyClient, HomeyClient


@pytest.mark.asyncio
@respx.mock
async def test_async_ping_and_capability() -> None:
    base = "http://homey.test"
    respx.get(f"{base}/api/manager/system").respond(200, json={"ok": True})
    respx.get(f"{base}/api/manager/devices/device/dev1").respond(
        200,
        json={"capabilitiesObj": {"measure_temperature": {"value": 21.5}}},
    )

    client = AsyncHomeyClient(base, "token")
    assert await client.ping() is True
    assert await client.get_capability_value("dev1", "measure_temperature") == 21.5


@respx.mock
def test_sync_set_capability() -> None:
    base = "http://homey.test"
    route = respx.put(f"{base}/api/manager/devices/device/dev1/capability/onoff").respond(
        200, json={}
    )
    client = HomeyClient(base, "token")
    client.set_capability("dev1", "onoff", True)
    assert route.called
    assert route.calls.last.request.content == b'{"value":true}'


@pytest.mark.asyncio
@respx.mock
async def test_async_update_logic_variable_uses_flat_body() -> None:
    base = "http://homey.test"
    route = respx.put(f"{base}/api/manager/logic/variable/var1").respond(
        200, json={"id": "var1", "name": "hc_logic_synced_at", "type": "number", "value": 42}
    )
    client = AsyncHomeyClient(base, "token")
    result = await client.update_logic_variable("var1", 42)
    assert route.called
    assert route.calls.last.request.content == b'{"value":42}'
    assert result["value"] == 42


@pytest.mark.asyncio
@respx.mock
async def test_async_read_device_capabilities_meta() -> None:
    base = "http://homey.test"
    respx.get(f"{base}/api/manager/devices/device/dev1").respond(
        200,
        json={
            "capabilitiesObj": {
                "target_temperature": {
                    "value": 21.0,
                    "lastUpdated": "2026-07-23T07:12:00+00:00",
                },
                "onoff": {"value": True, "lastUpdated": 1_700_000_000_000},
            }
        },
    )

    client = AsyncHomeyClient(base, "token")
    meta = await client.read_device_capabilities_meta(
        "dev1",
        ["target_temperature", "onoff", "missing"],
    )
    assert meta["target_temperature"]["value"] == 21.0
    assert meta["target_temperature"]["last_updated"] == "2026-07-23T07:12:00+00:00"
    assert meta["onoff"]["value"] is True
    assert meta["onoff"]["last_updated"] is not None
    assert meta["missing"]["value"] is None


@respx.mock
def test_sync_read_device_capabilities_meta() -> None:
    base = "http://homey.test"
    respx.get(f"{base}/api/manager/devices/device/dev1").respond(
        200,
        json={
            "capabilitiesObj": {
                "measure_temperature": {"value": 18.5, "lastUpdated": "2026-07-23T08:00:00+00:00"},
            }
        },
    )
    client = HomeyClient(base, "token")
    meta = client.read_device_capabilities_meta("dev1", ["measure_temperature"])
    assert meta["measure_temperature"]["value"] == 18.5
    assert meta["measure_temperature"]["last_updated"] == "2026-07-23T08:00:00+00:00"
