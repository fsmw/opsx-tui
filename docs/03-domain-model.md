# Domain Model and Glossary — OPSX TUI

## 1. Purpose

This document defines the domain model of **OPSX TUI** and the common vocabulary that must be used by OpenSpec specifications, code, tests, the interface, and documentation.

Its goal is to prevent concepts such as `workspace`, `change`, `spec`, `backend`, `provider`, `execution`, or `verification` from being interpreted differently across layers or project phases.

This document is normative. The names, responsibilities, and relationships defined here must be maintained, unless explicitly modified by an architectural decision or a later OpenSpec change.

---

# 2. Model principles

## 2.1 OpenSpec is the methodological source of truth

OPSX TUI represents and operates an OpenSpec project, but does not replace its model.

The following concepts belong to OpenSpec:

- canonical specs;
- active changes;
- archived changes;
- proposals;
- designs;
- tasks;
- delta specs;
- requirements;
- scenarios;
- methodological artifacts.

OPSX TUI must not duplicate this data as a second authoritative source.

## 2.2 The domain does not depend on the interface

Domain models must not import:

- Textual;
- widgets;
- screens;
- TCSS;
- visual APIs;
- focus state;
- terminal components.

The interface consumes snapshots and results from the domain, but does not determine its rules.

## 2.3 The domain does not depend on concrete implementations

Domain models and application services must not depend directly on:

- real filesystem;
- SQLite;
- Git;
- OpenSpec CLI;
- Codex CLI;
- keyring;
- LLM providers;
- subprocesses.

These capabilities are exposed via ports or contracts.

## 2.4 Snapshots are immutable

Reading a workspace produces an immutable snapshot.

When a file changes, a new snapshot is generated instead of modifying the previous one.

This enables:

- reactive updates;
- comparisons;
- deterministic tests;
- reduced race conditions;
- change audit.

## 2.5 External entities preserve their original identity

Names and paths coming from OpenSpec must be preserved.

The application may add internal identifiers for persistence, but must not replace:

- change name;
- spec path;
- task identifier;
- artifact name;
- workspace structure.

---

# 3. Domain overview map

```text
OPSXTuiApplication
│
├── Project
│   ├── OpenSpecWorkspace
│   │   ├── CanonicalSpec
│   │   │   ├── Requirement
│   │   │   └── Scenario
│   │   │
│   │   ├── ActiveChange
│   │   │   ├── ProposalArtifact
│   │   │   ├── DesignArtifact
│   │   │   ├── DeltaSpec
│   │   │   ├── TaskDocument
│   │   │   │   └── Task
│   │   │   └── LifecycleAssessment
│   │   │
│   │   ├── ArchivedChange
│   │   └── WorkspaceDiagnostic
│   │
│   ├── ProjectConfiguration
│   ├── GitWorkspaceState
│   └── LocalChangeMetadata
│
├── CommandCatalog
│   └── CommandDefinition
│
├── AgentBackendRegistry
│   ├── AgentBackend
│   ├── BackendCapabilities
│   └── BackendHealth
│
├── LLMProviderRegistry
│   ├── LLMProvider
│   └── ProviderCapabilities
│
└── Execution
    ├── ExecutionRequest
    ├── ExecutionEvent
    ├── ExecutionResult
    ├── AffectedFile
    └── VerificationRecord
```

---

# 4. Main contexts

The domain is divided into six functional contexts.

## 4.1 Workspace

Responsible for representing the OpenSpec project.

Includes:

- root discovery;
- spec loading;
- change loading;
- artifact reading;
- task parsing;
- diagnostics;
- snapshots;
- change observation.

## 4.2 Lifecycle

Responsible for inferring the operational state of each change.

Includes:

- state;
- reasons;
- warnings;
- available actions;
- blocking;
- verification freshness;
- underlying state.

## 4.3 Commands

Responsible for describing available operations.

Includes:

- local commands;
- agent actions;
- compatibility;
- parameters;
- risks;
- confirmations;
- preconditions.

