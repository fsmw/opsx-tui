from __future__ import annotations

from pydantic import BaseModel

from opsx_tui.domain.project import Project
from opsx_tui.domain.workspace import WorkspaceSnapshot


class OpenSpecProject(BaseModel):
    project: Project
    workspace: WorkspaceSnapshot
