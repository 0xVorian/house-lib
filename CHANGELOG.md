# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