## 4.4 Backends and providers

Responsible for abstracting agents and LLM providers.

Includes:

- capabilities;
- configuration;
- healthcheck;
- models;
- execution;
- cancellation;
- authentication;
- error normalization.

## 4.5 Execution

Responsible for representing each executed process.

Includes:

- request;
- state;
- events;
- output;
- result;
- cancellation;
- affected files;
- history;
- recovery.

## 4.6 Configuration and Operations

Responsible for OPSX TUI's own data.

Includes:

- global configuration;
- per-project configuration;
- visual preferences;
- local metadata;
- recent projects;
- persistence;
- security;
- Git.

---

# 5. Entities and value objects

# 5.1 Project

## Definition

Represents a project known to OPSX TUI.

It is not exactly equivalent to a Git repository nor to the `openspec/` folder.

## Attributes

| Field | Type | Description |
|---|---|---|
| `id` | internal UUID | Local persistent identity |
| `root` | `Path` | Project operational root |
| `openspec_root` | `Path` | OpenSpec folder path |
| `display_name` | `str` | Display name |
| `discovery_source` | enum | How it was found |
| `last_opened_at` | optional datetime | Last opened |
| `is_valid` | bool | Validation result |
| `diagnostics` | tuple | Detected problems |

## Rules

- `root` must be absolute and normalized.
- `openspec_root` must be inside `root`, except for explicit future compatibility.
- It must not be inferred that `root` is always the Git root.
- The project may exist even if Git is not available.
- An invalid project may be represented to show diagnostics.

---

# 5.2 OpenSpecWorkspace

## Definition

Immutable snapshot of a project's OpenSpec content at a given moment.

## Attributes

| Field | Type |
|---|---|
| `project_root` | `Path` |
| `openspec_root` | `Path` |
| `loaded_at` | datetime |
| `openspec_version` | optional version |
| `canonical_specs` | tuple of `CanonicalSpec` |
| `active_changes` | tuple of `Change` |
| `archived_changes` | tuple of `Change` |
| `diagnostics` | tuple of `WorkspaceDiagnostic` |
| `fingerprint` | hash or snapshot identifier |

## Rules

- It is immutable.
- Must be constructible without Textual.
- Must contain only data needed to represent the workspace.
- Must not contain connections, processes, or open handles.
- Its `fingerprint` must change when relevant content changes.

---

# 5.3 CanonicalSpec

## Definition

Current canonical specification of a product capability.

## Attributes

| Field | Type |
|---|---|
| `name` | `str` |
| `path` | `Path` |
| `title` | optional `str` |
| `raw_content` | `str` |
| `requirements` | tuple of `Requirement` |
| `related_changes` | tuple of names |
| `diagnostics` | tuple |

## Rules

- The name is derived from OpenSpec structure.
- `raw_content` preserves the original Markdown.
- The parser may extract structure without altering content.
- Partial errors must produce diagnostics, not complete spec loss.

---

# 5.4 Requirement

## Definition

Normative behavior defined within a spec.

## Attributes

| Field | Type |
|---|---|
| `identifier` | optional `str` |
| `title` | `str` |
| `statement` | `str` |
| `scenarios` | tuple of `Scenario` |
| `source_path` | `Path` |
| `line_start` | int |
| `line_end` | int |

## Rules

- The statement must preserve normative terms such as SHALL, MUST, or equivalents.
- A requirement may have no explicit identifier.
- The source location must be preserved for navigation and diagnostics.

---

# 5.5 Scenario

## Definition

Verifiable behavior example within a requirement.

## Attributes

| Field | Type |
|---|---|
| `title` | `str` |
| `given` | tuple of strings |
| `when` | tuple of strings |
| `then` | tuple of strings |
| `and_steps` | tuple of strings |
| `source_path` | `Path` |
| `line_start` | int |

## Rules

- The parser must not invent missing steps.
- Original text is preserved for rendering.
- Incomplete scenarios generate a diagnostic.

