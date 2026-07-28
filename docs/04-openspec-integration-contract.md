# OpenSpec Integration Contract — OPSX TUI

## 1. Purpose

This document defines how **OPSX TUI** integrates with OpenSpec.

It establishes:

- what information is obtained from the filesystem;
- what information is obtained through the official CLI;
- which operations are internal;
- which operations correspond to the `openspec` CLI;
- which operations must be executed through an agent;
- which files the application may read or modify;
- how versions and capabilities are detected;
- how the result of an operation is validated;
- how errors, incompatibilities, and future changes are handled;
- what the security boundaries are.

This contract is normative for adapters, application services, command catalog, and screens that interact with OpenSpec.

---

# 2. Official OpenSpec context

OpenSpec has two different operation surfaces.

## 2.1 Terminal CLI

The CLI runs through the program:

```bash
openspec
```

It is used for tasks such as:

- initializing a project;
- updating the integration;
- listing changes;
- inspecting status;
- validating;
- opening supported views or dashboards;
- managing changes through available official commands;
- querying structured information when the version allows it.

Conceptual examples:

```bash
openspec init
openspec list
openspec status
openspec view
openspec validate
```

The exact availability of commands and options depends on the installed version.

## 2.2 OPSX actions in the agent

OPSX actions are executed in the programming agent's chat or interface, not directly in a conventional shell.

Examples:

```text
/opsx:explore
/opsx:propose
/opsx:new
/opsx:continue
/opsx:ff
/opsx:apply
/opsx:verify
/opsx:sync
/opsx:archive
```

The visible syntax may vary depending on the tool:

```text
/opsx:propose
/opsx-propose
openspec-propose
```

The methodological intent is equivalent, but each agent may install or expose actions differently.

## 2.3 Fundamental rule

```text
OpenSpec CLI ≠ agent OPSX action
```

OPSX TUI must model both surfaces separately.

It must not be assumed that:

```bash
openspec apply
```

is equivalent to:

```text
/opsx:apply
```

unless the installed official version explicitly declares a CLI command with that behavior.

---

# 3. Integration goals

The integration must enable:

1. Detecting whether a project uses OpenSpec.
2. Identifying the installed version.
3. Reading the workspace without modifying it.
4. Querying structured information when the CLI supports it.
5. Displaying specs and changes even if the CLI is not installed.
6. Executing supported local commands.
7. Delegating OPSX actions to an agent backend.
8. Validating results through evidence.
9. Adapting to version differences.
10. Degrading functionality without losing read mode.
11. Avoiding dependence on undocumented internal details.
12. Keeping OpenSpec as the methodological source of truth.

---

# 4. Information sources

OPSX TUI will use four information sources.

## 4.1 Filesystem

Primary source for representing persistent content.

Used for:

- locating the `openspec/` folder;
- reading configuration;
- listing specs;
- listing changes;
- reading Markdown;
- reading tasks;
- detecting archived changes;
- watching modifications;
- calculating fingerprints;
- showing paths;
- detecting missing artifacts.

## 4.2 OpenSpec CLI

Preferred source for:

- installed version;
- declared capabilities;
- structured listings;
- official status;
- validations;
- available management operations;
- configuration diagnostics;
- compatibility;
- commands that OpenSpec implements canonically.

## 4.3 Agent backend

Execution source for agent-based methodological actions.

Used for:

- exploring;
- proposing;
- creating changes;
- continuing artifacts;
- generating missing artifacts;
- applying;
- verifying;
- synchronizing;
- archiving when it corresponds to the agent workflow.

## 4.4 OPSX TUI operational state

Local source for:

- history;
- configuration;
- executions;
- events;
- filters;
- auxiliary metadata;
- recorded verifications;
- backends;
- models;
- security policies.

It cannot replace OpenSpec content.

---

# 5. Minimum recognized structure

OPSX TUI will recognize as an OpenSpec candidate a root containing:

```text
<project>/
└── openspec/
```

The expected structure may include:

```text
openspec/
├── config.yaml
├── specs/
│   └── <capability>/
│       └── spec.md
└── changes/
    ├── <active-change>/
    │   ├── proposal.md
    │   ├── design.md
    │   ├── tasks.md
    │   └── specs/
    │       └── <capability>/
    │           └── spec.md
    └── archive/
        └── <archived-change>/
```

The absence of any of these elements must not automatically cause the project to be invisible.

## 5.1 Candidate

`openspec/` exists, but the structure has not been fully validated.

## 5.2 Valid project

Meets the minimum structure compatible with the known version or can be safely interpreted.

## 5.3 Partially valid project

Can be read, but has:

- missing configuration;
- incomplete folders;
- malformed artifacts;
- partial changes;
- minor incompatibility;
- missing CLI.

## 5.4 Invalid project

Cannot be represented without risk or critical ambiguity.

Examples:

- insufficient permissions;
- untrusted external paths;
- structure impossible to interpret;
- critically corrupt configuration;
- root outside the requested project.

---

# 6. Root detection

Detection will follow this order:

```text
1. --project argument
2. OPSX_TUI_PROJECT variable
3. upward search from cwd
4. Git root
5. recent selected project
6. interactive selector
```

## 6.1 Upward search

Starting from the current directory:

```text
/project/src/module
/project/src
/project
/
```

At each level, the existence of:

```text
openspec/
```

is checked.

The search ends when the filesystem root is reached.

## 6.2 Git root

The Git root is only used as an additional candidate.

It will not be assumed:

```text
Git root = OpenSpec project root
```

## 6.3 Prohibitions

OPSX TUI must not:

- search recursively throughout the home directory;
- initialize automatically;
- silently select a recent project;
- follow symlinks outside the defined policy;
- change the process global working directory without control.

---

# 7. Direct filesystem reading

## 7.1 Read elements

OPSX TUI may directly read:

```text
openspec/config.yaml
openspec/specs/**
openspec/changes/**
openspec/changes/archive/**
```

It may also read:

- timestamps;
- size;
- permissions;
- hashes;
- relative paths;
- Markdown content;
- checkboxes;
- folder names.

## 7.2 Interpreted elements

It may interpret:

- spec title;
- requirements;
- scenarios;
- existing artifacts;
- tasks;
- progress;
- delta operations;
- archived status;
- name-based relationships;
- structure errors.

## 7.3 Tolerant reading

The parser must:

- preserve original content;
- produce partial diagnostics;
- not delete unknown content;
- not require all files to be valid;
- allow displaying malformed files;
- avoid blocking the entire workspace due to a single change.

## 7.4 On-demand loading

For large projects:

- the catalog may load metadata first;
- full content may be loaded when opening an artifact;
- hashes may be calculated selectively;
- the watcher must refresh only affected entities.

---

# 8. Using the OpenSpec CLI

## 8.1 Detection

The executable will be searched in this order:

```text
1. CLI-configured path
2. project configuration
3. global configuration
4. PATH
```

Executables will not be downloaded automatically.

## 8.2 Healthcheck

The adapter must check:

- executable found;
- execution permission;
- version;
- valid output;
- working directory;
- compatibility;
- detectable commands.

## 8.3 Version

The version will be represented as a structured value when possible.

Example:

```python
class OpenSpecVersion(BaseModel):
    raw: str
    major: int | None
    minor: int | None
    patch: int | None
    prerelease: str | None
```

If the output cannot be parsed:

- `raw` is preserved;
- compatibility is marked as unknown;
- only safe operations are enabled.

## 8.4 Invocation

The following will be used:

```python
asyncio.create_subprocess_exec(
    executable,
    *arguments,
    cwd=project_root,
)
```

The following is prohibited:

```python
shell=True
create_subprocess_shell
os.system
```

unless a future formal exception is documented through an ADR with additional controls.

## 8.5 Structured outputs

When the CLI offers JSON or another structured format:

- it will be preferred over text parsing;
- it will be validated with Pydantic;
- the raw output will be preserved for diagnostics;
- an unknown schema will produce controlled incompatibility.

## 8.6 Human output

Human-readable text may be displayed, but must not be used as the sole source of critical rules if a structured output exists.

