"""POST structured activity events to house-master-engine."""

from __future__ import annotations

import logging
from typing import Any

import httpx

log = logging.getLogger(__name__)


def _build_body(
    *,
    service_id: str,
    event_type: str,
    ok: bool,
    summary: str,
    payload: dict[str, Any] | None,
    occurred_at: str | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "service_id": service_id,
        "event_type": event_type,
        "ok": ok,
        "summary": summary,
        "payload": payload or {},
    }
    if occurred_at:
        body["occurred_at"] = occurred_at
    return body


async def emit_event(
    *,
    service_id: str,
    ingest_url: str,
    ingest_secret: str,
    event_type: str,
    ok: bool,
    summary: str,
    payload: dict[str, Any] | None = None,
    occurred_at: str | None = None,
    timeout: float = 10.0,
) -> bool:
    ingest_url = (ingest_url or "").strip()
    ingest_secret = (ingest_secret or "").strip()
    if not ingest_url or not ingest_secret:
        log.debug("Event ingest skipped — ingest URL or secret unset")
        return False

    body = _build_body(
        service_id=service_id,
        event_type=event_type,
        ok=ok,
        summary=summary,
        payload=payload,
        occurred_at=occurred_at,
    )
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                ingest_url,
                json=body,
                headers={"Authorization": f"Bearer {ingest_secret}"},
            )
            response.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        log.warning("Event ingest failed: %s", exc)
        return False


def emit_event_sync(
    *,
    service_id: str,
    ingest_url: str,
    ingest_secret: str,
    event_type: str,
    ok: bool,
    summary: str,
    payload: dict[str, Any] | None = None,
    occurred_at: str | None = None,
    timeout: float = 10.0,
) -> bool:
    ingest_url = (ingest_url or "").strip()
    ingest_secret = (ingest_secret or "").strip()
    if not ingest_url or not ingest_secret:
        log.debug("Event ingest skipped — ingest URL or secret unset")
        return False

    body = _build_body(
        service_id=service_id,
        event_type=event_type,
        ok=ok,
        summary=summary,
        payload=payload,
        occurred_at=occurred_at,
    )
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(
                ingest_url,
                json=body,
                headers={"Authorization": f"Bearer {ingest_secret}"},
            )
            response.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        log.warning("Event ingest failed: %s", exc)
        return False
