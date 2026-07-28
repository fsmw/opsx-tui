from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel

from opsx_tui.domain.change_parser import (
    ChangeState,
    ParsedDesign,
    ParsedProposal,
    ParsedTaskList,
)
from opsx_tui.domain.metadata import ChangeMetadata
from opsx_tui.domain.project import Diagnostic
from opsx_tui.domain.spec_parser import ParsedSpec


class ArtifactKind(StrEnum):
    PROPOSAL = "proposal"
    DESIGN = "design"
    TASKS = "tasks"
    SPECS = "specs"


class ArtifactInfo(BaseModel, frozen=True):
    kind: ArtifactKind
    path: Path
    absolute_path: Path
    exists: bool


class CanonicalSpec(BaseModel, frozen=True):
    name: str
    spec_dir: Path
    spec_file: Path | None
    absolute_spec_dir: Path
    absolute_spec_file: Path | None
    raw_markdown: str | None = None
    parsed: ParsedSpec | None = None


class Change(BaseModel, frozen=True):
    name: str
    change_dir: Path
    absolute_change_dir: Path
    artifacts: tuple[ArtifactInfo, ...]
    is_archived: bool
    delta_specs: tuple[CanonicalSpec, ...] = ()
    state: ChangeState = ChangeState.UNKNOWN
    parsed_proposal: ParsedProposal | None = None
    parsed_design: ParsedDesign | None = None
    parsed_tasks: ParsedTaskList | None = None
    metadata: ChangeMetadata | None = None
    artifact_diagnostics: tuple[Diagnostic, ...] = ()


class WorkspaceSnapshot(BaseModel, frozen=True):
    root: Path
    openspec_root: Path
    config_yaml: bool
    specs: tuple[CanonicalSpec, ...]
    active_changes: tuple[Change, ...]
    archived_changes: tuple[Change, ...]
    diagnostics: tuple[Diagnostic, ...]
    fingerprint: str