---

# 9. Initial operations catalog

The actual catalog must be generated according to capabilities and version.

| Operation | Preferred executor | Read/write | Confirmation |
|---|---|---|---|
| Detect project | Internal | Read | No |
| Read workspace | Internal | Read | No |
| Watch workspace | Internal | Read | No |
| Query version | CLI | Read | No |
| List changes | CLI or filesystem | Read | No |
| Query status | CLI preferred | Read | No |
| Validate | CLI preferred | Read | No |
| Initialize | CLI | Write | Yes |
| Update integration | CLI | Write | Yes |
| Explore | Agent | May write notes | Per preview |
| Propose | Agent | Write | Yes |
| New change | Agent | Write | Yes |
| Continue | Agent | Write | Yes |
| Fast-forward | Agent | Write | Yes |
| Apply | Agent | Code write | Yes |
| Verify | Agent and/or CLI | Read or minor write | Configurable |
| Sync | Agent or supported CLI | Write | Yes |
| Archive | Official CLI or agent | Write | Yes |
| Open official view | CLI | Read | No |

## 9.1 Executor rule

The executor is determined by:

```text
official version capability
+ operation type
+ configured backend
+ security policy
```

Not by a rigid list embedded in widgets.

---

# 10. OPSX actions via agent

## 10.1 Invocation form

OPSX TUI must not assume that all agents literally accept:

```text
/opsx:apply
```

Each backend must declare how it invokes an action.

Possible examples:

- slash command;
- skill name;
- structured prompt;
- agent CLI command;
- instruction file;
- API with tools.

## 10.2 Normalized action

The domain will use neutral identifiers:

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

The adapter translates to the agent-specific format.

## 10.3 Minimum context

A request to the agent must include:

- project root;
- target change;
- action;
- user objective;
- constraints;
- permissions;
- relevant artifacts;
- definition of done;
- no scope creep instructions;
- closing report format.

## 10.4 Preview

Before executing, the TUI must show:

- normalized action;
- backend;
- model;
- change;
- permissions;
- prompt or summary;
- expected files;
- risks;
- required confirmation.

---

# 11. Result validation

OPSX TUI must not accept a phrase like:

```text
The task is done.
```

as sufficient evidence.

The result must be validated.

## 11.1 Possible evidence

- exit code;
- artifact created;
- artifact modified;
- checkbox change;
- successful OpenSpec command;
- OpenSpec validation;
- tests;
- lint;
- type checking;
- Git diff;
- fingerprint;
- absence of critical errors;
- expected structure.

## 11.2 Validation per operation

### Propose

Check, according to workflow:

- change created;
- proposal available;
- delta specs available when applicable;
- design available when applicable;
- tasks available when applicable;
- valid structure;
- diagnostics.

### Apply

Check:

- tasks modified;
- code files modified;
- tests run when the change requires it;
- Git status;
- errors;
- intact artifacts;
- pending tasks.

### Verify

Check:

- checks executed;
- findings;
- result;
- input fingerprint;
- requirement coverage;
- complete tasks;
- verification log.

### Archive

Check:

- change is no longer active;
- appears in archive;
- canonical specs updated when applicable;
- valid structure;
- no duplication exists;
- official operation completed successfully.

## 11.3 Ambiguous result

If the process terminates correctly, but the evidence does not match:

```text
ExecutionResult.success = false
or
ExecutionResult.success = true with functional_validation = failed
```

The UI must show:

```text
The process finished, but OPSX TUI could not confirm the expected result.
```

---

# 12. Priority between filesystem and CLI

## 12.1 Filesystem as persistent source

The filesystem is the source of visible content:

- Markdown;
- tasks;
- specs;
- changes;
- archive.

## 12.2 CLI as official interpreter

The CLI is preferred for:

- validation;
- structured status;
- versioning;
- compatibility;
- canonical operations.

## 12.3 Discrepancy rule

If filesystem and CLI disagree:

1. filesystem content is preserved;
2. the status returned by CLI is shown;
3. a diagnostic is generated;
4. the discrepancy is not hidden;
5. a modifying operation may be blocked;
6. the user may refresh or run diagnostics.

