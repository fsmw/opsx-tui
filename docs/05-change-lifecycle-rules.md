# Lifecycle and Kanban Rules — OPSX TUI

## 1. Purpose

This document defines the functional rules used by **OPSX TUI** to infer, explain, and represent OpenSpec change states on a Kanban board.

Its goal is to ensure that:

- the state of a change is deterministic;
- the board represents real evidence;
- the interface does not create a parallel system to OpenSpec;
- the rules are consistent across domain, UI, tests, and persistence;
- operational blocks do not hide the methodological state;
- verifications lose validity when their inputs change;
- every state can be explained to the user.

This document is normative for:

- `LifecycleService`;
- `LifecycleAssessment`;
- `VerificationRecord`;
- Kanban board;
- change cards;
- filters;
- contextual actions;
- inference tests;
- post-execution validation.

---

# 2. Fundamental principles

## 2.1 State is derived

State must not be manually assigned as the source of truth.

It must be derived from:

- change location;
- artifacts present;
- required artifacts;
- tasks;
- progress;
- validation results;
- verifications;
- fingerprints;
- diagnostics;
- operational blocks;
- available capabilities.

## 2.2 State must be explainable

Every assessment must include:

- state;
- reasons;
- warnings;
- blocks;
- available actions;
- evidence used;
- underlying state when a block exists.

Example:

```text
State: applying

Reasons:
- proposal.md available.
- design.md available.
- delta specs available.
- tasks.md contains 11 tasks.
- 7 tasks are completed.
- 4 tasks are pending.
```

## 2.3 The Kanban is a projection

Columns represent a visual projection of the lifecycle.

They do not represent:

- a rigid state machine;
- a mandatory workflow;
- a ticket system;
- an OpenSpec replacement;
- manually stored state.

## 2.4 Changes may be incomplete

An incomplete change remains visible.

The app must display:

- what exists;
- what is missing;
- what could not be interpreted;
- possible actions.

## 2.5 Operational states may wrap methodological states

A change may be methodologically in `applying`, but operationally blocked.

Representation:

```text
status: blocked
underlying_status: applying
```

## 2.6 Rules must be deterministic

For the same set of inputs, the result must be identical.

States based on the following are not accepted:

- unstable file order;
- free-form agent messages;
- current time without explicit rule;
- non-persisted content;
- visual user selection.

---

# 3. Defined states

The initial states are:

```text
draft
planning
ready
applying
verification
ready-to-archive
blocked
archived
unknown
```

---

# 4. Precedence

The general precedence is:

```text
archived
blocked
ready-to-archive
verification
applying
ready
planning
draft
unknown
```

This precedence does not mean mandatory transition. It only defines which state dominates when multiple conditions are true.

## 4.1 Archived

Has the highest precedence because it is derived from the change's actual location.

## 4.2 Blocked

Has precedence over active states, but preserves `underlying_status`.

## 4.3 Ready to archive

Has precedence over verification when a current and successful verification exists.

## 4.4 Unknown

Only used when there is insufficient evidence to safely apply another rule.

---

# 5. Lifecycle inputs

The assessment must receive a structure equivalent to:

```python
class LifecycleInput(BaseModel):
    change: Change
    required_artifacts: tuple[RequiredArtifact, ...]
    verification: VerificationRecord | None
    local_metadata: LocalChangeMetadata | None
    diagnostics: tuple[WorkspaceDiagnostic, ...]
    openspec_state: OpenSpecReportedState | None
    backend_availability: tuple[BackendAvailability, ...]
    git_state: GitWorkspaceState | None
    current_fingerprint: str
```

Not all inputs are required for all states.

---

# 6. Relevant artifacts

## 6.1 Primary artifacts

Initially considered:

- `proposal.md`;
- `design.md`;
- `tasks.md`;
- delta specs;
- change configuration when present;
- additional artifacts declared by the workflow.

## 6.2 Required artifacts

Required artifacts must not be hardcoded exclusively in the UI.

They are determined by:

