## Why

The current `infer_change_state()` function produces only 5 coarse states (UNKNOWN, INCOMPLETE, PARTIALLY_VALID, ACTIVE, ARCHIVED) derived solely from artifact presence and diagnostic severity. It cannot express task progress, verification status, operational blocks, or methodological position — making it useless for a Kanban board. The lifecycle rules document (`docs/05-change-lifecycle-rules.md`) defines a complete 9-state model with strict precedence, explainable reasons, block handling, and verification awareness. This change implements that model as a pure domain inference engine.

## What Changes

- **BREAKING**: Replace `ChangeState` enum (5 states) with `ChangeStatus` enum (9 states: draft, planning, ready, applying, verification, ready-to-archive, blocked, archived, unknown)
- **BREAKING**: Replace `infer_change_state()` with `assess_lifecycle(LifecycleInput) -> LifecycleAssessment`
- Add `LifecycleInput` frozen model (change, required artifacts, verification, metadata, diagnostics, fingerprints — future fields optional)
- Add `LifecycleAssessment` frozen model (status, reasons, warnings, available actions, underlying status, blocking conditions)
- Add `BlockingCondition` frozen model (code, message, severity, recoverable, suggested actions)
- Add `RequiredArtifact` model for workflow-driven artifact expectations
- Add `LifecycleService` in application layer that wires inputs and calls assessment
- Remove old `ChangeState` usage from `Change` model, workspace reader, and container

## Capabilities

### New Capabilities
- `change-lifecycle`: Deterministic lifecycle inference from evidence — 9 states, precedence rules, block detection, available actions per state, explainable reasons/warnings, verification staleness

### Modified Capabilities
- `change-parsing`: Replace `ChangeState` enum and `infer_change_state()` function with `ChangeStatus` and `assess_lifecycle()`

## Impact

- `domain/change_parser.py` — remove old `ChangeState`, `infer_change_state()`
- `domain/lifecycle.py` — new file with `ChangeStatus`, `LifecycleInput`, `LifecycleAssessment`, `BlockingCondition`, `RequiredArtifact`, `assess_lifecycle()`
- `domain/workspace.py` — `Change.state` type changes to `ChangeStatus`
- `application/lifecycle_service.py` — new service wrapping assessment
- `application/container.py` — wire lifecycle service
- `infrastructure/workspace_reader.py` — call lifecycle service instead of `infer_change_state()`
- `presentation/views/changes_view.py` — state badges map to new 9 states
- `presentation/views/change_detail_panel.py` — Overview tab shows lifecycle reasons
- Tests: all references to old `ChangeState` need update
