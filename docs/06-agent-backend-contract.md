# Agent Backend Contract — OPSX TUI

## 1. Purpose

This document defines the functional and technical contract that agent backends integrated with **OPSX TUI** must fulfill.

The contract aims to ensure that different agents, such as Codex CLI, Claude Code, or Gemini CLI, can be used through a common interface without leaking unnecessary differences to the UI or domain.

This document establishes:

- what an agent backend is;
- what capabilities it may declare;
- how it is configured;
- how its availability is validated;
- how it executes OPSX actions;
- how it emits events;
- how it is cancelled;
- how it normalizes errors;
- how its result is validated;
- how the workspace is protected;
- how a new backend is incorporated.

This document is normative for:

- `AgentBackend`;
- `BackendRegistry`;
- `BackendCapabilities`;
- `BackendHealth`;
- `ExecutionService`;
- `OPSXActionExecutor`;
- `CodexCLIBackend`;
- agent configuration;
- Settings and Runner screens;
- backend contract tests.

---

# 2. Definition

An **Agent Backend** is an adapter that allows OPSX TUI to invoke an agent capable of reasoning and executing actions on a project.

Examples:

- Codex CLI;
- Claude Code;
- Gemini CLI;
- another compatible programming agent.

A backend may:

- read files;
- modify files;
- run tools;
- run tests;
- interact with Git;
- respond with events;
- cancel an operation;
- use a configurable model.

## 2.1 It is not an LLM provider

An agent backend is not equivalent to a model provider.

```text
Agent Backend
→ runs an agent with tools

LLM Provider
→ provides access to a model
```

An LLM provider must not be registered as an agent backend if it does not have a compatible tools and execution layer.

---

# 3. Principles

## 3.1 Common interface

The UI and application services must not know specific details such as:

- flag syntax;
- event format;
- binary name;
- authentication variable;
- agent internal structure;
- approval format;
- specific sandbox.

These differences belong to the adapter.

## 3.2 Declarative capabilities

The application must not assume all backends support:

- streaming;
- cancellation;
- model selection;
- sandbox;
- approvals;
- resume;
- structured events;
- network access;
- workspace writing.

Each backend must declare its capabilities.

## 3.3 Security by default

A backend is considered untrusted until it passes:

- configuration validation;
- healthcheck;
- executable verification;
- authentication verification when applicable;
- permission evaluation;
- operation compatibility.

## 3.4 Verifiable result

The backend does not decide on its own that an OpenSpec action was successful.

The result must be validated through:

- filesystem;
- OpenSpec CLI;
- tests;
- Git diff;
- expected artifacts;
- fingerprints;
- defined checks.

## 3.5 Explicit cancellation

Every backend must declare whether it can be cancelled.

If it does not support safe cancellation:

- the UI must report it;
- it must not show a false action;
- application shutdown must warn the user.

---

# 4. Backend identity

Each backend must have a stable identity.

## 4.1 Fields

| Field | Description |
|---|---|
| `id` | Stable internal identifier |
| `type` | Implementation type |
| `display_name` | Displayed name |
| `version` | Adapter version |
| `executable` | Executable, if applicable |
| `provider_name` | Agent or vendor |
| `configuration_scope` | Global or project |
| `enabled` | Configured state |

## 4.2 Initial identifiers

```text
codex-cli
claude-code
gemini-cli
mock-agent
```

## 4.3 Rule

The `id` must not depend on:

- absolute path;
- selected model;
- project name;
- installed version.

---

# 5. Capabilities

## 5.1 Recommended model

```python
class BackendCapabilities(BaseModel):
    model_config = ConfigDict(frozen=True)

    supports_streaming: bool
    supports_cancellation: bool
    supports_model_selection: bool
    supports_approval_modes: bool
    supports_sandbox: bool
    supports_workspace_read: bool
    supports_workspace_write: bool
    supports_network_policy: bool
    supports_structured_events: bool
    supports_resume: bool
    supports_non_interactive_mode: bool
    supports_custom_environment: bool
    supports_action_aliases: bool
```

## 5.2 Minimum capabilities for MVP

A usable backend in the MVP must support:

- non-interactive mode;
- workspace reading;
- workspace writing for modifying actions;
- stdout and stderr capture;
- exit code;
- working directory;
- timeout;
- cancellation or controlled termination.

## 5.3 Compatibility per operation

An operation may declare requirements:

```python
required_capabilities = (
    "supports_workspace_write",
    "supports_non_interactive_mode",
)
```

If capabilities are missing:

- the action is disabled;
- the reason is shown;
- another backend may be suggested.

---

# 6. Health states

## 6.1 Model

```python
class BackendHealthStatus(StrEnum):
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    MISCONFIGURED = "misconfigured"
    AUTHENTICATION_REQUIRED = "authentication-required"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"
```

## 6.2 Healthcheck

The healthcheck must evaluate:

- executable existence;
- execution permission;
- version;
- compatibility;
- authentication;
- configuration;
- non-interactive mode;
- ability to start a safe test;
- OPSX integration availability.

## 6.3 Result

```python
class BackendHealth(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: BackendHealthStatus
    version: str | None
    message: str
    diagnostics: tuple[BackendDiagnostic, ...]
    capabilities: BackendCapabilities
    checked_at: datetime
```

## 6.4 Safe healthcheck

It must not:

- modify the workspace;
- consume a significant amount of tokens;
- run a real OPSX action;
- create files;
- print secrets;
- start an uncontrollable interactive session.

---

# 7. Normalized actions

OPSX TUI will use agent-independent identifiers.

```text
explore
propose
new-change
continue-change
fast-forward
apply
verify
sync
archive
bulk-archive
onboard
```

## 7.1 Translation

Each backend translates the normalized action to its mechanism.

Examples:

```text
normalized action: apply

Codex:
- structured prompt;
- installed skill;
- equivalent command;
- OPSX instruction.

Claude:
- slash command;
- skill;
- equivalent prompt.
```

## 7.2 Rule

The UI must never directly construct backend-specific syntax.

---

# 8. Execution request

## 8.1 Model

```python
class AgentRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    action: OPSXAction
    project_root: Path
    change_name: str | None
    prompt: str
    model: str | None
    approval_mode: ApprovalMode
    sandbox_mode: SandboxMode
    network_policy: NetworkPolicy
    timeout_seconds: int
    environment: dict[str, str]
    allowed_paths: tuple[Path, ...]
    expected_outputs: tuple[ExpectedOutput, ...]
    metadata: dict[str, object]
```

## 8.2 Rules

- `project_root` must be normalized.
- `allowed_paths` must be within policy.
- `environment` must be filtered.
- it must not include persistable secrets;
- the prompt must be safe to display;
- the action must be compatible;
- the model must be validated.

---

# 9. Normalized result

## 9.1 Model

```python
class AgentResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    success: bool
    exit_code: int | None
    cancelled: bool
    timed_out: bool
    summary: str
    changed_files: tuple[Path, ...]
    created_files: tuple[Path, ...]
    deleted_files: tuple[Path, ...]
    warnings: tuple[str, ...]
    backend_error: BackendError | None
    raw_result_reference: str | None
```

## 9.2 Main rule

`success=True` means the backend finished technically according to its contract.

It does not mean the OpenSpec action functionally met its objective.

Functional validation belongs to `ResultValidator`.

---

# 10. Events

## 10.1 Minimum events

```text
backend.healthcheck-started
backend.healthcheck-completed
agent.execution-started
agent.process-spawned
agent.stdout
agent.stderr
agent.message
agent.tool-started
agent.tool-completed
agent.file-created
agent.file-modified
agent.file-deleted
agent.approval-requested
agent.cancellation-requested
agent.cancelled
agent.failed
agent.completed
```

## 10.2 Model

```python
class AgentEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    sequence: int
    timestamp: datetime
    event_type: str
    severity: str
    message: str
    metadata: dict[str, object]
    redacted: bool = False
```

## 10.3 Order

- The sequence must be monotonic.
- The adapter normalizes native events.
- If structured events do not exist, stdout and stderr are converted to events.
- The UI may group visually, but not reorder.

## 10.4 Redaction

Before emitting or persisting:

- tokens;
- API keys;
- credentials;
- headers;
- secrets;
- sensitive values;

must be redacted.

---

