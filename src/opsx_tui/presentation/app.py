from __future__ import annotations

import asyncio
from pathlib import Path
from textual.app import App
from textual.binding import Binding

from opsx_tui.application.container import Container
from opsx_tui.application.workspace_watcher_service import WorkspaceWatcherService
from opsx_tui.domain.open_spec_project import OpenSpecProject
from opsx_tui.domain.openspec_cli import OpenSpecCLIInfo
from opsx_tui.domain.project import DiscoverySource, Project
from opsx_tui.domain.workspace import WorkspaceSnapshot
from opsx_tui.infrastructure.recent_projects_discoverer import write_recent_project
from opsx_tui.infrastructure.validation import validate_project
from opsx_tui.presentation.shell_screen import ShellScreen


class OpsxTuiApp(App):
    BINDINGS = [
        Binding("q", "exit", "Quit", priority=True),
        Binding("ctrl+c", "exit", "Quit", priority=True),
    ]

    def __init__(
        self,
        container: Container | None = None,
        project_arg: Path | None = None,
    ) -> None:
        super().__init__()
        self._container = container
        self._project_arg = project_arg
        self.opsx_project: OpenSpecProject | None = None
        self.cli_info: OpenSpecCLIInfo | None = None
        self._watcher: WorkspaceWatcherService | None = None

    def on_mount(self) -> None:
        self._container = self._container or Container()
        container = self._container
        project: Project | None = None

        if self._project_arg is not None:
            project = validate_project(self._project_arg, DiscoverySource.CLI_ARG)

        if project is None or not project.is_valid:
            service = container.create_project_discovery_service()
            discovered = service.discover()
            if discovered is not None and discovered.is_valid:
                project = discovered
            else:
                self.notify(
                    "No valid OpenSpec project found",
                    severity="error",
                    timeout=5,
                )
                self.exit()
                return

        write_recent_project(project.root)
        self._load_workspace(container, project)
        asyncio.create_task(self._run_cli_detection(container))

    def _load_workspace(self, container: Container, project: Project) -> None:
        try:
            ws_service = container.create_workspace_service()
            snapshot = ws_service.read_snapshot(project.openspec_root)
            store = container.create_metadata_store(project.openspec_root)
            snapshot = container.enrich_snapshot(snapshot, store)
        except Exception:
            self.notify(
                "Failed to read workspace",
                severity="error",
                timeout=5,
            )
            self.exit()
            return
        self.opsx_project = OpenSpecProject(project=project, workspace=snapshot)
        self._metadata_store = store
        watcher = container.create_workspace_watcher_service(ws_service)
        watcher.start(project.openspec_root, self._on_workspace_change)
        self._watcher = watcher
        self.push_screen(ShellScreen(self.opsx_project))

    async def _run_cli_detection(self, container: Container) -> None:
        self.cli_info = await container.run_cli_detection()

    def _on_workspace_change(self, snapshot: WorkspaceSnapshot) -> None:
        if self.opsx_project is not None:
            store = getattr(self, "_metadata_store", None)
            if store is not None and self._container is not None:
                snapshot = self._container.enrich_snapshot(snapshot, store)
            self.opsx_project = OpenSpecProject(
                project=self.opsx_project.project,
                workspace=snapshot,
            )
            if self._container is not None:
                asyncio.create_task(self._run_cli_detection(self._container))
        self.refresh()

    async def on_unmount(self) -> None:
        if self._watcher is not None:
            watcher = self._watcher
            self._watcher = None
            await watcher.stop()
