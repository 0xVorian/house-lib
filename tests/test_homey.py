from __future__ import annotations

import httpx
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
async def test_async_ping_failure() -> None:
    base = "http://homey.test"
    respx.get(f"{base}/api/manager/system").mock(side_effect=httpx.ConnectError("down"))
    client = AsyncHomeyClient(base, "token")
    assert await client.ping() is False
