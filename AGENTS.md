# house-lib

Shared Python helpers for house automation NAS services.

## Consume this if you need

- **Homey client** — `AsyncHomeyClient` / `HomeyClient`
- **Hub events / deploy** — `hub_events.emit_event`, `hub_deploy.record_deployment`
- **Runtime controls** — `ControlsClient` (batched `GET /controls` + sticky cache)
- **Health build info** — `versioning.build_info`

Do **not** add a local twin of these modules in a NAS service; prefer house-lib and stage via `.house-lib-src` when the Docker image needs it.

This is a **library**, not a Docker service. When bumping `VERSION`, update `CHANGELOG.md` in the same commit.

Hub sync & stack map: `.cursor/rules/house-config-hub.mdc`. Open gates: hub [status.md](https://github.com/0xVorian/house-master-engine/blob/main/docs/status.md).
