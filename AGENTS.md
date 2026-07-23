# house-lib

Shared Python helpers for house automation NAS services.

## House stack

Part of the house automation stack. Config registry:

`C:\Users\Edouard\Projects\house-master-engine\docs\config.md`

This is a **library**, not a Docker service. After changing the public API or install/deploy story, update house-master-engine (`docs/inventory.md`, `docs/architecture.md`, `docs/optimization.md`, `docs/shore-up.md`) before finishing.

When bumping `VERSION`, update `CHANGELOG.md` in the same commit.

## Cursor Cloud specific instructions

Cloud VMs come with dependencies pre-installed by the environment update script into a **shared Python venv at `~/house-venv`** (already on `PATH` via `~/.bashrc`), so `python`, `ruff`, and `pytest` resolve to it without activating anything. This library is installed **editable** (`pip install -e .`) into that venv, so consumers like `house-context` import your local changes directly.

- **Lint + tests:** `scripts/ci-local.sh` (equivalently `python -m ruff check . && python -m pytest -q`, 11 tests).
- Not a service — nothing to run; validate via tests and by importing from a sibling service.
