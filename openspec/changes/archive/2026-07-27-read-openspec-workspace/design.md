## Context

`discover-openspec-project` found the OpenSpec root. Now we must read its contents: specs, changes (active + archived), and their artifacts. The output is a `WorkspaceSnapshot` — an immutable, fingerprinted representation of the entire OpenSpec project. Every downstream widget, service, and watcher reads from this snapshot; none modifies it.

Constraints inherited from the architecture:
- Domain models are `frozen=True`, Pydantic 2, `extra="forbid"`.
- `WorkspaceReader` is a port in `domain/`. `FilesystemWorkspaceReader` is the adapter in `infrastructure/`.
- The reader never modifies files. Detects presence/absence only — no content parsing.
- Must not crash on unknown filenames, malformed structures, or missing config.yaml. Uses diagnostics.

## Goals / Non-Goals

**Goals:**
- Domain models: `CanonicalSpec`, `ArtifactKind`, `ArtifactInfo`, `Change`, `WorkspaceSnapshot`.
- `WorkspaceReader` Protocol + `FilesystemWorkspaceReader` adapter.
- `WorkspaceService` in `application/` wrapping the reader.
- Wire into `Container` and `OpsxTuiApp.on_mount` (run workspace read after discovery).
- Composite `OpenSpecProject` model bundling `Project` + `WorkspaceSnapshot`.
- Fingerprint: SHA256 of sorted `relpath:mtimestamp` pairs for change detection.
- Diagnostic-rich: every missing file, unexpected subdirectory, or empty spec dir is a diagnostic.

**Non-Goals:**
- Content parsing of tasks, specs, proposals, or designs (Change 1.3).
- File watching or change detection (Change 1.4).
- SQLite persistence (later phase).
- Markdown rendering (later phase).

## Decisions

### D1: Shared `Diagnostic` model
**Choice:** Reuse `Diagnostic`/`DiagnosticLevel` from `domain/project.py`. Workspace diagnostics use the same model.
**Why:** One diagnostic type across discovery and workspace keeps the UI rendering consistent. Importing from the same module avoids duplication.
**Alternatives:** Separate `WorkspaceDiagnostic` — rejected as needless duplication.

### D2: `WorkspaceSnapshot` frozen with fingerprint
**Choice:** `WorkspaceSnapshot(BaseModel, frozen=True)` with a `fingerprint: str` field computed by the reader as SHA256 of `"\n".join(sorted(relpath:mtime for each file under openspec/))`.
**Why:** The watcher (Change 1.4) needs a deterministic baseline to detect changes. File mtimes catch modifications without content hashing. `frozen=True` enforces immutability — once constructed, the snapshot is read-only.
**Alternatives:** No fingerprint — rejected because the watcher would need to re-construct the full snapshot and compare object equality (expensive). Content hashes — rejected as more expensive than mtimes for change detection.

### D3: Artifact detection by filename convention
**Choice:** Scan `changes/<name>/` and match known filenames: `proposal.md`, `design.md`, `tasks.md`, `specs/**/*.md`. Unknown files are silently ignored. Missing known files become `ArtifactInfo(exists=False)` with a `WARNING` diagnostic.
**Why:** OpenSpec defines artifact filenames by convention. The scanner must be permissive: a change without `design.md` is still a valid change (early draft state), just with a warning.
**Alternatives:** Require all artifacts — rejected per the construction plan "No fallar por Markdown desconocido" and the gate "tolera cambios incompletos".

### D4: Spec detection by `spec.md` marker
**Choice:** A canonical spec exists at `specs/<name>/spec.md`. Subdirectories without `spec.md` are reported as `WARNING` diagnostics but not included as `CanonicalSpec`.
**Why:** Everything under `specs/` from the same naming pattern. A directory without `spec.md` is either incomplete or not a spec directory.
**Alternatives:** Treat any subdirectory as a spec — rejected because empty dirs or non-spec dirs would pollute the model.

### D5: Composite `OpenSpecProject` model
**Choice:** `OpenSpecProject(BaseModel)` with fields `project: Project` and `workspace: WorkspaceSnapshot`. The app stores this instead of storing `Project` alone.
**Why:** Every screen needs both the project metadata and the workspace content. Storing them separately means passing two objects around. Bundling them eliminates an invariant (valid project + loaded workspace = consistent state).
**Alternatives:** Keep `<code>dict[str, Change]` schema — rejected as fragile. Separate `root` (parent of `openspec/`) from `openspec_root` — correct but better captured in a single bundle. Two separate fields on the app (`self.project` + `self.workspace`) — simpler but `OpenSpecProject` makes the type tighter.

### D6: Reader returns `WorkspaceSnapshot` or raises `WorkspaceReadError`
**Choice:** If the workspace is readable (files exist, traversable), return a `WorkspaceSnapshot` with diagnostics for anomalies. Only raise `WorkspaceReadError` for genuinely unrecoverable states (e.g., permission denied on `openspec/`).
**Why:** An incomplete workspace is still valuable — the UI can show "no specs yet" instead of crashing. The design doc and the gate confirm tolerance.
**Alternatives:** Return `None` for any anomaly — rejected because it discards partial data. Raise on everything — rejected as fragile.

### D7: `config.yaml` presence is a boolean field, not parsed
**Choice:** `WorkspaceSnapshot.config_yaml: bool` indicates whether `openspec/config.yaml` exists. The reader does NOT parse YAML or attempt to validate its contents.
**Why:** Config parsing is a separate concern (already partially handled by project-discovery validation). The workspace reader only catalogs what exists. YAML parsing can be added later if needed; the boolean is sufficient for the "valid OpenSpec project" check.
**Alternatives:** Parse config.yaml and include its data — rejected as scope creep beyond cataloging.

### D8: `WorkspaceService` wraps the reader port
**Choice:** `WorkspaceService(reader: WorkspaceReader)` in `application/`. Provides `read_snapshot(root: Path) -> WorkspaceSnapshot`. The service orchestrates validation and diagnostic aggregation.
**Why:** Follows the established pattern from `ConfigService` and `ProjectDiscoveryService`. Keeps application logic out of infrastructure.
**Alternatives:** Call the reader directly from presentation — rejected as it would bypass the application layer.

## Risks / Trade-offs

- **[Risk] mtime-based fingerprint may miss content-only changes** (e.g., `git checkout` restores same mtime) → Acceptable for v0.1; if false negatives matter, upgrade to content hash in a later change.
- **[Risk] Symlinks under `openspec/`** → The reader uses `Path.iterdir()` with default resolution; symlinked dirs are followed. Diagnostic warning emitted for symlinked files.
- **[Risk] Very large workspaces** (hundreds of specs/changes) → The snapshot builds synchronously on mount. If >100 dirs, defer to background scanning (future change, not in scope yet).
- **[Trade-off] No YAML parsing of `config.yaml`** → Leaves a gap: "valid OpenSpec project" is defined as "has `openspec/config.yaml`" but we don't verify the YAML is well-formed. The discovery validation already checked file existence, not YAML validity. This is acceptable — broken YAML will surface when the config is loaded.