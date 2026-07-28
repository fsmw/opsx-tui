# Tasks: read-openspec-workspace

## 1. Domain models

- [x] 1.1 Create `src/opsx_tui/domain/workspace.py` with `ArtifactKind(StrEnum)`, `ArtifactInfo(BaseModel, frozen=True)`, `CanonicalSpec(BaseModel, frozen=True)`, `Change(BaseModel, frozen=True)`, `WorkspaceSnapshot(BaseModel, frozen=True)`
- [x] 1.2 Add `WorkspaceReadError` to `src/opsx_tui/domain/errors.py`
- [x] 1.3 Add `WorkspaceReader` Protocol to `src/opsx_tui/domain/ports.py` with `read_workspace(openspec_root: Path) -> WorkspaceSnapshot`
- [x] 1.4 Create `src/opsx_tui/domain/open_spec_project.py` with `OpenSpecProject(BaseModel)` composite model bundling `Project` + `WorkspaceSnapshot`
- [x] 1.5 Ensure `diagnostics` are shared type used consistently across discovery and workspace

## 2. FilesystemWorkspaceReader adapter

- [x] 2.1 Create `src/opsx_tui/infrastructure/workspace_reader.py` with `FilesystemWorkspaceReader` implementing `WorkspaceReader`
- [x] 2.2 Implement spec scanning: iterate `openspec_root/specs/`, detect subdirs with `spec.md`, create `CanonicalSpec` instances
- [x] 2.3 Implement active change scanning: iterate `openspec_root/changes/` (skip `archive/`), detect artifacts by filename convention
- [x] 2.4 Implement archived change scanning: iterate `openspec_root/changes/archive/`, same artifact detection
- [x] 2.5 Implement fingerprint computation: collect all regular file paths under `openspec_root`, sort, join `relpath:mtimestamp` with newlines, SHA256 hash
- [x] 2.6 Implement diagnostic collection: WARNING for missing `spec.md`, missing artifacts, empty dirs; silently skip unknown files
- [x] 2.7 Raise `WorkspaceReadError` if `openspec_root` does not exist or is not readable

## 3. Application service

- [x] 3.1 Create `src/opsx_tui/application/workspace_service.py` with `WorkspaceService(reader: WorkspaceReader)` and `read_snapshot(root: Path) -> WorkspaceSnapshot`
- [x] 3.2 Add `create_workspace_service()` and `create_workspace_reader()` to `Container` in `application/container.py`

## 4. Presentation wiring

- [x] 4.1 Update `OpsxTuiApp` to store `OpenSpecProject` instead of `Project`: add `self.opsx_project: OpenSpecProject | None`, remove `self.project`
- [x] 4.2 Update `on_mount` in `presentation/app.py`: after discovery succeeds, call `WorkspaceService.read_snapshot(project.openspec_root)`, handle errors
- [x] 4.3 Update `InteractiveProjectScreen` callback to read workspace after interactive selection succeeds
- [x] 4.4 Update `WelcomeScreen` to show project root and basic workspace stats (spec count, change count)

## 5. Fixtures

- [x] 5.1 Create `tests/fixtures/workspace/` with a minimal valid OpenSpec project (config.yaml, one spec, one active change, one archived change)
- [x] 5.2 Create a fixture with missing artifacts (no design.md, empty specs dir) for diagnostics testing
- [x] 5.3 Create a fixture with an empty workspace (config.yaml only, no specs or changes)

## 6. Tests

- [x] 6.1 Write unit tests for domain models in `tests/unit/domain/test_workspace_models.py`
- [x] 6.2 Write contract test for `WorkspaceReader` against `FilesystemWorkspaceReader` in `tests/contract/test_workspace_reader_contract.py`
- [x] 6.3 Write integration test for `FilesystemWorkspaceReader` scan logic in `tests/integration/test_workspace_reader.py`
- [x] 6.4 Write test for fingerprint determinism (same dir → same hash, changed mtime → different hash)
- [x] 6.5 Write test for incomplete workspace (missing artifacts → WARNING diagnostics, snapshot still valid)
- [x] 6.6 Write test for empty workspace (no specs/changes → empty tuples, no ERROR)
- [x] 6.7 Write test for unknown files (ignored silently, no diagnostics)
- [x] 6.8 Write test for `WorkspaceReadError` (non-existent path, permission denied)
- [x] 6.9 Write test for `WorkspaceService` in `tests/unit/application/test_workspace_service.py`
- [x] 6.10 Write TUI test for app mount sequence (discovery → workspace → welcome screen)

## 7. Documentation

- [x] 7.1 Update `docs/architecture.md` with workspace module paths and the `OpenSpecProject` composite model
- [x] 7.2 Update `AGENTS.md` if any new patterns or conventions emerged
