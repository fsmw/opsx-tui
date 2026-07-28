## 1. Domain models

- [x] 1.1 Add `DiscoverySource(StrEnum)` to `src/opsx_tui/domain/project.py`
- [x] 1.2 Add `DiagnosticLevel(StrEnum)` to `project.py`
- [x] 1.3 Add `Diagnostic(BaseModel)` to `project.py`
- [x] 1.4 Add `Project(BaseModel)` to `project.py` with `is_valid` as a field (not computed property — domain cannot do I/O; set by infrastructure validation)
- [x] 1.5 Add `ProjectDiscoveryStrategy(Protocol)` to `project.py`

## 2. Infrastructure strategies

- [x] 2.1 Add `EnvVarDiscoverer` in `infrastructure/env_var_discoverer.py`
- [x] 2.2 Add `AncestorDiscoverer` in `infrastructure/ancestor_discoverer.py`
- [x] 2.3 Add `GitRootDiscoverer` in `infrastructure/git_root_discoverer.py`
- [x] 2.4 Add `RecentProjectsDiscoverer` in `infrastructure/recent_projects_discoverer.py`
- [x] 2.5 Add `write_recent_project` to `recent_projects_discoverer.py`

## 3. Presentation

- [x] 3.1 Add `CliArgDiscoverer` in `presentation/cli_arg_discoverer.py`
- [x] 3.2 Add `InteractiveProjectScreen(Screen)` in `presentation/project_screen.py`
- [x] 3.3 Wire discovery into `OpsxTuiApp.on_mount`
- [x] 3.4 Register `InteractiveProjectScreen` (used directly, not via SCREENS string key)

## 4. Application service

- [x] 4.1 Add `ProjectDiscoveryService` in `application/project_discovery_service.py`
- [x] 4.2 Wire `ProjectDiscoveryService` into `Container`

## 5. Entry point

- [x] 5.1 Add argparse `--project` and `--help` to `__main__.py`
- [x] 5.2 Pass parsed `project` arg to `OpsxTuiApp`

## 6. Shared validation logic

- [x] 6.1 Extract `validate_project(path, source) -> Project | None` in `infrastructure/validation.py`

## 7. Tests

- [x] 7.1 Unit tests for domain models (test_project_models.py)
- [x] 7.2 Unit tests for `EnvVarDiscoverer` (test_env_var_discoverer.py)
- [x] 7.3 Unit tests for `AncestorDiscoverer` (test_ancestor_discoverer.py)
- [x] 7.4 Unit tests for `GitRootDiscoverer` (test_git_root_discoverer.py)
- [x] 7.5 Unit tests for `RecentProjectsDiscoverer` (test_recent_projects_discoverer.py)
- [x] 7.6 Unit tests for `ProjectDiscoveryService` (test_project_discovery_service.py)
- [x] 7.7 TUI tests for app shell already pass (existing test_app_shell.py)
- [x] 7.8 Integration tests via tmp_path fixtures cover the full chain

## 8. Fixtures

- [x] 8.1 Add `tests/fixtures/projects/valid-project/openspec/config.yaml` with empty `specs/` and `changes/`
- [x] 8.2 Add `tests/fixtures/projects/incomplete-project/openspec/` without `config.yaml`

## 9. Docs

- [x] 9.1 Update `docs/architecture.md` with project discovery layer