1. OpenSpec capabilities;
2. configured workflow;
3. schema or profile;
4. OPSX TUI compatible fallback.

## 6.3 Optional artifacts

An absent optional artifact does not prevent `ready`.

## 6.4 Invalid artifacts

An existing but unreadable or critically invalid artifact is considered unusable.

Example:

```text
proposal.md exists
but cannot be read
→ proposal not available for lifecycle
```

It must be preserved as an artifact with a diagnostic.

---

# 7. Draft state

## 7.1 Definition

The change exists, but does not yet have a usable proposal or sufficient planning evidence.

## 7.2 Typical conditions

`draft` is assigned when:

- the change is active;
- it is not blocked;
- `proposal.md` does not exist; or
- `proposal.md` exists, but is not usable; or
- the change folder exists, but there are insufficient methodological artifacts.

## 7.3 Evidence

Examples:

```text
- Change folder detected.
- proposal.md absent.
```

or:

```text
- proposal.md exists.
- The file cannot be interpreted.
- No other valid planning artifacts exist.
```

## 7.4 Suggested actions

- explore;
- propose;
- new-change;
- open-editor;
- diagnose.

## 7.5 Edge cases

### Empty folder

```text
status = draft
```

### Only tasks.md

```text
status = draft
warning = tasks exist without proposal
```

### Only delta specs

```text
status = draft
warning = delta specs without proposal
```

---

# 8. Planning state

## 8.1 Definition

A usable proposal exists, but one or more required artifacts to begin implementation are missing.

## 8.2 Conditions

`planning` is assigned when:

- the change is active;
- usable proposal;
- no dominant block;
- at least one required artifact is absent or invalid;
- insufficient implementation evidence exists yet.

## 8.3 Evidence

Example:

```text
- proposal.md available.
- design.md available.
- tasks.md absent.
- Required delta spec absent.
```

## 8.4 Suggested actions

- continue;
- fast-forward;
- open-editor;
- validate;
- diagnose.

## 8.5 Partial tasks rule

If `tasks.md` exists with completed tasks, but required artifacts are still missing:

```text
status = planning
warning = implementation evidence exists before planning artifacts are complete
```

The rule may escalate to `blocked` if the policy requires it.

---

# 9. Ready state

## 9.1 Definition

The change has all required artifacts and is ready to begin implementation.

## 9.2 Conditions

`ready` is assigned when:

- active change;
- required artifacts available;
- no critical diagnostics;
- no block exists;
- usable `tasks.md` exists;
- total tasks is greater than zero;
- no tasks are completed;
- no prior implementation evidence.

## 9.3 Evidence

```text
- proposal.md available.
- design.md available.
- Delta specs available.
- tasks.md contains 12 tasks.
- 0 tasks completed.
```

## 9.4 Suggested actions

- apply;
- verify-planning;
- open-editor;
- inspect-git;
- create-checkpoint.

## 9.5 Zero tasks

If all artifacts exist, but `tasks.md` contains no tasks:

```text
status = planning
warning = tasks document has no actionable tasks
```

It is not considered `ready`.

---

# 10. Applying state

## 10.1 Definition

There is evidence of ongoing implementation and pending tasks remain.

## 10.2 Main conditions

`applying` is assigned when:

- active change;
- required artifacts are available or sufficiently usable;
- at least one task is completed;
- at least one task is pending;
- no dominant block exists;
- not archived.

## 10.3 Evidence

```text
- 7 of 11 tasks completed.
- 4 tasks pending.
```

## 10.4 Optional additional evidence

May be reinforced by:

- recent apply execution;
- modified code files;
- Git diff;
- task events;
- active execution.

## 10.5 Suggested actions

- apply;
- continue;
- inspect-run;
- verify-partial;
- open-editor;
- view-diff;
- cancel-active-execution.

## 10.6 Active execution

When an active `apply` execution exists:

```text
status = applying
runtime_indicator = running
```

A separate Kanban state called `running` is not created.

---

# 11. Verification state

## 11.1 Definition