---

# 5.6 Change

## Definition

Represents an active or archived OpenSpec change.

## Attributes

| Field | Type |
|---|---|
| `name` | `str` |
| `path` | `Path` |
| `kind` | active or archived |
| `proposal` | optional `Artifact` |
| `design` | optional `Artifact` |
| `delta_specs` | tuple of `DeltaSpec` |
| `task_document` | optional `TaskDocument` |
| `artifacts` | tuple of `Artifact` |
| `lifecycle` | `LifecycleAssessment` |
| `diagnostics` | tuple |
| `modified_at` | optional datetime |

## Rules

- `name` is the functional identity of the change.
- Archived state is derived from its actual location.
- Lifecycle must not be persisted as truth in SQLite.
- A change may exist with incomplete artifacts.
- A malformed change must remain visible.
- The UI cannot directly mutate the object.

---

# 5.7 Artifact

## Definition

Significant file belonging to a change.

## Initial types

- proposal;
- design;
- task document;
- delta spec;
- configuration;
- unknown.

## Attributes

| Field | Type |
|---|---|
| `artifact_type` | enum |
| `path` | `Path` |
| `relative_path` | `Path` |
| `exists` | bool |
| `readable` | bool |
| `size_bytes` | optional int |
| `modified_at` | optional datetime |
| `content_hash` | optional string |
| `raw_content` | optional string |
| `diagnostics` | tuple |

## Rules

- An expected artifact may be represented with `exists=False`.
- `raw_content` may be loaded on demand for large projects.
- The resolved path must be validated against the project root.
- External symlinks must produce a warning or block per policy.

---

# 5.8 DeltaSpec

## Definition

Specification associated with a change that adds, modifies, or removes behavior relative to a canonical spec.

## Attributes

| Field | Type |
|---|---|
| `capability_name` | `str` |
| `path` | `Path` |
| `raw_content` | `str` |
| `operations` | tuple of `SpecDeltaOperation` |
| `target_spec` | optional reference |
| `diagnostics` | tuple |

## Initial operations

- added;
- modified;
- removed;
- renamed;
- unknown.

## Rules

- The application must not apply deltas on its own.
- It may display and compare them.
- Unknown operations are preserved as `unknown`.
- The target canonical spec may not yet exist.

---

# 5.9 TaskDocument

## Definition

Structured representation of `tasks.md`.

## Attributes

| Field | Type |
|---|---|
| `path` | `Path` |
| `sections` | tuple of `TaskSection` |
| `tasks` | tuple of `Task` |
| `completed_count` | int |
| `total_count` | int |
| `progress_ratio` | decimal |
| `raw_content` | string |
| `diagnostics` | tuple |

## Rules

- Progress is derived from tasks.
- It is not persisted as a separate source.
- Reading does not modify checkboxes.
- Numbers are recalculated when rebuilding the snapshot.

---

# 5.10 Task

## Definition

Verifiable unit of work declared in `tasks.md`.

## Attributes

| Field | Type |
|---|---|
| `identifier` | optional `str` |
| `title` | `str` |
| `completed` | bool |
| `section` | optional `str` |
| `indent_level` | int |
| `source_path` | `Path` |
| `line_number` | int |
| `raw_line` | `str` |

## Rules

- `completed` is derived from the checkbox.
- The identifier may not exist.
- The source line is mandatory.
- A task must not be stored duplicated in SQLite.
- The TUI must not mark tasks without an explicit operation.

---

# 5.11 LifecycleAssessment

## Definition

Explainable evaluation of a change's operational state.

## Attributes

| Field | Type |
|---|---|
| `status` | `ChangeStatus` |
| `underlying_status` | optional state |
| `reasons` | tuple of strings |
| `warnings` | tuple of strings |
| `available_actions` | tuple of identifiers |
| `blocking_conditions` | tuple |
| `verification_state` | enum |
| `assessed_at` | datetime |
| `input_fingerprint` | string |

