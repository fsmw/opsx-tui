from __future__ import annotations

from pathlib import Path

from opsx_tui.application.change_metadata_service import merge_metadata
from opsx_tui.application.change_parser_service import ChangeParserService
from opsx_tui.application.config_service import ConfigService
from opsx_tui.application.lifecycle_service import LifecycleService
from opsx_tui.application.project_discovery_service import ProjectDiscoveryService
from opsx_tui.application.spec_parser_service import SpecParserService
from opsx_tui.application.workspace_service import WorkspaceService
from opsx_tui.application.workspace_watcher_service import WorkspaceWatcherService
from opsx_tui.domain.logging import Logger
from opsx_tui.domain.openspec_cli import OpenSpecCLIInfo
from opsx_tui.domain.ports import (
    ConfigLoader,
    MetadataStore,
    OpenSpecCLIDetector,
    WorkspaceReader,
)
from opsx_tui.domain.workspace import WorkspaceSnapshot
from opsx_tui.infrastructure.ancestor_discoverer import AncestorDiscoverer
from opsx_tui.infrastructure.cli_detector import ProcessOpenSpecCLIDetector
from opsx_tui.infrastructure.env_var_discoverer import EnvVarDiscoverer
from opsx_tui.infrastructure.git_root_discoverer import GitRootDiscoverer
from opsx_tui.infrastructure.metadata_store import TomlMetadataStore, _project_key
from opsx_tui.infrastructure.recent_projects_discoverer import RecentProjectsDiscoverer
from opsx_tui.infrastructure.stdlib_logger import StdlibLogger
from opsx_tui.infrastructure.toml_config_loader import TomlConfigLoader
from opsx_tui.infrastructure.watchfiles_observer import WatchfilesObserver
from opsx_tui.infrastructure.workspace_reader import FilesystemWorkspaceReader


class Container:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root

    def create_config_loader(self) -> ConfigLoader:
        return TomlConfigLoader(project_root=self._project_root)

    def create_logger(self, name: str = "opsx_tui") -> Logger:
        return StdlibLogger(name=name)

    def create_config_service(self) -> ConfigService:
        return ConfigService(
            loader=self.create_config_loader(),
            logger=self.create_logger(),
        )

    def create_project_discovery_service(self) -> ProjectDiscoveryService:
        return ProjectDiscoveryService([
            EnvVarDiscoverer(),
            AncestorDiscoverer(),
            GitRootDiscoverer(),
            RecentProjectsDiscoverer(),
        ])

    def create_spec_parser_service(self) -> SpecParserService:
        return SpecParserService(logger=self.create_logger())

    def create_workspace_reader(self) -> WorkspaceReader:
        return FilesystemWorkspaceReader(
            lifecycle_service=self.create_lifecycle_service(),
        )

    def create_change_parser_service(self) -> ChangeParserService:
        return ChangeParserService()

    def create_lifecycle_service(self) -> LifecycleService:
        return LifecycleService(logger=self.create_logger())

    def create_workspace_service(self) -> WorkspaceService:
        return WorkspaceService(reader=self.create_workspace_reader())

    def create_metadata_store(self, openspec_root: Path) -> MetadataStore:
        return TomlMetadataStore(project_key=_project_key(openspec_root))

    def enrich_snapshot(
        self, snapshot: WorkspaceSnapshot, store: MetadataStore
    ) -> WorkspaceSnapshot:
        metadata_map = store.load_all()
        return merge_metadata(snapshot, metadata_map)

    def create_cli_detector(self) -> OpenSpecCLIDetector:
        return ProcessOpenSpecCLIDetector()

    async def run_cli_detection(self) -> OpenSpecCLIInfo:
        detector = self.create_cli_detector()
        return await detector.detect()

    def create_workspace_watcher_service(
        self, workspace_service: WorkspaceService
    ) -> WorkspaceWatcherService:
        return WorkspaceWatcherService(
            observer=WatchfilesObserver(logger=self.create_logger()),
            logger=self.create_logger(),
            workspace_service=workspace_service,
        )