# 11. Streaming

## 11.1 Requirement

The backend must emit events while the execution is active.

It must not wait until the end to deliver all output.

## 11.2 Backpressure

The implementation must prevent abundant output from blocking the UI.

Strategies:

- bounded queues;
- batching;
- visual truncation;
- progressive persistence;
- separation between stream and render.

## 11.3 Limits

The console may keep an in-memory window.

History may save:

- full output up to a limit;
- summary;
- external log reference;
- truncation indicator.

---

# 12. Cancellation

## 12.1 Recommended flow

```text
1. user requests cancellation;
2. execution transitions to cancelling;
3. backend attempts cooperative termination;
4. waits grace period;
5. sends stronger signal;
6. marks cancelled or failed;
7. refreshes workspace;
8. validates possible partial changes.
```

## 12.2 Signals

The concrete implementation may use:

- SIGINT;
- SIGTERM;
- kill;
- agent's own mechanism.

## 12.3 Rules

- Cancellation does not imply rollback.
- Partial files must be detected.
- The execution is recorded.
- The UI must warn of possible inconsistency.
- The backend must not claim it undid changes.

---

# 13. Timeout

## 13.1 Configuration

The timeout may be defined:

- globally;
- per project;
- per operation;
- per session.

## 13.2 Behavior

Upon expiration:

- request cancellation;
- mark `timed_out=True`;
- terminate process;
- log;
- refresh;
- run consistency validation.

## 13.3 Suggested initial value

```text
1800 seconds
```

Must be configurable.

---

# 14. Approval modes

## 14.1 Initial enum

```text
never
confirm
on-risk
agent-managed
```

## 14.2 Meaning

### never

Do not request internal agent approvals.

Only allowed for safe operations or controlled environments.

### confirm

Request approval before relevant actions.

### on-risk

Request approval when the agent detects a risky operation.

### agent-managed

Delegate behavior to the agent.

## 14.3 Rule

OPSX TUI confirmation and internal agent approval are different layers.

```text
TUI Confirmation
→ authorizes starting the operation

Agent Approval
→ authorizes an action during execution
```

---

# 15. Sandbox

## 15.1 Initial modes

```text
read-only
workspace-write
unrestricted
backend-default
```

## 15.2 Policy

The default mode for modifying actions will be:

```text
workspace-write
```

When the backend supports it.

## 15.3 Unrestricted

Must require:

- explicit warning;
- confirmation;
- reason;
- logging;
- enabled policy.

## 15.4 Backends without sandbox

If it does not support sandbox:

- it is reported;
- it may be blocked per policy;
- non-existent protection is not simulated.

---

# 16. Network policy

## 16.1 Modes

```text
deny
allow
backend-default
restricted
```

## 16.2 Rule

The application must declare what it can actually control.

If the backend does not allow network control:

- `supports_network_policy=False`;
- the UI shows the limitation;
- the policy must not appear as applied.

---

# 17. Configuration

## 17.1 TOML example

```toml
[backends.codex]
type = "codex-cli"
enabled = true
executable = "codex"
model = "default"
approval_mode = "confirm"
sandbox_mode = "workspace-write"
network_policy = "backend-default"
timeout_seconds = 1800

[backends.codex.environment]
SOME_ALLOWED_VARIABLE = "value"
```

## 17.2 Per-operation configuration

```toml
[operations.explore]
backend = "codex"
model = "reasoning-model"

[operations.apply]
backend = "codex"
model = "coding-model"
approval_mode = "confirm"
sandbox_mode = "workspace-write"
```

## 17.3 Secrets

Must not be stored in TOML.

The following will be used:

- CLI's own authentication;
- keyring;
- environment variables;
- temporary session.

---

# 18. Environment variables

## 18.1 Allow list

The backend must receive an explicit or filtered list.

It must not blindly inherit the entire environment if a restrictive policy exists.

## 18.2 Redaction

Sensitive names are configured via patterns:

```text
*_API_KEY
*_TOKEN
*_SECRET
*_PASSWORD
OPENAI_API_KEY
ANTHROPIC_API_KEY
```

## 18.3 Logging

Logs show:

```text
OPENAI_API_KEY=<redacted>
```

Never the value.

