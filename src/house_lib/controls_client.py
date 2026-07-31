"""Fetch runtime settings from house-context /controls with sticky cache."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import httpx

log = logging.getLogger(__name__)

Source = Literal["live", "cached", "bootstrap"]


@dataclass
class ControlsSnapshot:
    values: dict[str, Any] = field(default_factory=dict)
    source: Source = "bootstrap"
    fetched_at: str | None = None
    age_seconds: float | None = None

    def get_bool(self, control_id: str, default: bool = True) -> bool:
        if control_id in self.values:
            return bool(self.values[control_id])
        return default

    def get_float(self, control_id: str, default: float) -> float:
        if control_id in self.values:
            return float(self.values[control_id])
        return default

    def get_int(self, control_id: str, default: int) -> int:
        if control_id in self.values:
            return int(self.values[control_id])
        return default

    def get_str(self, control_id: str, default: str) -> str:
        if control_id in self.values:
            return str(self.values[control_id])
        return default

    def get_json(self, control_id: str, default: Any = None) -> Any:
        if control_id in self.values:
            return self.values[control_id]
        return default


def _auth_headers(token: str | None) -> dict[str, str]:
    secret = (token or "").strip()
    if secret:
        return {"Authorization": f"Bearer {secret}"}
    return {}


def _parse_iso_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _age_seconds(fetched_at: str | None) -> float | None:
    dt = _parse_iso_timestamp(fetched_at)
    if dt is None:
        return None
    return max(0.0, (datetime.now(UTC) - dt.astimezone(UTC)).total_seconds())


class ControlsClient:
    """Poll house-context /controls once per tick; sticky cache on failure."""

    def __init__(
        self,
        base_url: str,
        *,
        token: str | None = None,
        cache_path: Path | str | None = None,
        timeout: float = 5.0,
    ) -> None:
        self.base_url = (base_url or "").rstrip("/")
        self.token = token
        self.cache_path = Path(cache_path) if cache_path else None
        self.timeout = timeout
        self._memory_cache: dict[str, Any] | None = None
        self._memory_fetched_at: str | None = None

    def fetch(self, prefix: str | None = None) -> ControlsSnapshot:
        if not self.base_url:
            return ControlsSnapshot(source="bootstrap")

        live = self._fetch_live()
        if live is not None:
            values, fetched_at = live
            self._persist_cache(values, fetched_at)
            filtered = _filter_prefix(values, prefix)
            return ControlsSnapshot(
                values=filtered,
                source="live",
                fetched_at=fetched_at,
                age_seconds=_age_seconds(fetched_at),
            )

        cached_values, cached_at = self._load_cache()
        if cached_values is not None:
            filtered = _filter_prefix(cached_values, prefix)
            return ControlsSnapshot(
                values=filtered,
                source="cached",
                fetched_at=cached_at,
                age_seconds=_age_seconds(cached_at),
            )

        return ControlsSnapshot(source="bootstrap")

    def _fetch_live(self) -> tuple[dict[str, Any], str] | None:
        url = f"{self.base_url}/controls"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=_auth_headers(self.token))
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            log.warning("House-context controls unavailable (%s): %s", url, exc)
            return None

        controls = payload.get("controls") if isinstance(payload, dict) else None
        if not isinstance(controls, list):
            return None

        values: dict[str, Any] = {}
        for item in controls:
            if not isinstance(item, dict):
                continue
            control_id = item.get("id")
            if not control_id:
                continue
            if item.get("value") is not None:
                values[str(control_id)] = item["value"]

        fetched_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        return values, fetched_at

    def _persist_cache(self, values: dict[str, Any], fetched_at: str) -> None:
        self._memory_cache = dict(values)
        self._memory_fetched_at = fetched_at
        if not self.cache_path:
            return
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(
                json.dumps({"fetched_at": fetched_at, "values": values}, indent=2),
                encoding="utf-8",
            )
        except OSError as exc:
            log.warning("Failed to persist controls cache (%s): %s", self.cache_path, exc)

    def _load_cache(self) -> tuple[dict[str, Any] | None, str | None]:
        if self._memory_cache is not None:
            return self._memory_cache, self._memory_fetched_at
        if not self.cache_path or not self.cache_path.is_file():
            return None, None
        try:
            payload = json.loads(self.cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            log.warning("Failed to load controls cache (%s): %s", self.cache_path, exc)
            return None, None
        if not isinstance(payload, dict):
            return None, None
        values = payload.get("values")
        if not isinstance(values, dict):
            return None, None
        self._memory_cache = {str(key): val for key, val in values.items()}
        fetched_at = payload.get("fetched_at")
        self._memory_fetched_at = str(fetched_at) if fetched_at else None
        return self._memory_cache, self._memory_fetched_at


def _filter_prefix(values: dict[str, Any], prefix: str | None) -> dict[str, Any]:
    if not prefix:
        return dict(values)
    return {key: value for key, value in values.items() if key.startswith(prefix)}


def runtime_settings_payload(snapshot: ControlsSnapshot, *, stale_after_seconds: float = 600) -> dict[str, Any]:
    age = snapshot.age_seconds
    stale = age is not None and age > stale_after_seconds
    return {
        "source": snapshot.source,
        "fetched_at": snapshot.fetched_at,
        "age_seconds": age,
        "stale": stale,
    }


def parse_time_windows(value: Any) -> list[dict[str, int]]:
    """Normalize time window control values to {start_min, end_min} dicts."""
    if not isinstance(value, list):
        raise ValueError("time_windows value must be a list")
    windows: list[dict[str, int]] = []
    for index, window in enumerate(value):
        if isinstance(window, dict):
            start = window.get("start_min")
            end = window.get("end_min")
        elif isinstance(window, (list, tuple)) and len(window) == 2:
            start, end = window
        else:
            raise ValueError(f"time_windows entry {index} is invalid")
        windows.append({"start_min": int(start), "end_min": int(end)})
    return windows