The declared implementation is complete, but current verification does not exist or is not satisfactory.

## 11.2 Conditions

`verification` is assigned when:

- active change;
- all tasks are completed;
- no pending tasks;
- no verification exists; or
- verification failed; or
- verification was interrupted; or
- verification is stale; or
- verification only partially covers current inputs.

## 11.3 Evidence

```text
- 11 of 11 tasks completed.
- No current verification exists.
```

or:

```text
- All tasks completed.
- Last verification failed.
- 2 critical findings.
```

## 11.4 Suggested actions

- verify;
- inspect-findings;
- reopen-tasks;
- view-diff;
- run-tests;
- diagnose.

## 11.5 Completed tasks with no tasks

An empty `tasks.md` does not equal 100%.

It must remain in `planning`.

---

# 12. Ready to archive state

## 12.1 Definition

The change is implemented and has a current and satisfactory verification.

## 12.2 Conditions

`ready-to-archive` is assigned when:

- active change;
- all tasks completed;
- `VerificationRecord` exists;
- verification state is `passed` or `passed-with-warnings` (allowed);
- verified fingerprint matches current fingerprint;
- no blocks exist;
- no critical findings;
- required artifacts remain available.

## 12.3 Evidence

```text
- 14 of 14 tasks completed.
- Successful verification.
- Fingerprint unchanged since verification.
- No critical findings.
```

## 12.4 Suggested actions

- archive;
- inspect-verification;
- view-diff;
- create-checkpoint;
- export-report.

## 12.5 Passed with warnings

The initial policy will be:

```text
passed-with-warnings
→ allows ready-to-archive
only if there are no blocking warnings
```

Blocking warnings are defined by severity and policy.

---

# 13. Blocked state

## 13.1 Definition

A condition exists that prevents executing the expected action or advancing safely.

## 13.2 Blocking sources

### Manual/local

- user-declared reason;
- pending decision;
- external dependency;
- waiting for credentials;
- waiting for approval.

### Technical

- Git conflict;
- backend unavailable;
- authentication failed;
- critical file unreadable;
- incompatible version;
- unsafe path;
- incompatible active operation;
- critical validation failed;
- inconsistent artifacts.

### Methodological

- OpenSpec reports block;
- incompatible artifacts;
- duplicate change;
- unrecognized structure.

## 13.3 Representation

```python
LifecycleAssessment(
    status="blocked",
    underlying_status="applying",
    blocking_conditions=(...),
)
```

## 13.4 Conditions

`blocked` is assigned when at least one active blocking condition exists.

## 13.5 Evidence

```text
Underlying state: applying

Blocks:
- Codex CLI not authenticated.
- Working tree contains conflicts.
```

## 13.6 Suggested actions

- resolve-blocker;
- configure-backend;
- authenticate;
- inspect-git;
- open-diagnostics;
- remove-local-block;
- retry.

## 13.7 Blocking must not alter progress

A blocked change retains:

- progress;
- artifacts;
- underlying state;
- informational actions.

---

# 14. Archived state

## 14.1 Definition

The change is in the official archive location recognized by OpenSpec.

## 14.2 Condition

`archived` is assigned when:

- the change is detected under the official archive; or
- the official CLI reports it as archived and the structure is coherent.

## 14.3 Evidence

```text
- Change detected in openspec/changes/archive/.
```

## 14.4 Suggested actions

- view;
- compare;
- inspect-history;
- open-spec;
- export.

## 14.5 Restrictions

An archived change must not offer:

- apply;
- continue;
- fast-forward;
- verify as active;
- archive again.

---

# 15. Unknown state

## 15.1 Definition

OPSX TUI cannot safely evaluate the lifecycle.

## 15.2 Cases

- unknown future structure;
- critical parser error;
- unresolvable discrepancy;
- incompatible version;
- contradictory data;
- inaccessible artifacts;
- unrecognized CLI state.

## 15.3 Rule

`unknown` must not be used as a silent fallback.

It must include clear diagnostics.

