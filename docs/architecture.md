# Architecture

## Overview

OPSX TUI uses a hexagonal (ports-and-adapters) architecture with four layers.
Dependencies point **inward only** — no layer may import from a layer outside
itself.

## Layer diagram

```
┌─────────────────────────────────────────┐
│              Presentation               │
│ Textual screens, widgets, controllers   │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│              Application                │
│ Use cases, services, orchestration      │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│                Domain                   │
│ Pydantic models, rules, contracts       │
└────────────────────▲────────────────────┘
                     │
┌────────────────────┴────────────────────┐
│            Infrastructure               │
│ Filesystem, CLI, Git, SQLite, agents   │
└─────────────────────────────────────────┘
```

## Layer rules

### Presentation
- **Depends on:** Application, Domain
- **Forbidden imports:** `opsx_tui.infrastructure.*`, `pathlib` (filesystem ops),
  `subprocess`, `os.system`, `logging`
- **Responsibility:** Widgets, screens, key bindings, layout. Reads data
  through application services via ports.

### Application
- **Depends on:** Domain
- **Forbidden imports:** `opsx_tui.infrastructure.*`, `opsx_tui.presentation.*`,
  `pathlib` (filesystem ops), `subprocess`
- **Responsibility:** Use cases, service orchestration, dependency injection

### Domain
- **Depends on:** Nothing outside itself
- **Forbidden imports:** `textual`, `opsx_tui.{application,infrastructure,presentation}`,
  `pathlib.*`, `logging`, `subprocess`
- **Responsibility:** Pydantic models, business rules, port interfaces (Protocols)

### Infrastructure
- **Depends on:** Domain
- **Forbidden imports:** `opsx_tui.{application,presentation}`
- **Responsibility:** Adapters for filesystem, CLI, Git, SQLite, logging,
  agent backends. Implements ports defined in Domain.

## Module map

### Domain (`src/opsx_tui/domain/`)

| Module | Contents |
|---|---|
| `workspace.py` | `ArtifactKind`, `ArtifactInfo`, `CanonicalSpec`, `Change`, `WorkspaceSnapshot` (all `frozen=True`) |
| `open_spec_project.py` | `OpenSpecProject` composite model bundling `Project` + `WorkspaceSnapshot` |
| `project.py` | `Project`, `Diagnostic`, `DiagnosticLevel`, `DiscoverySource` |
| `ports.py` | `ConfigLoader`, `WorkspaceReader`, `ProjectDiscoveryStrategy` Protocols |
| `config.py` | `Config`, `BackendConfig`, `ExecutionConfig`, `UIConfig` |
| `errors.py` | `ConfigLoadError`, `WorkspaceReadError` |
| `logging.py` | `Logger` Protocol |

### Application (`src/opsx_tui/application/`)

| Module | Contents |
|---|---|
| `config_service.py` | `ConfigService` — loads and caches config |
| `project_discovery_service.py` | `ProjectDiscoveryService` — orchestrates discovery strategies |
| `workspace_service.py` | `WorkspaceService` — wraps `WorkspaceReader` port |
| `container.py` | `Container` — dependency injection factory |

### Infrastructure (`src/opsx_tui/infrastructure/`)

| Module | Contents |
|---|---|
| `toml_config_loader.py` | `TomlConfigLoader` — hierarchical TOML config |
| `stdlib_logger.py` | `StdlibLogger` — stdlib logging adapter |
| `discovery/` | `EnvVarDiscoverer`, `AncestorDiscoverer`, `GitRootDiscoverer`, `RecentProjectsDiscoverer` |
| `workspace_reader.py` | `FilesystemWorkspaceReader` — scans filesystem for specs, changes, artifacts |
| `validation.py` | `validate_project()` — shared validation logic |

### Presentation (`src/opsx_tui/presentation/`)

| Module | Contents |
|---|---|
| `app.py` | `OpsxTuiApp`, `WelcomeScreen` |
| `project_screen.py` | `InteractiveProjectScreen` — file picker |

## Key design decisions

| Decision | Rationale |
|---|---|
| Domain never imports Textual | Keeps business logic testable without TUI |
| Presentation never accesses filesystem | Enforced by lint; all I/O goes through infrastructure |
| Infrastructure implements ports from domain | Adapters are swappable; domain stays pure |
| Config loader is a port in domain | Enables unit-testing config logic without files |
| Logger is a port in domain | Enables redaction testing and future structured logging |
| WorkspaceReader is a port in domain | Enables swapping filesystem scan for mock in tests |
| WorkspaceSnapshot is frozen | Immutable snapshot guarantees no accidental mutation after construction |
| OpenSpecProject composite | Bundles Project + WorkspaceSnapshot so app state is always consistent |
| Project discovery uses strategy pattern | Chain of individual strategies, orchestrated by application service |
| Validation lives in infrastructure | Shared utility called by all strategies; pure I/O operation |
| Recent projects stored in JSON sidecar | Avoids SQLite dependency in Fase 0; operational metadata only |
