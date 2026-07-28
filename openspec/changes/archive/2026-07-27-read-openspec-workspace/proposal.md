## Why

The project can now discover an OpenSpec root (`discover-openspec-project`). Without the next step — reading the workspace — there is nothing to show in the TUI. Every subsequent change (task parsing, Kanban, command palette, detail screens) depends on having a structured, immutable representation of the OpenSpec project's content: its specs, changes, artifacts, and their relationships. This change builds that representation: a `WorkspaceSnapshot` that is the single source of truth for the entire application layer.

## What Changes

- Add domain models: `WorkspaceSnapshot`, `CanonicalSpec`, `Change`, `ArtifactKind`, `ArtifactInfo` (reusing `Diagnostic` from the discovery module).
- Add `WorkspaceReader` Protocol in `domain/ports.py` and a `FilesystemWorkspaceReader` adapter in `infrastructure/` that traverses `openspec/` directories and builds the snapshot.
- The reader scans: `openspec/config.yaml`, `openspec/specs/` (each subdirectory with a `spec.md`), `openspec/changes/` (active changes with their artifacts), `openspec/changes/archive/` (archived changes).
- Each change's artifacts are detected by filename (`proposal.md`, `design.md`, `tasks.md`, `specs/**/*.md`). Missing artifacts are captured as `WARNING` diagnostics — the workspace is still valid.
- The snapshot is `frozen=True` and includes a `fingerprint: str` (SHA256 of sorted file paths + mtimes) for change detection.
- Add a `WorkspaceService` in `application/` that wraps the reader and provides `read_snapshot(openspec_root) -> WorkspaceSnapshot`.
- Wire the service into `Container` alongside the existing project discovery.
- Add a composite model `OpenSpecProject` that bundles `Project` (from discovery) with `WorkspaceSnapshot` (from reading). The app's `mount` sequence becomes: discover project → read workspace → show main screen.
- Does NOT parse task contents (deferred to Change 1.3). Only detects that `tasks.md` exists and counts tasks.

## Capabilities

### New Capabilities
- `workspace-catalog`: Models, reader, and service for enumerating specs, changes, and artifacts from an OpenSpec filesystem.

### Modified Capabilities
- `project-foundation`: `Container` gets `create_workspace_service()`. `OpsxTuiApp` runs workspace read after discovery. `docs/architecture.md` updated with new module paths.

## Impact

- Existing discovery module untouched (except container wiring).
- New domain models are in `domain/workspace.py` — reusable by all future changes.
- Architecture doc amendment: add workspace layer to the module map.
- No new external dependencies (stdlib `pathlib`, `os`, `hashlib`).
- No change to the existing `config`, `logging`, or `errors` modules.