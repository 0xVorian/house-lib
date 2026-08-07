# house-lib

Shared Python package for the house automation NAS stack: Homey HTTP client, hub event ingest, deploy records, and `/health` build info.

**Not a runnable service.** Consumers: house-context (runtime), plus other NAS services as they migrate off local twins.

## Consume this if you need

| Need | Use | Do not |
|------|-----|--------|
| Homey REST (async) | `house_lib.homey.AsyncHomeyClient` | Copy a local Homey HTTP client |
| Homey REST (sync) | `house_lib.homey.HomeyClient` | Duplicate pool/HVAC-style wrappers |
| Runtime controls | `house_lib.ControlsClient` | Local `/controls` fetch + cache twins |
| Hub event ingest | `house_lib.hub_events.emit_event` | Local `events.py` twins for `POST /api/events/ingest` |
| Deploy SHA record | `house_lib.hub_deploy.record_deployment` | Ad-hoc deploy POSTs |
| `/health` build fields | `house_lib.versioning.build_info` | Per-service `build_info` copies |

Domain logic (bookings, thermal model, eco eligibility, planner policy) stays in service repos.

## Install

```bash
pip install -e .
# or from GitHub (after publish):
# pip install "house-lib @ git+https://github.com/0xVorian/house-lib.git@v0.1.1"
```

NAS Docker: deploy stages a sibling `/volume5/docker/house-lib` clone into `.house-lib-src` in the consumer build context (see house-context Dockerfile + `deploy-nas-remote.sh`).

## Modules

| Import | Purpose |
|--------|---------|
| `house_lib.homey.AsyncHomeyClient` | Async Homey REST (ping, capabilities, logic vars) |
| `house_lib.homey.HomeyClient` | Sync Homey REST (pool-heating style) |
| `house_lib.ControlsClient` | Batched `GET /controls` with sticky cache |
| `house_lib.hub_events.emit_event` | `POST /api/events/ingest` |
| `house_lib.hub_deploy.record_deployment` | `POST /api/deployments/record` |
| `house_lib.versioning.build_info` | `{service, version, git_sha?}` |

## House stack

Catalog node `house-lib` — zone `lib`, no port, no runbook, `depends_on: []`. It is a **shared package, not a Docker service**: it never appears in health checks or deploy records of its own. Consumers today: [house-context](https://github.com/0xVorian/house-context) (runtime); other NAS services as they migrate off local twins.

Config registry: [house-master-engine/docs/config.md](https://github.com/0xVorian/house-master-engine/blob/main/docs/config.md). Full stack map (do not duplicate it here): hub [`config/services.yaml`](https://github.com/0xVorian/house-master-engine/blob/main/config/services.yaml) `catalog` · `#/stack` · `GET /api/registry`.

When bumping `VERSION`, update `CHANGELOG.md` in the same commit — consumers pin or rebuild against it.