Example:

```text
Filesystem detects 4 changes.
CLI reports 3 changes.

Result:
- show all 4;
- identify which one the CLI does not recognize;
- mark compatibility or partial structure.
```

---

# 13. Compatibility and evolution

## 13.1 Policy

OPSX TUI will not depend on a single exact version of OpenSpec.

It will use:

- version detection;
- feature detection;
- capability catalog;
- versioned adapters when necessary;
- filesystem fallback;
- explicit diagnostics.

## 13.2 Compatibility levels

### Supported

Version tested in CI or fixtures.

### Compatible

Version not fully tested, but required capabilities detected.

### Partial

Read mode available; some operations disabled.

### Unsupported

The structure or CLI cannot be used safely.

### Unknown

Version or capabilities could not be determined.

## 13.3 Feature detection

Asking or detecting capabilities will be preferred over comparing only version numbers.

Examples:

- does JSON output exist?
- does the `status` command exist?
- does structured validation exist?
- does the archive command exist?
- what options does `--help` declare?
- what skills were installed?

## 13.4 Future changes

Unknown content must:

- be preserved;
- be shown as an unknown artifact;
- generate an informative diagnostic;
- not be deleted;
- not block reading unless there is risk.

---

# 14. Initialization and update

## 14.1 Initialization

`openspec init` modifies the project.

It must require:

- explicit or confirmed path;
- preview;
- confirmation;
- visible Git status;
- compatible executable;
- execution log.

After initializing:

- the project is refreshed;
- created files are detected;
- agent integrations are detected;
- the result is shown.

## 14.2 Update

An update may modify:

- OpenSpec configuration;
- skills;
- slash commands;
- agent integration;
- generated files.

It must require:

- preview;
- current version;
- target version when known;
- visible Git;
- confirmation;
- post diff.

## 14.3 Prohibition

OPSX TUI must never execute init or update automatically when opening a project.

---

# 15. Agent tool integration

## 15.1 Detection

Detection may use:

- executable in PATH;
- configuration;
- folders or files installed by OpenSpec;
- backend healthcheck;
- available commands.

## 15.2 Do not assume full installation

A project may have OpenSpec, but may not have the chosen agent configured.

The UI must differentiate:

```text
OpenSpec available
Codex available
OpenSpec skills for Codex available
Authentication available
```

## 15.3 Action capability

A backend may only execute an action if:

- it is installed;
- it responds to healthcheck;
- it has authentication;
- it declares the capability;
- it recognizes the integration or accepts the equivalent prompt;
- it meets the security policy.

---

# 16. Watcher and consistency

## 16.1 Watched directories

```text
openspec/config.yaml
openspec/specs/**
openspec/changes/**
```

Optionally:

- agent integration files;
- local project configuration;
- code files during an execution.

## 16.2 Debounce

Multiple events must be grouped.

Suggested initial value:

```text
250 to 500 ms
```

Configurable if necessary.

## 16.3 Partial writes

The watcher must avoid reading files while they are being replaced.

Strategies:

- debounce;
- retry;
- size stability check;
- temporary file handling;
- tolerant reading.

## 16.4 During executions

The watcher remains active.

Events may be associated to the execution through:

- time window;
- active process;
- before/after snapshot;
- Git diff;
- hashes;
- expected paths.

---

# 17. Modifying OpenSpec files

## 17.1 General rule

OPSX TUI is not initially a direct OpenSpec editor.

It may only modify files through:

- official commands;
- agent actions;
- explicitly specified internal operations;
- external editing via `$EDITOR`.

## 17.2 Allowed internal operations

In the MVP:

- own local metadata;
- own configuration;
- history;
- filters;
- preferences.

Direct modifications to the following are not included:

- proposal;
- design;
- tasks;
- specs;
- archive.

## 17.3 Future evolution

A future feature to mark tasks or edit OpenSpec metadata will require:

- its own spec;
- format validation;
- atomic write strategy;
- backups or Git;
- confirmation;
- compatibility tests.

---

# 18. Path security

