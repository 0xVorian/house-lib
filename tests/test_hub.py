from __future__ import annotations

import pytest
import respx

from house_lib.hub_deploy import record_deployment
from house_lib.hub_events import emit_event, emit_event_sync


@pytest.mark.asyncio
async def test_emit_event_skips_without_secret() -> None:
    ok = await emit_event(
        service_id="test",
        ingest_url="http://hub/api/events/ingest",
        ingest_secret="",
        event_type="tick",
        ok=True,
        summary="hi",
    )
    assert ok is False


@pytest.mark.asyncio
@respx.mock
async def test_emit_event_posts_body() -> None:
    route = respx.post("http://hub/api/events/ingest").respond(200, json={"ok": True})
    ok = await emit_event(
        service_id="guest-stays",
        ingest_url="http://hub/api/events/ingest",
        ingest_secret="secret",
        event_type="sync",
        ok=True,
        summary="synced",
        payload={"n": 1},
    )
    assert ok is True
    assert route.called
    assert route.calls.last.request.headers["Authorization"] == "Bearer secret"


@respx.mock
def test_emit_event_sync() -> None:
    respx.post("http://hub/api/events/ingest").respond(200, json={"ok": True})
    assert (
        emit_event_sync(
            service_id="pool-heating-engine",
            ingest_url="http://hub/api/events/ingest",
            ingest_secret="secret",
            event_type="tick",
            ok=True,
            summary="ok",
        )
        is True
    )


@pytest.mark.asyncio
@respx.mock
async def test_record_deployment() -> None:
    route = respx.post("http://hub/api/deployments/record").respond(200, json={"ok": True})
    ok = await record_deployment(
        hub_base_url="http://hub",
        secret="secret",
        service_id="echo",
        git_sha="abcdef1234567890",
        version="0.1.0",
    )
    assert ok is True
    assert route.called
    body = route.calls.last.request.content
    assert b'"git_sha":"abcdef123456"' in body
