# house-lib

Shared Python helpers for house automation NAS services.

## Consume this if you need

- **Homey client** — `AsyncHomeyClient` / `HomeyClient`
- **Hub events / deploy** — `hub_events.emit_event`, `hub_deploy.record_deployment`
- **Health build info** — `versioning.build_info`

Do **not** add a local twin of these modules in a NAS service; prefer house-lib and stage via `.house-lib-src` when the Docker image needs it.

## House stack

Part of the house automation stack. Config registry:

`C:\Users\Edouard\Projects\house-master-engine\docs\config.md`

This is a **library**, not a Docker service. After changing the public API or install/deploy story, update house-master-engine (`docs/inventory.md`, `docs/architecture.md`, `docs/optimization.md`, `docs/shore-up.md`, and `catalog.nodes` if purpose/deps change) before finishing. See `.cursor/rules/house-config-hub.mdc`. For “where does X live?”, use hub `catalog` / `#/stack` / `GET /api/registry`.

When bumping `VERSION`, update `CHANGELOG.md` in the same commit.