## Initial states

- draft;
- planning;
- ready;
- applying;
- verification;
- ready-to-archive;
- blocked;
- archived;
- unknown.

## Rules

- Must be deterministic for the same input.
- Must always include reasons.
- `blocked` may wrap an underlying state.
- `archived` has the highest precedence.
- Not persisted as methodological truth.
- Must be recalculated if its fingerprint changes.

---

# 5.12 LocalChangeMetadata

## Definition

OPSX TUI's own operational information associated with a change.

## Allowed fields

| Field | Description |
|---|---|
| `priority` | Visual priority |
| `tags` | Auxiliary tags |
| `blocked_reason` | Local reason |
| `favorite` | Bookmark |
| `notes` | Operational notes |
| `display_order` | Optional visual order |

## Prohibited fields

- progress;
- tasks;
- proposal content;
- archived state;
- computed lifecycle;
- copy of delta specs;
- official methodological verification.

## Rules

- Must not alter OpenSpec artifacts.
- May be stored per project.
- Its absence does not affect workspace reading.
- `blocked_reason` may trigger `blocked` presentation.

---

# 5.13 CommandDefinition

## Definition

Describes an operation that OPSX TUI can offer.

## Attributes

| Field | Type |
|---|---|
| `id` | stable string |
| `label` | string |
| `executor_type` | internal, openspec-cli, agent, provider |
| `requires_project` | bool |
| `requires_change` | bool |
| `mutates_workspace` | bool |
| `requires_confirmation` | bool |
| `parameters` | tuple |
| `required_capabilities` | tuple |
| `availability_rules` | tuple |
| `supported_versions` | optional range |

## Rules

- The UI consumes the catalog; it does not hardcode operations.
- Availability must include explanation.
- Incompatible actions may be shown as disabled.
- A modifying operation must never be marked as informational.

---

# 5.14 AgentBackend

## Definition

Adapter capable of executing a programming agent.

Examples:

- Codex CLI;
- Claude Code;
- Gemini CLI.

## Responsibilities

- healthcheck;
- declare capabilities;
- list or validate models;
- execute;
- emit events;
- cancel;
- normalize result;
- hide specific differences.

## Non-responsibilities

- infer lifecycle;
- render UI;
- write history directly;
- decide confirmations;
- modify global configuration;
- interpret functional success on its own.

---

# 5.15 BackendCapabilities

## Definition

Set of capabilities declared by a backend.

## Initial fields

```text
supports_streaming
supports_cancellation
supports_model_selection
supports_approval_modes
supports_sandbox
supports_workspace_write
supports_network_policy
supports_structured_events
supports_resume
```

## Rules

- The UI must not assume undeclared capabilities.
- Operations require specific capabilities.
- A backend may be available but incompatible with an operation.

---

# 5.16 LLMProvider

## Definition

Model provider invoked via API, not necessarily a complete programming agent.

Examples:

- OpenAI-compatible;
- OpenRouter;
- LM Studio;
- Ollama compatible;
- Anthropic;
- Gemini.

## Difference from AgentBackend

An `AgentBackend` can operate on the workspace and execute tools.

An `LLMProvider` delivers model access, but does not by itself imply:

- filesystem;
- tools;
- shell;
- editing;
- verification;
- code execution.

## Rule

They must not be treated as synonyms.

---

# 5.17 Execution

## Definition

Observable instance of an operation executed by OPSX TUI.

## Attributes

| Field | Type |
|---|---|
| `id` | UUID |
| `project_id` | reference |
| `change_name` | optional |
| `command_id` | string |
| `executor_type` | enum |
| `backend_id` | optional |
| `provider_id` | optional |
| `model` | optional |
| `status` | `ExecutionStatus` |
| `started_at` | datetime |
| `finished_at` | optional datetime |
| `exit_code` | optional int |
| `summary` | optional string |
| `request_fingerprint` | string |
| `workspace_before` | optional fingerprint |
| `workspace_after` | optional fingerprint |