## 18.1 Normalization

Every path must:

- be converted to absolute;
- be resolved according to policy;
- be compared against the root;
- preserve a safe relative representation.

## 18.2 Symlinks

Symlinks must be classified:

- internal to the project;
- explicitly allowed external;
- not allowed external;
- broken.

## 18.3 External writes

An agent may attempt to modify files outside the workspace.

OPSX TUI must:

- detect when possible;
- warn;
- block if policy requires it;
- log;
- not mark the execution as fully validated.

## 18.4 Sensitive files

The policy may identify:

```text
.env
*.pem
*.key
credentials*
secrets*
```

These files:

- are not shown in full;
- are not included in logs;
- generate warnings;
- may block operations.

---

# 19. Normalized errors

## 19.1 Categories

```text
openspec-not-found
openspec-version-unknown
openspec-version-unsupported
workspace-not-found
workspace-invalid
workspace-partial
config-invalid
command-unavailable
command-failed
structured-output-invalid
agent-not-found
agent-not-configured
agent-authentication-failed
agent-action-unsupported
operation-cancelled
operation-timeout
path-outside-workspace
permission-denied
validation-failed
result-ambiguous
unknown
```

## 19.2 Structure

```python
class IntegrationError(BaseModel):
    code: str
    message: str
    severity: str
    recoverable: bool
    details: dict[str, object]
    suggested_actions: tuple[str, ...]
```

## 19.3 Messages

Messages must explain:

- what failed;
- where;
- whether anything was modified;
- what the user can do;
- where to check logs.

They must not expose:

- secrets;
- full variables;
- tokens;
- unsolicited sensitive prompts.

---

# 20. Degraded mode

OPSX TUI must remain useful if components are missing.

## 20.1 Without OpenSpec CLI

Available:

- filesystem detection;
- reading;
- specs;
- changes;
- tasks;
- inferred Kanban;
- search;
- external editor.

Not available:

- official validation;
- CLI commands;
- confirmed compatibility;
- CLI-dependent canonical operations.

## 20.2 Without an agent

Available:

- full reading;
- CLI commands;
- history;
- Git;
- diagnostics.

Not available:

- delegated OPSX actions.

## 20.3 Without Git

Available:

- reading;
- CLI;
- agent per policy;
- history.

Not available:

- Git status;
- checkpoint;
- Git diff;
- some protections.

## 20.4 Without keyring

Options:

- environment variables;
- backend that handles its own authentication;
- temporary session configuration.

Never fallback to plain-text secrets without a later explicit decision.

---

# 21. Observability requirements

Every interaction with OpenSpec must log:

- operation;
- executor;
- version;
- redacted arguments;
- cwd;
- start;
- end;
- exit code;
- error;
- affected files;
- validation;
- compatibility;
- cancellation.

The log must not include:

- API keys;
- tokens;
- full content of sensitive files;
- full environment variables.

---

# 22. Test requirements

## 22.1 Version fixtures

Maintain fixtures representing:

- minimum structure;
- complete project;
- project without config;
- incomplete change;
- archive;
- malformed task;
- valid JSON output;
- unknown JSON output;
- missing CLI;
- incompatible version.

## 22.2 Contract tests

Each adapter must pass common tests:

- healthcheck;
- version;
- cancellation;
- timeout;
- stdout;
- stderr;
- exit code;
- redaction;
- cwd;
- safe arguments.

## 22.3 Discrepancy tests

Cases:

- filesystem and CLI differ;
- change moves during reading;
- archiving occurs during watcher;
- process ends before producing output;
- agent says success without creating artifacts;
- CLI exit 0 with invalid output;
- external symlink;
- partial permissions.

---

# 23. Interface contracts

## 23.1 OpenSpecCLIAdapter

```python
class OpenSpecCLIAdapter(Protocol):
    async def healthcheck(self, project_root: Path) -> OpenSpecHealth:
        ...

    async def version(self) -> OpenSpecVersion:
        ...

    async def capabilities(self) -> OpenSpecCapabilities:
        ...

    async def execute(
        self,
        request: OpenSpecCLIRequest,
    ) -> AsyncIterator[ExecutionEvent]:
        ...
```

