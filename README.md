# house-lib

Shared Python package for the house automation NAS stack: Homey HTTP client, hub event ingest, deploy records, and `/health` build info.

**Not a runnable service.** Consumers: house-context, guest-stays, pool-heating-engine, eco-sessions, echo, house-master-engine.

## Install

```bash
pip install -e .
# or from GitHub (after publish):
# pip install "house-lib @ git+https://github.com/0xVorian/house-lib.git@v0.1.0"
```

NAS Docker: deploy stages a sibling `/volume5/docker/house-lib` clone into `.house-lib-src` in the consumer build context (see house-context Dockerfile + `deploy-nas-remote.sh`).

## Modules

| Import | Purpose |
|--------|---------|
| `house_lib.homey.AsyncHomeyClient` | Async Homey REST (ping, capabilities, logic vars) |
| `house_lib.homey.HomeyClient` | Sync Homey REST (pool-heating style) |
| `house_lib.hub_events.emit_event` | `POST /api/events/ingest` |
| `house_lib.hub_deploy.record_deployment` | `POST /api/deployments/record` |
| `house_lib.versioning.build_info` | `{service, version, git_sha?}` |

Domain logic (bookings, thermal model, eco eligibility) stays in service repos.

## House stack

Config registry: `C:\Users\Edouard\Projects\house-master-engine\docs\config.md`

When bumping `VERSION`, update `CHANGELOG.md` in the same commit.