## States

- pending;
- validating;
- awaiting-confirmation;
- running;
- cancelling;
- cancelled;
- succeeded;
- failed;
- interrupted;
- unknown.

## Rules

- Each execution has its own identity.
- State is persisted operationally.
- `succeeded` does not automatically imply all requirements are met.
- The result must be validated with additional evidence where applicable.
- An interrupted execution is detected when the application starts.

---

# 5.18 ExecutionRequest

## Definition

Validated request before starting an execution.

## Attributes

- operation;
- project;
- change;
- backend;
- provider;
- model;
- timeout;
- sandbox;
- approval mode;
- arguments;
- allowed environment variables;
- previewed prompt or command.

## Rules

- Contains no secrets in persistable text.
- Must be partially showable to the user.
- Must be validated before creating the process.
- Paths must be normalized.

---

# 5.19 ExecutionEvent

## Definition

Immutable event emitted during an execution.

## Initial types

```text
execution.started
validation.completed
process.spawned
stdout.received
stderr.received
artifact.created
artifact.modified
artifact.deleted
task.changed
verification.started
verification.completed
execution.cancellation-requested
execution.cancelled
execution.failed
execution.completed
```

## Attributes

| Field | Type |
|---|---|
| `sequence` | integer |
| `timestamp` | datetime |
| `event_type` | enum |
| `message` | string |
| `severity` | enum |
| `metadata` | serializable map |
| `redacted` | bool |

## Rules

- Sequence must be monotonic per execution.
- Secrets are redacted before persisting.
- Events must not contain non-serializable objects.
- The UI may group events, but the model preserves their order.

---

# 5.20 ExecutionResult

## Definition

Normalized result when an execution finishes.

## Attributes

- technical success;
- exit code;
- summary;
- normalized error;
- affected files;
- performed validations;
- warnings;
- duration;
- cancelled;
- output truncated;
- follow-up actions.

## Main rule

Technical success does not necessarily equal functional success.

Example:

```text
Process finished with exit code 0
but proposal.md was not created
→ technically successful execution, failed functional validation.
```

---

# 5.21 AffectedFile

## Definition

File whose creation, modification, or deletion was detected during an execution.

## Attributes

- path;
- relative path;
- change type;
- hash before;
- hash after;
- inside workspace;
- sensitive;
- tracked by Git;
- detected source.

## Rules

- Files outside the workspace must generate an alert.
- Contents are not persisted by default.
- Hashes may be used to invalidate verifications.

---

# 5.22 VerificationRecord

## Definition

Operational record of an executed verification.

## Attributes

- project;
- change;
- execution;
- status;
- verified_at;
- verifier;
- input fingerprint;
- checks;
- findings;
- valid until fingerprint changes.

## States

- not-run;
- running;
- passed;
- passed-with-warnings;
- failed;
- stale;
- interrupted.

## Rules

- A verification becomes `stale` if a relevant artifact changes.
- It does not replace official OpenSpec data.
- It serves as evidence for `ready-to-archive`.
- Must indicate what was verified.

---

# 5.23 WorkspaceDiagnostic

## Definition

Problem or warning detected when reading a project.

## Categories

- structure;
- parse;
- permission;
- compatibility;
- path;
- version;
- configuration;
- security;
- unknown.

## Severities

- info;
- warning;
- error;
- critical.

## Rules

- A diagnostic does not always invalidate the project.
- Must include location when available.
- Must suggest action when possible.
- Must never include secrets.

---

# 5.24 GitWorkspaceState

## Definition

Snapshot of the project's Git state.

## Attributes

- is repository;
- root;
- branch;
- head commit;
- dirty;
- staged files;
- unstaged files;
- untracked files;
- conflicts;
- detached head;
- upstream;
- optional ahead/behind.

## Rules

- Git is optional for reading.
- Modifying operations may require Git policy.
- This state is not part of OpenSpec.
- It is recalculated before and after relevant executions.

