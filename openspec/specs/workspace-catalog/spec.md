## ADDED Requirements

### Requirement: WorkspaceSnapshot domain model
The system SHALL define a `WorkspaceSnapshot` Pydantic model with `frozen=True`. It SHALL contain:
- `root: Path` — project root (parent of `openspec/`)
- `openspec_root: Path`
- `config_yaml: bool` — whether `openspec/config.yaml` exists
- `specs: tuple[CanonicalSpec, ...]`
- `active_changes: tuple[Change, ...]`
- `archived_changes: tuple[Change, ...]`
- `diagnostics: tuple[Diagnostic, ...]`
- `fingerprint: str` — SHA256 of sorted `relpath:mtimestamp` pairs

#### Scenario: Snapshot is frozen
- **WHEN** a `WorkspaceSnapshot` is instantiated
- **THEN** attempting to set any field after creation raises `ValidationError`

#### Scenario: Snapshot with diagnostics
- **WHEN** the workspace has missing artifacts
- **THEN** the snapshot includes `WARNING` diagnostics and all other fields are populated

### Requirement: CanonicalSpec model
The system SHALL define a `CanonicalSpec` Pydantic model with fields:
- `name: str` — directory name (e.g., `"project-foundation"`)
- `spec_dir: Path` — relative to `openspec_root`
- `spec_file: Path | None` — `spec.md` path relative to `openspec_root`, or `None` if missing
- `absolute_spec_dir: Path`
- `absolute_spec_file: Path | None`

#### Scenario: Spec with file
- **WHEN** `specs/project-foundation/spec.md` exists
- **THEN** `CanonicalSpec(name="project-foundation", spec_file=Path("specs/project-foundation/spec.md"))` is created

#### Scenario: Spec directory without spec.md
- **WHEN** a subdirectory under `specs/` has no `spec.md`
- **THEN** a `WARNING` diagnostic is added and no `CanonicalSpec` is emitted for that directory

### Requirement: Artifact models
The system SHALL define:
- `ArtifactKind(StrEnum)` with values `PROPOSAL`, `DESIGN`, `TASKS`, `SPECS`.
- `ArtifactInfo(BaseModel, frozen=True)` with fields `kind: ArtifactKind`, `path: Path` (relative to openspec_root), `absolute_path: Path`, `exists: bool`.

#### Scenario: ArtifactInfo for present file
- **WHEN** `changes/my-change/proposal.md` exists
- **THEN** `ArtifactInfo(kind=ArtifactKind.PROPOSAL, exists=True)` is created

#### Scenario: ArtifactInfo for missing file
- **WHEN** `changes/my-change/design.md` does not exist
- **THEN** `ArtifactInfo(kind=ArtifactKind.DESIGN, exists=False)` is created without error

### Requirement: Change model
The system SHALL define a `Change` Pydantic model with fields:
- `name: str`
- `change_dir: Path` — relative to `openspec_root`
- `absolute_change_dir: Path`
- `artifacts: tuple[ArtifactInfo, ...]`
- `is_archived: bool`

#### Scenario: Active change scanned
- **WHEN** `changes/my-change/` is scanned
- **THEN** a `Change` is created with `is_archived=False` and all detected artifacts

#### Scenario: Archived change scanned
- **WHEN** `changes/archive/2026-07-27-my-change/` is scanned
- **THEN** a `Change` is created with `is_archived=True`

### Requirement: WorkspaceReader port
The system SHALL define a `WorkspaceReader` Protocol in `domain/` with a single method `read_workspace(openspec_root: Path) -> WorkspaceSnapshot`.

#### Scenario: Reader returns a snapshot
- **WHEN** `read_workspace` is called with a valid path
- **THEN** a `WorkspaceSnapshot` is returned

### Requirement: FilesystemWorkspaceReader adapter
The system SHALL implement `WorkspaceReader` as `FilesystemWorkspaceReader` in `infrastructure/`. It SHALL:
1. Verify `openspec_root` exists and is a directory. If not, raise `WorkspaceReadError`.
2. Scan `openspec_root / "specs"` for subdirectories with `spec.md`.
3. Scan `openspec_root / "changes"` for change directories.
4. Scan `openspec_root / "changes" / "archive"` for archived changes.
5. For each change directory, detect artifacts by known filenames.
6. Compute fingerprint. Collect diagnostics throughout.

#### Scenario: Full workspace scan
- **WHEN** a well-formed OpenSpec project is scanned
- **THEN** all specs, active changes, and archived changes are enumerated with their artifacts

#### Scenario: Empty workspace
- **WHEN** `openspec/` has no `specs/` or `changes/` subdirectories
- **THEN** `specs` and `changes` are empty tuples; diagnostics exist indicating empty workspace

#### Scenario: Permission denied
- **WHEN** `openspec_root` exists but is not readable
- **THEN** `WorkspaceReadError` is raised

### Requirement: Fingerprint computation
The fingerprint SHALL be computed as `sha256("\n".join(sorted(relpath:mtimestamp for files under openspec_root)))`. Only regular files SHALL be included (not directories, not symlinks). The fingerprint SHALL be deterministic (same filesystem state → same fingerprint).

#### Scenario: Deterministic fingerprint
- **WHEN** the same workspace is scanned twice without changes
- **THEN** both fingerprints are identical

#### Scenario: File modification changes fingerprint
- **WHEN** a file under `openspec/` is modified (mtime changes)
- **THEN** the new fingerprint differs from the previous one

### Requirement: Unknown files are ignored
The reader SHALL silently skip files that do not match known artifact filenames (`proposal.md`, `design.md`, `tasks.md`, `spec.md`) or are not in recognized directories. Unknown files SHALL NOT produce diagnostics.

#### Scenario: Unknown file skipped
- **WHEN** `changes/my-change/notes.txt` exists
- **THEN** no diagnostic is emitted and no `ArtifactInfo` is created for `notes.txt`

### Requirement: WorkspaceService in application
The system SHALL define `WorkspaceService` in `application/` with method `read_snapshot(root: Path) -> WorkspaceSnapshot`. The service SHALL accept a `WorkspaceReader` via constructor injection.

#### Scenario: Service delegates to reader
- **WHEN** `read_snapshot(root)` is called
- **THEN** it returns the result of `reader.read_workspace(root)`

### Requirement: OpenSpecProject composite model
The system SHALL define `OpenSpecProject(BaseModel)` with fields `project: Project` and `workspace: WorkspaceSnapshot`. The app SHALL store this as `self.opsx_project` instead of `self.project`.

#### Scenario: Composite after discovery + workspace read
- **WHEN** discovery returns a valid `Project` and workspace read returns a `WorkspaceSnapshot`
- **THEN** an `OpenSpecProject` bundles both

### Requirement: App mount sequence updated
On mount, after project discovery succeeds, the app SHALL read the workspace via `WorkspaceService.read_snapshot(project.openspec_root)`. If the workspace read fails, the app SHALL display an error screen. If a valid `OpenSpecProject` is produced, the app pushes the welcome screen.

#### Scenario: Full mount sequence succeeds
- **WHEN** discovery and workspace read both succeed
- **THEN** `self.opsx_project` is set and the welcome screen is shown

#### Scenario: Workspace read error handled
- **WHEN** discovery succeeds but workspace read raises `WorkspaceReadError`
- **THEN** the app displays an error notification and does not crash