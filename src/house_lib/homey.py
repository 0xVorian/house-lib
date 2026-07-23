"""Homey Pro local API clients (async + sync)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

import httpx

log = logging.getLogger(__name__)


def _parse_last_updated(raw: Any) -> str | None:
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        ts = float(raw)
        if ts > 1_000_000_000_000:
            ts /= 1000.0
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    if isinstance(raw, str):
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except ValueError:
            return None
    return None


def _capability_meta(caps_obj: dict[str, Any], capability: str) -> dict[str, Any]:
    cap_data = caps_obj.get(capability) or {}
    return {
        "value": cap_data.get("value"),
        "last_updated": _parse_last_updated(cap_data.get("lastUpdated")),
    }


class AsyncHomeyClient:
    """Async Homey REST client — base_url + bearer token only (no service Settings)."""

    def __init__(self, base_url: str, token: str, *, timeout: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {token}"}
        self.timeout = timeout

    async def _get(self, path: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}{path}", headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, dict) else {}

    async def _put(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(
                f"{self.base_url}{path}",
                headers=self.headers,
                json=body,
            )
            response.raise_for_status()
            if not response.content:
                return {}
            data = response.json()
            return data if isinstance(data, dict) else {}

    async def ping(self) -> bool:
        try:
            await self._get("/api/manager/system")
            return True
        except Exception as exc:
            log.warning("Homey ping failed: %s", exc)
            return False

    async def get_device(self, device_id: str) -> dict[str, Any]:
        return await self._get(f"/api/manager/devices/device/{device_id}")

    async def get_capability_value(self, device_id: str, capability: str) -> Any:
        data = await self.get_device(device_id)
        caps = data.get("capabilitiesObj") or {}
        cap = caps.get(capability) or {}
        return cap.get("value")

    async def read_device_capabilities(
        self, device_id: str, capabilities: list[str]
    ) -> dict[str, Any]:
        data = await self.get_device(device_id)
        caps_obj = data.get("capabilitiesObj") or {}
        result: dict[str, Any] = {}
        for cap in capabilities:
            cap_data = caps_obj.get(cap) or {}
            result[cap] = cap_data.get("value")
        return result

    async def read_device_capabilities_meta(
        self, device_id: str, capabilities: list[str]
    ) -> dict[str, dict[str, Any]]:
        data = await self.get_device(device_id)
        caps_obj = data.get("capabilitiesObj") or {}
        return {cap: _capability_meta(caps_obj, cap) for cap in capabilities}

    async def set_capability(self, device_id: str, capability: str, value: Any) -> None:
        encoded = quote(capability, safe="")
        await self._put(
            f"/api/manager/devices/device/{device_id}/capability/{encoded}",
            {"value": value},
        )

    async def list_logic_variables(self) -> dict[str, Any]:
        data = await self._get("/api/manager/logic/variable")
        return data if isinstance(data, dict) else {}

    async def update_logic_variable(self, variable_id: str, value: Any) -> dict[str, Any]:
        # Homey local REST expects a flat body. Nested {"variable":{"value":…}} returns
        # HTTP 200 but leaves the value unchanged (verified on Homey Pro).
        return await self._put(
            f"/api/manager/logic/variable/{variable_id}",
            {"value": value},
        )


class HomeyClient:
    """Sync Homey REST client for planners that are not async (e.g. pool-heating-engine)."""

    def __init__(self, base_url: str, token: str, *, timeout: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {token}"}
        self.timeout = timeout

    def _get(self, path: str) -> dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(f"{self.base_url}{path}", headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, dict) else {}

    def _put(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.put(
                f"{self.base_url}{path}",
                headers=self.headers,
                json=body,
            )
            response.raise_for_status()
            if not response.content:
                return {}
            data = response.json()
            return data if isinstance(data, dict) else {}

    def ping(self) -> bool:
        try:
            self._get("/api/manager/system")
            return True
        except Exception as exc:
            log.warning("Homey ping failed: %s", exc)
            return False

    def get_device(self, device_id: str) -> dict[str, Any]:
        return self._get(f"/api/manager/devices/device/{device_id}")

    def capability(self, device_id: str, capability: str) -> Any:
        data = self.get_device(device_id)
        caps = data.get("capabilitiesObj") or {}
        return (caps.get(capability) or {}).get("value")

    def read_device_capabilities_meta(
        self, device_id: str, capabilities: list[str]
    ) -> dict[str, dict[str, Any]]:
        data = self.get_device(device_id)
        caps_obj = data.get("capabilitiesObj") or {}
        return {cap: _capability_meta(caps_obj, cap) for cap in capabilities}

    def set_capability(self, device_id: str, capability: str, value: Any) -> None:
        encoded = quote(capability, safe="")
        self._put(
            f"/api/manager/devices/device/{device_id}/capability/{encoded}",
            {"value": value},
        )