---

# 6. Application services

Services coordinate use cases and depend on ports.

# 6.1 ProjectDiscoveryService

Responsibilities:

- resolve explicit path;
- read environment variable;
- upward search;
- evaluate Git root;
- list recent projects;
- validate candidate;
- produce `ProjectDiscoveryResult`.

Must not:

- auto-initialize OpenSpec;
- modify files;
- open UI.

---

# 6.2 WorkspaceService

Responsibilities:

- load snapshot;
- partially refresh;
- resolve artifacts;
- coordinate parsers;
- compute fingerprint;
- produce diagnostics.

Must not:

- execute commands;
- persist history;
- decide visual presentation.

---

# 6.3 LifecycleService

Responsibilities:

- receive `Change`;
- evaluate rules;
- consider local metadata;
- consider verification;
- produce `LifecycleAssessment`.

Must be pure when possible.

---

# 6.4 CommandCatalogService

Responsibilities:

- register operations;
- evaluate availability;
- declare risks;
- resolve parameters;
- select appropriate executor.

---

# 6.5 ExecutionService

Responsibilities:

- validate request;
- create execution;
- invoke executor;
- stream events;
- cancel;
- build result;
- coordinate persistence;
- refresh workspace.

---

# 6.6 BackendRegistryService

Responsibilities:

- register backends;
- resolve backend per operation;
- healthcheck;
- capabilities;
- models;
- configuration errors.

---

# 6.7 ConfigurationService

Responsibilities:

- load defaults;
- load global configuration;
- load project configuration;
- apply environment variables;
- apply CLI;
- validate;
- migrate schemas;
- save non-sensitive configuration.

---

# 6.8 HistoryService

Responsibilities:

- persist executions;
- persist events;
- query history;
- apply retention;
- detect interrupted executions;
- export.

---

# 6.9 SecurityService

Responsibilities:

- validate paths;
- detect secrets;
- redact;
- evaluate policies;
- approve environment variables;
- verify executables;
- control access outside the workspace.

---

# 7. Infrastructure ports

The following contracts must exist as `Protocol` or equivalent abstractions.

## 7.1 WorkspaceReader

```python
class WorkspaceReader(Protocol):
    async def load(self, project: Project) -> OpenSpecWorkspace:
        ...
```

## 7.2 WorkspaceWatcher

```python
class WorkspaceWatcher(Protocol):
    async def events(self, project: Project) -> AsyncIterator[WorkspaceEvent]:
        ...
```

## 7.3 DocumentReader

```python
class DocumentReader(Protocol):
    async def read_text(self, path: Path) -> str:
        ...
```

## 7.4 ProcessRunner

```python
class ProcessRunner(Protocol):
    async def execute(
        self,
        request: ProcessRequest,
    ) -> AsyncIterator[ProcessEvent]:
        ...

    async def cancel(self, process_id: str) -> None:
        ...
```

## 7.5 ExecutionRepository

```python
class ExecutionRepository(Protocol):
    async def save_execution(self, execution: Execution) -> None:
        ...

    async def append_event(self, execution_id: UUID, event: ExecutionEvent) -> None:
        ...
```

## 7.6 SecretStore

```python
class SecretStore(Protocol):
    async def get(self, key: str) -> str | None:
        ...

    async def set(self, key: str, value: str) -> None:
        ...

    async def delete(self, key: str) -> None:
        ...
```

## 7.7 GitInspector

```python
class GitInspector(Protocol):
    async def inspect(self, root: Path) -> GitWorkspaceState:
        ...
```

---

# 8. Layer relationships

## 8.1 Presentation

May depend on:

- application;
- domain;
- derived view models.

Must not depend directly on:

- infrastructure;
- filesystem;
- subprocess;
- SQLite;
- Git;
- keyring.

## 8.2 Application

May depend on:

- domain;
- ports;
- contracts.

Must not depend on:

- Textual;
- widgets;
- concrete implementations.

## 8.3 Domain