## 15.4 Suggested actions

- diagnose;
- refresh;
- open-files;
- run-openspec-validation;
- update-opsx-tui;
- use-read-only-mode.

---

# 16. Formal assessment rule

The conceptual algorithm will be:

```text
1. Determine if archived.
2. Validate critical inputs.
3. Compute underlying methodological state.
4. Evaluate verification.
5. Evaluate blocks.
6. Apply precedence.
7. Compute available actions.
8. Build reasons and warnings.
9. Generate assessment fingerprint.
```

Pseudocode:

```python
def assess_lifecycle(data: LifecycleInput) -> LifecycleAssessment:
    if data.change.is_archived:
        return archived_assessment(data)

    if cannot_assess_safely(data):
        base = unknown_assessment(data)
    elif proposal_missing_or_invalid(data):
        base = draft_assessment(data)
    elif required_planning_artifacts_missing(data):
        base = planning_assessment(data)
    elif task_document_empty_or_invalid(data):
        base = planning_assessment(data)
    elif no_tasks_completed(data):
        base = ready_assessment(data)
    elif some_tasks_pending(data):
        base = applying_assessment(data)
    elif verification_is_current_and_acceptable(data):
        base = ready_to_archive_assessment(data)
    else:
        base = verification_assessment(data)

    blockers = evaluate_blockers(data, base)

    if blockers:
        return blocked_assessment(base, blockers)

    return base
```

---

# 17. Progress rules

## 17.1 Formula

```text
progress = completed_tasks / total_tasks
```

## 17.2 Representation

- value between 0 and 1;
- visual percentage;
- absolute counter;
- do not round internally;
- round only for presentation.

## 17.3 No tasks

```text
total_tasks = 0
progress = null
```

It is not represented as 0% or 100%.

## 17.4 Invalid tasks

Uninterpretable lines:

- generate a diagnostic;
- are not counted as tasks;
- may prevent `ready` if the document is not reliable.

---

# 18. Verification and currency

## 18.1 Fingerprint

Every verification must be associated with an input fingerprint.

It may include hashes of:

- proposal;
- design;
- delta specs;
- tasks;
- affected code;
- relevant configuration;
- Git commit;
- executed checks.

## 18.2 Stale state

A verification becomes `stale` when:

```text
verification.input_fingerprint != current_fingerprint
```

## 18.3 Changes that invalidate verification

Initially:

- proposal modification;
- design modification;
- delta specs modification;
- tasks modification;
- modification of files declared in scope;
- relevant commit change;
- checks configuration change;
- critical dependency change;
- manual change after verify.

## 18.4 Changes that do not necessarily invalidate

- theme change;
- UI filter;
- visual metadata;
- local note;
- recent project;
- card order.

## 18.5 Partial verification

A partial verification does not enable `ready-to-archive`.

It must remain in `verification`.

---

# 19. Available actions per state

| State | Primary actions |
|---|---|
| draft | explore, propose, open-editor |
| planning | continue, fast-forward, validate |
| ready | apply, inspect-git, checkpoint |
| applying | apply, continue, view-diff, inspect-run |
| verification | verify, inspect-findings, run-checks |
| ready-to-archive | archive, inspect-verification, export |
| blocked | resolve-blocker, diagnose, retry |
| archived | view, compare, inspect-history |
| unknown | diagnose, refresh, validate |

Final actions also depend on:

- capabilities;
- backend;
- version;
- security;
- Git;
- active operation.

---

# 20. Typical transitions

Transitions are not mandatory, but these paths are expected.

## 20.1 Normal flow

```text
draft
→ planning
→ ready
→ applying
→ verification
→ ready-to-archive
→ archived
```

## 20.2 Fast-forward flow

```text
draft
→ ready
```

if the agent generates all required artifacts.

## 20.3 Regression by edit

```text
ready-to-archive
→ verification
```

if a verified input changes.

## 20.4 Planning regression

```text
ready
→ planning
```

if a required artifact is removed.

## 20.5 Block

