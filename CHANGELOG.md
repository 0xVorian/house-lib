# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3] - 2026-08-07

### Changed

- README: fuller consumer list (pool / HVAC / eco / echo) and pin example at current release

## [0.3.2] - 2026-08-07

### Fixed

- Packaging honesty: `pyproject.toml` version was stuck at 0.3.0 while `VERSION` / `__version__` were 0.3.1 — align all three and assert in tests
- README / AGENTS: mention `ControlsClient` for consumers

## [0.3.1] - 2026-07-31

### Fixed

- `ControlsClient.fetch(prefix=...)` no longer persists a prefix-filtered subset to the sticky cache (audit A-005)

### Note

- Wheel / `pyproject.toml` metadata for this release incorrectly still reported 0.3.0; use 0.3.2+

## [0.3.0] - 2026-07-31

### Added

- `ControlsSnapshot.get_json()` and `parse_time_windows()` for structured runtime controls

## [0.2.0] - 2026-07-31

### Added

- `ControlsClient` — batched `GET /controls` with sticky disk/memory cache for NAS planners
- `ControlsSnapshot`, `runtime_settings_payload()` — merge helpers for planner `/status`

## [0.1.6] - 2026-07-31

### Fixed

- `list_zones()` uses Homey `/api/manager/zones/zone` (not the non-existent flow zone path)

## [0.1.5] - 2026-07-31

### Added

- `AsyncHomeyClient.list_devices()` / `list_zones()` and sync `HomeyClient` equivalents — Homey catalog for hub device registry UI

## [0.1.4] - 2026-07-27

### Changed

- README / AGENTS: discovery pointers — consume house-lib for Homey client, hub events, build_info; do not add local twins

## [0.1.3] - 2026-07-23

### Added

- `AsyncHomeyClient.reset_api_call_count()` and `api_call_count` — per-tick Homey REST budget observability

## [0.1.2] - 2026-07-23

### Added

- `read_device_capabilities_meta()` on async and sync Homey clients — returns `{value, last_updated}` per capability (for house-context device snapshot poller)

## [0.1.1] - 2026-07-19

### Fixed

- Homey Logic variable PUT uses flat `{"value": …}` body — nested `variable` wrapper returned 200 but did not change the value

### Changed

- README install example pins `@v0.1.1`

## [0.1.0] - 2026-07-16

### Added

- Initial shared package for NAS house services
- `AsyncHomeyClient` / `HomeyClient` — Homey REST ping, capability read/write, logic variables
- `emit_event` / `emit_event_sync` — hub activity ingest
- `record_deployment` / `record_deployment_sync` — hub deploy records
- `build_info` / `read_version` / `read_git_sha` — standard `/health` version payload
- `utc_now_iso` helper