May depend on:

- standard Python;
- Pydantic;
- own types.

Must not depend on:

- application;
- infrastructure;
- presentation.

## 8.4 Infrastructure

May depend on:

- domain;
- ports;
- application contracts when necessary.

Implements:

- filesystem;
- CLI;
- Git;
- SQLite;
- keyring;
- agents;
- providers.

---

# 9. Pydantic conventions

## 9.1 Version

Pydantic 2 shall be used.

## 9.2 Immutability

Snapshots and events must use:

```python
ConfigDict(frozen=True)
```

## 9.3 Paths

`pathlib.Path` shall be used.

Persisted paths must be serialized portably where applicable.

## 9.4 Datetime

Time zone-aware datetimes shall be used.

Naive timestamps are not accepted in persistence.

## 9.5 Enumerations

`StrEnum` shall be used for serializable states.

## 9.6 Arbitrary data

`arbitrary_types_allowed` shall not be enabled except with explicit justification.

## 9.7 Validation at boundaries

Pydantic shall be used especially in:

- configuration reading;
- adapter results;
- persistence;
- events;
- contracts between layers.

Shall not be used to represent process handles or widgets.

---

# 10. Glossary

## Agent

System capable of reasoning and executing development actions on a workspace.

Not synonymous with an LLM model.

## Agent Backend

Concrete adapter that enables invoking an agent, e.g. Codex CLI.

## Artifact

Significant file within OpenSpec.

## Backend

Executor component configured for a class of operation.

In this project, typically refers to an agent backend.

## Canonical Spec

Current specification representing the accepted product behavior.

## Change

Active or archived OpenSpec change unit.

## Command

Operation registered in the OPSX TUI catalog.

## Delta Spec

Proposed change relative to a canonical spec.

## Diagnostic

Finding generated when validating structure, content, configuration, or security.

## Execution

Instance of an executed operation.

## Execution Event

Ordered event produced during an execution.

## Executor

Component capable of performing an operation.

May be internal, CLI, agent, or provider.

## Lifecycle

Evaluation of a change's operational state.

## LLM Provider

Service that delivers model access via API.

Does not imply agent capabilities.

## Local Metadata

Auxiliary OPSX TUI information that is not part of OpenSpec.

## OpenSpec CLI

Official executable used for supported commands and queries.

## OPSX Action

Methodological action typically executed via an agent.

## Process Runner

Abstraction for creating, observing, and canceling processes.

## Project

Operational root opened by OPSX TUI.

## Proposal

Artifact explaining motivation and scope of a change.

## Provider

Model service. Must not be confused with agent backend.

## Requirement

Normative rule of a capability.

## Scenario

Verifiable example of a requirement.

## Snapshot

Immutable representation of a state at a given moment.

## Spec

Specification of a capability.

## Task

Unit of work declared in `tasks.md`.

## TUI

User interface running inside the terminal.

## Verification

Process that gathers evidence that a change meets its requirements.

## Workspace

Loaded OpenSpec content for a project.

## Workspace Root

OpenSpec root within the project.

---

# 11. Terms not to be confused

| Term A | Term B | Difference |
|---|---|---|
| Project | Workspace | Project is the operational root; Workspace is the OpenSpec snapshot |
| Agent | LLM | An agent uses tools; an LLM only produces responses |
| Backend | Provider | Backend executes an agent; provider offers models |
| Command | Process | Command is a definition; process is an OS instance |
| Execution | Command | Execution is a concrete run |
| Spec | Delta Spec | Spec is canonical; delta proposes changes |
| Status | LifecycleAssessment | Status is a value; assessment includes evidence |
| Verification | Execution success | Functional verification does not equal exit code 0 |
| Artifact | File | Artifact is a file with methodological meaning |
| OpenSpec data | Local metadata | The former is canonical; the latter is operational |

---

# 12. Domain invariants

The following rules must not be violated.