```text
applying
→ blocked(applying)
→ applying
```

## 20.6 Structural error

```text
planning
→ unknown
```

if a new structure cannot be interpreted.

---

# 21. Events that trigger re-evaluation

Lifecycle must be re-evaluated on:

- artifact creation;
- artifact modification;
- artifact deletion;
- change movement;
- task change;
- execution finished;
- verification finished;
- local metadata change;
- backend change;
- credentials change;
- Git change;
- OpenSpec version change;
- manual refresh;
- execution recovery.

---

# 22. Consistency during writes

## 22.1 Debounce

The assessment must wait for filesystem stability.

## 22.2 Transient state

`unknown` must not be displayed instantaneously during an expected atomic replacement.

The app may temporarily retain the last assessment and display:

```text
refreshing
```

as a visual indicator, not as a Kanban state.

## 22.3 Stability timeout

If the file remains inconsistent after the retry period:

- re-evaluate;
- generate diagnostic;
- use `unknown` or `blocked` depending on severity.

---

# 23. Kanban UI rules

## 23.1 Columns

Initial columns:

```text
Draft
Planning
Ready
Applying
Verification
Ready to Archive
Blocked
```

Archived is displayed:

- in a separate view; or
- via an explicit filter.

## 23.2 Unknown

May be displayed in:

- Diagnostics column;
- special section;
- Unknown column if changes exist.

## 23.3 Card

Each card must display at least:

- name;
- progress;
- state;
- artifacts;
- alerts;
- block;
- last activity.

## 23.4 Manual movement

Moving a card to assign state will not be allowed.

A future movement interaction may:

- suggest an action;
- open confirmation;
- execute an operation.

Example:

```text
Move from Ready to Applying
→ suggest /opsx:apply
```

## 23.5 Order

Default order within a column:

1. priority;
2. critical blocks;
3. last modified;
4. name.

Must be configurable.

---

# 24. Filters

Compatible filters:

- state;
- underlying state;
- blocked;
- priority;
- tag;
- text;
- with warnings;
- with errors;
- with backend available;
- with active execution;
- stale verification;
- archived.

Filters do not alter lifecycle.

---

# 25. Discrepancy with OpenSpec CLI

## 25.1 Rule

If the CLI reports a different state:

- retain local assessment;
- retain reported official state;
- display discrepancy;
- generate warning;
- avoid silent overwrite.

## 25.2 Preference

For official operations, the CLI state may block or enable actions.

For display, both are shown:

```text
OPSX TUI: applying
OpenSpec CLI: ready
```

## 25.3 Resolution

Actions:

- refresh;
- validate;
- inspect;
- update compatibility adapter;
- manual review.

---

# 26. Initially defined blocks

## 26.1 Critical

- path outside workspace;
- Git conflict;
- incompatible version for operation;
- required backend absent;
- authentication failed;
- critical artifact unreadable;
- active modifying process;
- critical verification failed before archive;
- ambiguous archive result.

## 26.2 Non-critical

- alternative backend unavailable;
- format warning;
- local metadata absent;
- Git unavailable in read mode;
- optional provider unconfigured.

## 26.3 Manual

The user may define:

- blocked reason;
- dependency;
- decision pending;
- external approval.

A manual block must include a description.

---

# 27. Diagnostic severity

| Severity | Impact |
|---|---|
| info | Does not change state |
| warning | May be shown on card |
| error | May limit actions |
| critical | Produces blocked or unknown |

Severity alone does not decide the state; it depends on category and policy.

---

# 28. Special cases

## 28.1 Change without tasks.md

- proposal exists;
- other artifacts exist;
- tasks absent.

Outcome:

```text
planning
```

## 28.2 Change with all tasks checked, but required artifact missing

Outcome:

```text
planning
warning = tasks complete while planning artifact is missing
```

May be `blocked` if it cannot be verified.

## 28.3 Archived change with incomplete tasks

Outcome:

```text
archived
warning = archived with incomplete tasks
```

Archived retains precedence.

