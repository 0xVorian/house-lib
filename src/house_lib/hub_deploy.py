"""POST deploy records to house-master-engine."""

from __future__ import annotations

import logging
from typing import Any

import httpx

log = logging.getLogger(__name__)


def _record_url(hub_base_url: str) -> str:
    return f"{hub_base_url.rstrip('/')}/api/deployments/record"


async def record_deployment(
    *,
    hub_base_url: str,
    secret: str,
    service_id: str,
    git_sha: str,
    version: str | None = None,
    source: str = "house-lib",
    timeout: float = 10.0,
) -> bool:
    hub_base_url = (hub_base_url or "").strip()
    secret = (secret or "").strip()
    git_sha = (git_sha or "").strip()
    if not hub_base_url or not secret or not git_sha:
        log.debug("Deploy record skipped — hub URL, secret, or git_sha unset")
        return False

    body: dict[str, Any] = {
        "service_id": service_id,
        "git_sha": git_sha[:12],
        "source": source,
    }
    if version:
        body["version"] = version

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                _record_url(hub_base_url),
                json=body,
                headers={"Authorization": f"Bearer {secret}"},
            )
            response.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        log.warning("Deploy record failed: %s", exc)
        return False


def record_deployment_sync(
    *,
    hub_base_url: str,
    secret: str,
    service_id: str,
    git_sha: str,
    version: str | None = None,
    source: str = "house-lib",
    timeout: float = 10.0,
) -> bool:
    hub_base_url = (hub_base_url or "").strip()
    secret = (secret or "").strip()
    git_sha = (git_sha or "").strip()
    if not hub_base_url or not secret or not git_sha:
        log.debug("Deploy record skipped — hub URL, secret, or git_sha unset")
        return False

    body: dict[str, Any] = {
        "service_id": service_id,
        "git_sha": git_sha[:12],
        "source": source,
    }
    if version:
        body["version"] = version

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(
                _record_url(hub_base_url),
                json=body,
                headers={"Authorization": f"Bearer {secret}"},
            )
            response.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        log.warning("Deploy record failed: %s", exc)
        return False