1. An `ArchivedChange` cannot be evaluated as active.
2. A task belongs to a single `TaskDocument`.
3. Progress is derived from tasks.
4. Lifecycle is derived from evidence.
5. Local metadata cannot turn a change into archived.
6. A provider is not presented as an agent backend if it lacks tools.
7. An execution has a single main operation.
8. An execution's events maintain order.
9. A verification is invalidated if its input fingerprint changes.
10. No secret may be persisted within an event.
11. The UI does not modify immutable models.
12. Write paths must be validated inside the workspace.
13. Operational history does not replace OpenSpec artifacts.
14. Technical success does not imply functional success.
15. A critical diagnostic may prevent an operation, but must not hide the project.

---

# 13. Suggested module structure

```text
src/opsx_tui/
├── domain/
│   ├── project.py
│   ├── workspace.py
│   ├── specs.py
│   ├── changes.py
│   ├── tasks.py
│   ├── lifecycle.py
│   ├── commands.py
│   ├── backends.py
│   ├── providers.py
│   ├── executions.py
│   ├── verification.py
│   ├── diagnostics.py
│   └── git.py
│
├── application/
│   ├── ports/
│   ├── project_discovery.py
│   ├── workspace_service.py
│   ├── lifecycle_service.py
│   ├── command_catalog.py
│   ├── execution_service.py
│   ├── backend_registry.py
│   ├── configuration_service.py
│   ├── history_service.py
│   └── security_service.py
│
├── infrastructure/
│   ├── filesystem/
│   ├── openspec_cli/
│   ├── processes/
│   ├── persistence/
│   ├── git/
│   ├── secrets/
│   ├── agents/
│   └── providers/
│
└── presentation/
    ├── screens/
    ├── widgets/
    ├── controllers/
    └── view_models/
```

---

# 14. View models

The presentation may create derived models to optimize rendering.

Examples:

- `ChangeCardViewModel`;
- `KanbanColumnViewModel`;
- `ExecutionRowViewModel`;
- `SpecTreeNodeViewModel`.

Rules:

- They are not domain models.
- They may contain formatted text and visual symbols.
- They must not be persisted.
- They must not introduce new business rules.
- They must be built from domain models.

---

# 15. Model acceptance criteria

The model shall be considered correctly implemented when:

1. It can represent a valid and an invalid project.
2. It can represent incomplete specs and changes.
3. It can load a workspace without Textual.
4. It can serialize relevant snapshots.
5. It can compute progress without duplicated persistence.
6. It can produce lifecycle with reasons.
7. It distinguishes backend from provider.
8. It distinguishes command from execution.
9. It maintains ordered events.
10. It invalidates verifications by fingerprint.
11. It allows simulated adapters in tests.
12. It does not depend on infrastructure implementations.
13. It does not expose secrets.
14. It preserves source paths and lines.
15. It supports Python 3.11.

---

# 16. Constraints for the implementing agent

The agent shall not:

- replace Pydantic with dataclasses as the main model;
- make snapshots mutable without justification;
- import Textual within the domain;
- use database models as domain models;
- duplicate tasks in SQLite;
- mix provider with agent backend;
- store lifecycle as canonical state;
- compute business rules in widgets;
- use unnormalized paths;
- ignore parse diagnostics;
- remove unknown artifacts from the model;
- infer functional success from an agent message;
- create a deep, unnecessary class hierarchy;
- add repositories or services without a real use case.

---

# 17. Summary

The OPSX TUI domain is organized around four questions:

```text
What exists?
→ Workspace, specs, changes, artifacts, and tasks.

What state is it in?
→ LifecycleAssessment and VerificationRecord.

What can be done?
→ CommandDefinition, BackendCapabilities, and policies.

What happened?
→ Execution, ExecutionEvent, and ExecutionResult.
```

The main conceptual separation is:

```text
OpenSpec describes the product and its changes.
OPSX TUI describes how they are visualized and operated.
Backends execute.
Executions record what happened.
The interface presents, but does not define the domain.
```
