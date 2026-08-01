from __future__ import annotations

from opsx_tui.domain.lifecycle import (
    LifecycleAssessment,
    LifecycleInput,
    RequiredArtifact,
    assess_lifecycle,
)
from opsx_tui.domain.logging import Logger
from opsx_tui.domain.workspace import Change

_SPEC_DRIVEN_ARTIFACTS: tuple[RequiredArtifact, ...] = (
    RequiredArtifact(name="proposal", required=True),
    RequiredArtifact(name="design", required=True),
    RequiredArtifact(name="tasks", required=True),
    RequiredArtifact(name="specs", required=False),
)


class LifecycleService:
    def __init__(self, logger: Logger | None = None) -> None:
        self._logger = logger

    def assess(self, change: Change) -> LifecycleAssessment:
        input_data = self._build_input(change)
        result = assess_lifecycle(input_data)
        if self._logger is not None:
            reasons_summary = "; ".join(result.reasons[:3])
            self._logger.info(
                f"Lifecycle: {change.name} -> {result.status.value}"
                f" ({reasons_summary})"
            )
        return result

    def assess_all(
        self, changes: tuple[Change, ...]
    ) -> dict[str, LifecycleAssessment]:
        return {c.name: self.assess(c) for c in changes}

    @staticmethod
    def _build_input(change: Change) -> LifecycleInput:
        return LifecycleInput(
            change=change,
            required_artifacts=_SPEC_DRIVEN_ARTIFACTS,
        )
