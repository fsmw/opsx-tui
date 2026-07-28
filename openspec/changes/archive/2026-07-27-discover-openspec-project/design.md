## Context

This change builds on the project foundation established in `bootstrap-opsx-tui-project`. The foundation provides: `pyproject.toml` with the `opsx-tui` entry point, a minimal Textual app shell (`OpsxTuiApp`), config models and hierarchical TOML loading, logging via ports, the four-layer hexagonal skeleton, and CI.

Currently `__main__.py` passes no args to the app and `app.py` shows a static welcome screen with no project awareness. This change adds the full discovery chain so the app starts on a known project or guides the user to provide one.

Constraints from existing code:
- `Path` import is allowed in domain only via `from pathlib import Path` (it's a data type, not I/O).
- Presentation must NOT import infrastructure or touch the filesystem.
- Infrastructure implements ports from domain.
- `opsx_tui.domain.ports.ConfigLoader` already exists; no other ports yet.
- `opsx_tui.infrastructure.toml_config_loader.TomlConfigLoader` exists.
- `opsx_tui.infrastructure.stdlib_logger.StdlibLogger` exists.
- Container wiring in `application/container.py`.

## Goals / Non-Goals

**Goals:**
- Domain models: `Project`, `Diagnostic`, `DiscoverySource`, `ProjectDiscoveryStrategy` protocol.
- Application service: `ProjectDiscoveryService` that orchestrates the strategy chain.
- Infrastructure strategies: `EnvVarDiscoverer`, `AncestorDiscoverer`, `GitRootDiscoverer`, `RecentProjectsDiscoverer`.
- Presentation: `CliArgDiscoverer` + `InteractiveProjectScreen`.
- `opsx-tui --project PATH` arg parsing in `__main__.py`.
- Wire discovery into `OpsxTuiApp.on_mount()`: run chain → if `None` → push interactive screen → if result → store as `app.project`.
- Recent projects JSON sidecar: write on successful discovery, read in `RecentProjectsDiscoverer`.
- Validation: `openspec/config.yaml` presence is required for validity; missing subdirs = WARNING.

**Non-Goals:**
- Full workspace reading (Change `read-openspec-workspace`).
- OpenSpec CLI validation (deferred to CLI adapter change).
- Git checkout or branch detection (deferred to Git phase).
- SQLite persistence (deferred; JSON sidecar is temporary).

## Decisions

### D1: Strategy protocol with `discover()` returning `Project | None`
**Choice:** `ProjectDiscoveryStrategy(Protocol)` with `discover() -> Project | None`. Each strategy is stateless; takes discovery context (cwd, env) via constructor.
**Why:** Clean isolation of strategies, easy to test individually, easy to add new ones. `None` = "not found, try next".
**Alternatives:** Single monolithic discoverer — rejected in exploration.

### D2: `--project` short-circuits the entire chain
**Choice:** If `--project PATH` is passed, the service validates that path directly and returns it (or marks invalid). No env var, ancestor walk, or any other strategy runs.
**Why:** Explicit user intent should not be overridden. Matches precedence order from `docs/01` §5.3.

### D3: Interactive screen is part of presentation, not a strategy
**Choice:** `ProjectDiscoveryService` returns `None` when no strategy finds a project. `OpsxTuiApp.on_mount()` pattern-matches: `None` → `push_screen(InteractiveProjectScreen)`; `Project` → store and proceed.
**Why:** The interactive screen is inherently UI — it wouldn't exist in a headless context. Separating it keeps strategies pure and the service reusable.

### D4: `Project` carries diagnostics, not validation exceptions
**Choice:** `Project.is_valid` is a boolean property computed from presence of `openspec/config.yaml`. `Project.diagnostics` is a tuple of `Diagnostic` objects (level + message). Strategies always return a `Project` if the path looks like an OpenSpec project — even with warnings. No exceptions for structural issues.
**Why:** The gate requires distinguishing "not found" from "invalid". Diagnostic collection lets the app display issues without aborting.

### D5: CLI arg passing — argparse in `__main__.py`, CliArgDiscoverer in presentation
**Choice:** `__main__.py` uses `argparse` to parse `--project PATH`. The resulting `Namespace` is passed to `OpsxTuiApp(project=...)`. Presentation's `CliArgDiscoverer` reads `app.project_arg` and returns a validated `Project` or `None`.
**Why:** Keeps arg parsing in the entry point without leaking it into the app. `CliArgDiscoverer` is a thin adapter that formats the path for the service.

### D6: Recent projects as JSON sidecar, not SQLite and not config
**Choice:** Write/read `~/.local/share/opsx-tui/recent-projects.json` via `platformdirs.user_data_dir`. Format: `{"recent_projects": [{"path": "...", "last_opened": "..."}, ...]}`. Max 10 entries, deduplicated.
**Why:** Config is for settings, not state. SQLite is deferred to a later change. JSON sidecar is trivially queryable and removable.

### D7: Ancestor walk — max depth
**Choice:** Walk up from cwd up to 10 levels or until `/` or a filesystem boundary (device change). Stop at the first directory containing `openspec/`.
**Why:** Prevent infinite loops with mount points. 10 levels is generous for any reasonable project tree.

### D8: Git root discoverer — `git rev-parse --show-toplevel` via subprocess, fallback to `.git` search
**Choice:** Try `git rev-parse --show-toplevel --path-format=absolute` first (handles worktrees). If `git` is unavailable or not a repo, fall back to walking up looking for `.git` (bare directory, not a file).
**Why:** Covers both standard repos and worktrees. Subprocess call is acceptable here (infrastructure layer, async-safe).
**Alternatives:** Pure-path `.git` search — rejected because it doesn't handle worktrees correctly.

### D9: No new PyPI dependencies
**Choice:** Use stdlib modules only: `argparse` (stdlib), `json`, `os`, `pathlib`, `subprocess`, `dataclasses`/Pydantic 2.
**Why:** The foundation already declares all needed deps. Adding a new dependency requires an ADR.

## Risks / Trade-offs

- **[Risk] Subprocess call in GitRootDiscoverer** — This is the only strategy that spawns a process. If `git` is missing or the repo is large, it could be slow (but sub-second in practice). The fallback path handles `FileNotFoundError`.
- **[Risk] Ancestor walk performance on NFS/network mounts** — 10 levels is bounded; even on slow filesystems it's a few directory checks. Acceptable.
- **[Risk] Interactive screen needs Textual's DirectoryTree** — `DirectoryTree` is a built-in Textual widget. Should work out of the box. Risk is styling and filter (only show dirs with `openspec/`). Low.
- **[Trade-off] JSON sidecar will be replaced by SQLite** — Accepted. The sidecar is deliberately separate and easy to migrate.
- **[Risk] `Path` import in domain** — Already established pattern in `errors.py` (uses `Path` type annotation). Domain uses `Path` as a type, not for I/O.