---

# 19. Models

## 19.1 Discovery

A backend may:

- list models;
- accept a configured model;
- use default;
- validate syntax.

## 19.2 Rule

Not all backends can list models.

The following must be differentiated:

```text
supports_model_selection
supports_model_listing
```

## 19.3 Invalid model

Must prevent execution before creating a process when detectable.

---

# 20. Normalized errors

## 20.1 Categories

```text
backend-not-found
backend-disabled
backend-misconfigured
backend-incompatible
backend-version-unsupported
authentication-required
authentication-failed
model-invalid
model-unavailable
action-unsupported
capability-missing
process-start-failed
process-crashed
process-timeout
process-cancelled
output-parse-failed
structured-event-invalid
permission-denied
sandbox-unavailable
network-policy-unavailable
path-policy-violation
result-ambiguous
unknown
```

## 20.2 Model

```python
class BackendError(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str
    message: str
    recoverable: bool
    severity: str
    details: dict[str, object]
    suggested_actions: tuple[str, ...]
```

## 20.3 Exposure

The UI shows:

- message;
- cause;
- recommended action;
- log access.

Full technical details may remain in diagnostics.

---

# 21. Backend registry

## 21.1 BackendRegistry

Responsibilities:

- register;
- resolve by ID;
- validate duplicates;
- query health;
- filter by capability;
- select default;
- suggest alternatives;
- load future plugins.

## 21.2 Selection

Order:

```text
session override
operation configuration
project configuration
global configuration
available default backend
```

## 21.3 Fallback

Backend must not be changed silently.

If the backend is not available:

- it is reported;
- alternatives are suggested;
- the user confirms the change.

---

# 22. Python contract

```python
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class AgentBackend(ABC):
    @property
    @abstractmethod
    def backend_id(self) -> str:
        ...

    @abstractmethod
    async def healthcheck(self) -> BackendHealth:
        ...

    @abstractmethod
    async def capabilities(self) -> BackendCapabilities:
        ...

    @abstractmethod
    async def validate_request(
        self,
        request: AgentRequest,
    ) -> tuple[BackendDiagnostic, ...]:
        ...

    @abstractmethod
    async def execute(
        self,
        request: AgentRequest,
    ) -> AsyncIterator[AgentEvent]:
        ...

    @abstractmethod
    async def cancel(
        self,
        execution_id: UUID,
    ) -> None:
        ...

    @abstractmethod
    async def collect_result(
        self,
        execution_id: UUID,
    ) -> AgentResult:
        ...
```

## 22.1 Alternative

May be implemented via `Protocol` if it facilitates testing.

The concrete decision must maintain the same semantic contract.

---

# 23. Codex CLI Backend

## 23.1 Role

It will be the first official MVP backend.

## 23.2 Responsibilities

- detect `codex`;
- query version;
- validate authentication;
- translate OPSX actions;
- select model;
- configure sandbox;
- configure approvals;
- execute non-interactively;
- emit events;
- cancel;
- capture modified files;
- normalize errors.

## 23.3 Configuration

```toml
[backends.codex]
type = "codex-cli"
executable = "codex"
model = "default"
approval_mode = "confirm"
sandbox_mode = "workspace-write"
timeout_seconds = 1800
```

## 23.4 Non-responsibilities

It must not:

- infer lifecycle;
- decide archive;
- modify SQLite;
- render output;
- store credentials;
- select project;
- execute visual confirmations.

---

# 24. Mock Backend

## 24.1 Purpose

A simulated backend must exist for:

- development;
- tests;
- demos;
- controlled errors;
- streaming;
- cancellation;
- timeout;
- simulated files.

## 24.2 Scenarios

- success;
- failure;
- cancellation;
- timeout;
- malformed event;
- abundant output;
- external file;
- authentication required;
- invalid model.

---

# 25. Post-execution functional validation

After `AgentResult`, `ExecutionService` must invoke `ResultValidator`.

## 25.1 Example

```text
AgentResult:
success = true
exit_code = 0

ResultValidator:
proposal.md does not exist

Final result:
technical_success = true
functional_success = false
```

## 25.2 Rule

The backend must not modify the lifecycle directly.

---

# 26. Git integration

