## Why

OPSX TUI's first job is to find an OpenSpec project. Without detection, nothing else works: no workspace reading, no Kanban, no command execution. Currently the app opens a blank welcome screen with no awareness of any project. This change gives it the full 6-step discovery chain so the user lands on a project immediately or gets a clear interactive fallback.

## What Changes

- Add `opsx-tui --project PATH` CLI argument, `OPSX_TUI_PROJECT` env var support, and the full discovery chain: ancestor walk → Git root → recent projects → interactive picker.
- Domain: `Project`, `Diagnostic`, `DiscoverySource` Pydantic models. `ProjectDiscoveryStrategy` Protocol.
- Application: `ProjectDiscoveryService` orchestrating the chain. Each strategy returns `Project | None`; the service tries them in order. `--project` short-circuits.
- Infrastructure: `EnvVarDiscoverer`, `AncestorDiscoverer`, `GitRootDiscoverer`, `RecentProjectsDiscoverer`.
- Presentation: `CliArgDiscoverer` (reads parsed args), `InteractiveProjectScreen` (file tree picker if chain yields nothing).
- Recent projects persisted as JSON sidecar at `~/.local/share/opsx-tui/recent-projects.json` via `platformdirs`.
- Validation: detects `openspec/` dir presence; missing `config.yaml` or subdirs = WARNING diagnostic but still valid. Distinguishes "not found" (discovery returns `None`) from "invalid" (found but structure wrong).
- Wire discovery into app startup: `App.on_mount` calls service; if `None`, push interactive screen.
- Project model becomes a first-class object the rest of the app can reference.

## Capabilities

### New Capabilities
- `project-discovery`: CLI arg + env var + ancestor walk + Git root + recent projects + interactive selector for detecting OpenSpec project roots.

### Modified Capabilities
- `project-foundation`: Wire `opsx-tui --project` arg; extend `__main__.py` with argparse.

## Impact

- New files in `src/opsx_tui/domain/`: `project.py` (Project, Diagnostic, DiscoverySource), `project_discovery.py` (strategy protocol).
- New file in `src/opsx_tui/application/`: `project_discovery_service.py`.
- New files in `src/opsx_tui/infrastructure/`: `env_var_discoverer.py`, `ancestor_discoverer.py`, `git_root_discoverer.py`, `recent_projects_discoverer.py`.
- New files in `src/opsx_tui/presentation/`: `project_screen.py` (interactive picker).
- Modified: `src/opsx_tui/__main__.py` (add argparse), `src/opsx_tui/presentation/app.py` (wire discovery into `on_mount`).
- New tests per strategy + integration test for the full chain + TUI test for interactive screen.
- No new PyPI dependencies (`platformdirs` already declared).