## 28.4 Successful verification then change in tasks.md

Outcome:

```text
verification
verification_state = stale
```

## 28.5 Backend unavailable in draft

Methodological state:

```text
draft
```

Visible state:

```text
blocked
underlying_status = draft
```

only if the backend is mandatory for the desired action or current policy.

## 28.6 No Git

Does not block reading.

May block apply if the policy requires a clean Git.

## 28.7 Change unknown to CLI

Displayed from filesystem and a warning is generated.

---

# 29. Recommended Pydantic model

```python
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ChangeStatus(StrEnum):
    DRAFT = "draft"
    PLANNING = "planning"
    READY = "ready"
    APPLYING = "applying"
    VERIFICATION = "verification"
    READY_TO_ARCHIVE = "ready-to-archive"
    BLOCKED = "blocked"
    ARCHIVED = "archived"
    UNKNOWN = "unknown"


class BlockingCondition(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str
    message: str
    severity: str
    recoverable: bool
    suggested_actions: tuple[str, ...] = ()


class LifecycleAssessment(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: ChangeStatus
    underlying_status: ChangeStatus | None = None
    reasons: tuple[str, ...]
    warnings: tuple[str, ...] = ()
    blocking_conditions: tuple[BlockingCondition, ...] = ()
    available_actions: tuple[str, ...] = ()
    assessed_at: datetime
    input_fingerprint: str
```

---

# 30. Test requirements

## 30.1 Mandatory unit tests

- draft without proposal;
- planning with missing artifact;
- ready with zero completed tasks;
- partial applying;
- verification with completed tasks;
- ready-to-archive with current verify;
- stale verify;
- blocked with underlying state;
- archived;
- unknown;
- empty tasks;
- unreadable artifact;
- CLI discrepancy;
- fingerprint change;
- Git block;
- no Git;
- manual metadata.

## 30.2 Property-based testing

Recommended to verify:

- progress between 0 and 1;
- determinism;
- archived always dominates;
- blocked preserves underlying;
- ready-to-archive requires current verification;
- never ready with empty tasks;
- never applying with zero completed tasks;
- never verification with pending tasks.

## 30.3 Fixtures

```text
tests/fixtures/lifecycle/
├── draft-empty/
├── planning-missing-design/
├── ready/
├── applying/
├── verification/
├── ready-to-archive/
├── blocked/
├── archived-incomplete/
├── unknown-structure/
└── stale-verification/
```

---

# 31. Invariants

1. `archived` always dominates.
2. `blocked` requires at least one block.
3. `blocked` must include underlying state when computable.
4. `ready` requires actionable tasks.
5. `applying` requires completed and pending tasks.
6. `verification` requires all tasks completed.
7. `ready-to-archive` requires current verification.
8. A stale verification does not enable archive.
9. Progress is not persisted as truth.
10. The same input produces the same assessment.
11. The UI does not modify the assessment.
12. A malformed change remains visible.
13. Unknown always includes a diagnostic.
14. Available actions respect capabilities.
15. A state is not assigned by drag-and-drop.

---

# 32. Constraints for the implementing agent

The agent must not:

- manually store the Kanban state;
- infer progress from history;
- use dates as a primary rule without specification;
- create additional states without an OpenSpec change;
- mix active execution with lifecycle state;
- consider empty tasks as completed;
- consider exit code 0 as verification;
- ignore fingerprints;
- hide blocks under a generic column;
- overwrite local state with CLI without showing discrepancy;
- implement rules in widgets;
- duplicate rules between screen and service;
- allow archive with stale verification;
- move cards to silently change state;
- treat warnings as blocks without policy.

---

# 33. Summary

The lifecycle answers four questions:

```text
Does a usable definition exist?
→ draft / planning

Is it ready or in implementation?
→ ready / applying

Is it implemented and verified?
→ verification / ready-to-archive

Does a dominant condition exist?
→ blocked / archived / unknown
```

The main rule is:

```text
The Kanban state is not chosen.
It is demonstrated.
```