Before a modifying operation:

- inspect Git;
- show working tree;
- apply policy;
- offer checkpoint;
- log current commit.

After:

- detect diff;
- associate files;
- compare;
- validate external changes.

The backend may use Git internally, but OPSX TUI must inspect the result independently.

---

# 27. Concurrency

## 27.1 Initial rule

- One modifying execution per workspace.
- Multiple concurrent reads.
- A backend may run on different projects.
- A change cannot have two simultaneous applies.
- Healthchecks may run in parallel with limits.

## 27.2 Operational lock

The lock belongs to `ExecutionService`, not the backend.

---

# 28. Persistence

The following is persisted:

- backend ID;
- version;
- model;
- capabilities;
- non-sensitive configuration;
- summarized healthcheck;
- execution;
- events;
- result.

The following is not persisted:

- tokens;
- keys;
- handles;
- processes;
- full environment;
- full sensitive prompts without policy.

---

# 29. Observability

Every execution must log:

- backend;
- version;
- model;
- action;
- cwd;
- sandbox;
- approval mode;
- network policy;
- timeout;
- start;
- end;
- exit code;
- cancellation;
- affected files;
- error;
- functional validation.

---

# 30. Contract tests

Every backend must pass the same suite.

## 30.1 Healthcheck

- available;
- not found;
- invalid version;
- authentication required;
- incompatible.

## 30.2 Execution

- stdout;
- stderr;
- events;
- exit code;
- cwd;
- filtered environment;
- timeout;
- cancellation;
- spawn error.

## 30.3 Security

- no shell;
- valid path;
- external path;
- redacted secrets;
- unsupported sandbox;
- unsupported network policy.

## 30.4 Result

- technical success;
- technical failure;
- ambiguous result;
- created files;
- deleted files;
- invalid event.

## 30.5 Compatibility

Contract tests must not depend on the UI.

---

# 31. Recommended fixtures

```text
tests/fixtures/backends/
├── codex-available/
├── codex-not-found/
├── codex-auth-required/
├── codex-incompatible/
├── successful-apply/
├── failed-apply/
├── cancelled-run/
├── timeout-run/
├── noisy-output/
├── malformed-events/
└── external-path-write/
```

---

# 32. Invariants

1. Every backend declares capabilities.
2. No backend is used without a valid healthcheck or explicit policy.
3. The UI does not construct specific commands.
4. The UI does not run processes directly.
5. Every event has a sequence.
6. Every secret is redacted before persisting.
7. Cancellation does not imply rollback.
8. Exit code 0 does not imply functional success.
9. A backend fallback is never silent.
10. A backend without sandbox does not appear to have one.
11. A backend without cancellation does not show false cancellation.
12. The backend does not calculate lifecycle.
13. The backend does not write history directly.
14. Models are validated before execution when possible.
15. Allowed paths are validated before creating the process.

---

# 33. Constraints for the implementing agent

The agent must not:

- couple the UI to Codex;
- use `shell=True`;
- assume capabilities;
- invent structured events;
- store credentials;
- inherit the entire environment without policy;
- silently select another backend;
- hide that a sandbox is not available;
- mark the change as completed;
- calculate lifecycle inside the adapter;
- mix backend and provider;
- duplicate the runner per agent;
- persist handles;
- ignore cancellations;
- block the UI;
- use stdout text as sole functional validation.

---

# 34. Acceptance criteria

The contract is considered correctly implemented when:

1. A common interface exists.
2. Codex CLI works through the contract.
3. Mock Backend exists.
4. The UI does not know Codex flags.
5. The backend declares capabilities.
6. Healthcheck distinguishes errors.
7. Streaming does not block.
8. Cancellation works.
9. Timeout works.
10. Secrets are redacted.
11. Configuration is hierarchical.
12. The model may vary per operation.
13. The sandbox is correctly shown.
14. Errors are normalized.
15. Contract tests pass.

---

# 35. Summary

The architecture must separate:

```text
OPSX Action
    ↓
ExecutionService
    ↓
Common AgentBackend
    ↓
Specific Adapter
    ↓
Real Agent
```

The main rule is:

```text
Backends may be different.
The observable behavior of OPSX TUI must be consistent.
```