## 23.2 OpenSpecWorkspaceReader

```python
class OpenSpecWorkspaceReader(Protocol):
    async def load(
        self,
        project: Project,
    ) -> OpenSpecWorkspace:
        ...
```

## 23.3 OPSXActionExecutor

```python
class OPSXActionExecutor(Protocol):
    async def supports(
        self,
        action: OPSXAction,
    ) -> bool:
        ...

    async def execute(
        self,
        request: OPSXActionRequest,
    ) -> AsyncIterator[ExecutionEvent]:
        ...

    async def cancel(self, execution_id: UUID) -> None:
        ...
```

## 23.4 ResultValidator

```python
class ResultValidator(Protocol):
    async def validate(
        self,
        request: ValidationRequest,
    ) -> FunctionalValidationResult:
        ...
```

---

# 24. Data ownership matrix

| Data | OpenSpec | OPSX TUI | CLI | Agent |
|---|:---:|:---:|:---:|:---:|
| Specs | Authoritative | Reads | Validates | Modifies per action |
| Proposal | Authoritative | Reads | May inspect | Creates/modifies |
| Design | Authoritative | Reads | May inspect | Creates/modifies |
| Tasks | Authoritative | Reads | May validate | Creates/modifies |
| Archive | Authoritative | Reads | Manages if supported | May orchestrate |
| Visual lifecycle | Evidence | Calculates | Provides status | Provides result |
| History | No | Authoritative | No | No |
| Backend config | No | Authoritative | No | Consumes |
| Credentials | No | Secure reference | No | Consumes |
| Logs | No | Authoritative | Produces | Produces |
| Recorded verification | Evidence | Records | Provides checks | Runs checks |
| Git state | No | Reads | No | May modify |

---

# 25. Explicit decisions

1. The filesystem will be sufficient for read mode.
2. The CLI will be preferred for official status and validation.
3. OPSX actions will be modeled as agent actions.
4. A single slash syntax will not be hardcoded.
5. The catalog will adapt by capabilities.
6. The UI will not execute subprocesses directly.
7. `shell=True` will not be used.
8. OpenSpec artifacts will not be edited directly in the MVP.
9. An exit code 0 is not sufficient proof of functional success.
10. Discrepancies will be visible.
11. The absence of CLI will not prevent viewing the project.
12. The absence of an agent will not prevent using OpenSpec in read or CLI mode.
13. Compatibility will be based on version and feature detection.
14. Unknown content will be preserved.
15. OpenSpec will remain the source of truth.

---

# 26. Constraints for the implementing agent

The agent must not:

- treat slash commands as shell commands;
- assume all versions have the same commands;
- parse human text if JSON exists;
- hide discrepancies;
- modify specs directly without a write spec;
- download OpenSpec automatically;
- execute init/update on open;
- assume Git is present;
- block read mode because Codex is missing;
- persist full copies of the workspace in SQLite;
- infer archive only from local history;
- store secrets;
- follow external symlinks without policy;
- declare success based only on the agent's message;
- couple widgets to specific commands;
- omit the preview of modifying operations.

---

# 27. Official reference sources

This contract was prepared considering the official documentation in effect consulted on **July 27, 2026**, in particular:

- official OpenSpec site;
- README of the `Fission-AI/OpenSpec` repository;
- Getting Started guide;
- CLI reference;
- How Commands Work document;
- Commands reference;
- Supported Tools;
- FAQ.

Since OpenSpec evolves, the implementation must verify the version and actual installed capabilities instead of relying solely on this document.

---

# 28. Summary

The integration is organized into three layers:

```text
FILESYSTEM
Persistent and observable content

OPENSPEC CLI
Status, validation, and official operations

AGENT BACKEND
OPSX actions and assisted work
```

OPSX TUI coordinates these layers:

```text
read
→ interpret
→ display
→ validate
→ execute
→ observe
→ verify evidence
→ log
```

The main rule is:

```text
OPSX TUI must never silently guess
what it can read, query, detect, or validate.
```
