# Architecture Decision Records — OPSX TUI

## 1. Purpose

This document defines the **Architecture Decision Records (ADR)** system for **OPSX TUI** and records the initial architectural decisions of the project.

Its goal is to ensure that relevant decisions:

- are documented;
- have context;
- indicate alternatives;
- make consequences explicit;
- can be reviewed;
- are not accidentally reverted;
- remain linked to product evolution.

This document is normative for:

- implementing agents;
- reviewers;
- OpenSpec changes;
- technical design;
- dependency additions;
- structural refactors;
- security decisions;
- compatibility decisions;
- integration decisions.

---

# 2. What is an ADR

An ADR is a brief, permanent record of a relevant technical decision.

It must answer:

```text
What problem existed?
What decision was made?
What alternatives were considered?
What are the consequences?
```

An ADR is not:

- a task;
- a functional spec;
- a temporary note;
- a code comment;
- an informal justification;
- a replacement for OpenSpec.

---

# 3. When to create an ADR

An ADR must be created when a decision:

- affects multiple layers;
- conditions future implementations;
- introduces a major dependency;
- modifies security;
- defines persistence;
- defines compatibility;
- changes integration with OpenSpec;
- creates a public contract;
- is difficult to reverse;
- replaces a previous decision;
- resolves a significant disagreement.

## 3.1 Does not require an ADR

No ADR is required for:

- renaming a variable;
- reorganizing minor tests;
- fixing a local bug;
- adjusting TCSS styles;
- adding a trivial internal function;
- changing a message;
- fully reversible and contained decisions.

---

# 4. Location

ADRs must be stored in:

```text
docs/adr/
```

Format:

```text
NNNN-kebab-case-title.md
```

Examples:

```text
0001-use-textual.md
0002-support-python-311.md
0003-use-pydantic.md
```

---

# 5. ADR states

## Proposed

Proposed decision, not yet approved.

## Accepted

Current decision.

## Deprecated

Historically valid decision, but no longer recommended.

## Superseded

Replaced by another ADR.

## Rejected

Evaluated and discarded.

## Experimental

Temporarily accepted under evaluation.

---

# 6. Template

```markdown
# ADR-NNNN: Title

## Status

Accepted

## Date

YYYY-MM-DD

## Context

Problem description.

## Decision

Adopted decision.

## Alternatives considered

### Alternative A

Description.

### Alternative B

Description.

## Consequences

### Positive

- ...

### Negative

- ...

### Risks

- ...

## Impact

- Affected layers.
- Affected specs.
- Migrations.
- Compatibility.

## Review

Conditions that would justify reviewing the decision.
```

---

# 7. Governance

## 7.1 Authority

A decision may be proposed from:

- an OpenSpec change;
- technical review;
- security finding;
- refactor;
- incompatibility;
- agent.

## 7.2 Approval

To accept an ADR there must be:

- sufficient context;
- alternatives;
- consequences;
- human review;
- consistency with specs.

## 7.3 Change

An accepted ADR must not be edited to hide history.

One must:

1. create a new ADR;
2. mark the previous one as superseded;
3. link both.

## 7.4 Relationship with OpenSpec

Specs describe behavior.

ADRs describe technical decisions.

Example:

```text
Spec:
The system SHALL execute processes without blocking the UI.

ADR:
asyncio will be used as the runtime.
```

---

# 8. Initial decision index

| ADR | Title | Status |
|---:|---|---|
| 0001 | Use Textual as the only TUI framework | Accepted |
| 0002 | Support Python 3.11 as minimum | Accepted |
| 0003 | Use Pydantic 2 as the main model | Accepted |
| 0004 | Adopt lightweight hexagonal architecture | Accepted |
| 0005 | Use asyncio for concurrency | Accepted |
| 0006 | Use TOML for configuration | Accepted |
| 0007 | Use SQLite for operational history | Accepted |
| 0008 | Keep OpenSpec as source of truth | Accepted |
| 0009 | Separate OpenSpec CLI from OPSX actions | Accepted |
| 0010 | Prohibit shell execution | Accepted |
| 0011 | Use keyring or environment for secrets | Accepted |
| 0012 | Use immutable snapshots | Accepted |
| 0013 | Model backends by capabilities | Accepted |
| 0014 | Validate results functionally | Accepted |
| 0015 | Prioritize degraded read mode | Accepted |

---

# ADR-0001: Use Textual as the only TUI framework

## Status

Accepted

## Date

2026-07-27

## Context

OPSX TUI requires:

- complex layouts;
- keyboard navigation;
- widgets;
- async;
- styles;
- modals;
- testing.

Combining TUI frameworks would increase complexity.

## Decision

Textual will be the sole main UI framework.

Rich will be used through Textual where applicable.

## Alternatives considered

### urwid

Mature, but less aligned with the desired reactive architecture.

### prompt_toolkit

Excellent for prompts, less suitable for a full dashboard.

### raw curses

Too low level.

### blessed

Insufficient as a main framework.

## Consequences

### Positive

- single event model;
- declarative layouts;
- TCSS;
- integrated testing;
- async compatible.

### Negative

- strong dependency on Textual;
- API changes may affect multiple visual layers.

### Risks

- coupling business logic to widgets.

## Mitigation

The UI will consume services and view models.

---

# ADR-0002: Support Python 3.11 as minimum

## Status

Accepted

## Date

2026-07-27

## Context

The development environment may use Python 3.14, but the product must be compatible with a broader base.

Python 3.11 offers:

- TaskGroup;
- ExceptionGroup;
- tomllib;
- good performance;
- stable ecosystem.

## Decision

```text
Minimum Python: 3.11
Target versions: 3.11, 3.12, 3.13 and 3.14
```

## Alternatives considered

### Python 3.12 minimum

Reduces compatibility.

### Python 3.14 minimum

Too restrictive.

### Python 3.10 minimum

Does not provide enough value compared to the required modern APIs.

## Consequences

### Positive

- reasonable compatibility;
- modern async APIs;
- broad support.

### Negative

- cannot use 3.12+ exclusive features without fallback.

---

# ADR-0003: Use Pydantic 2 as the main model

## Status

Accepted

## Date

2026-07-27

## Context

The system needs:

- validation;
- serialization;
- configuration;
- contracts;
- events;
- persistence;
- immutable models.

## Decision

Pydantic 2 will be the main system for domain models, configuration, and inter-layer contracts.

## Alternatives considered

### dataclasses

Lighter, but require additional validation.

### attrs

Powerful, but adds another conceptual dependency.

### TypedDict

Insufficient for runtime validation.

## Consequences

### Positive

- uniform validation;
- serialization;
- schemas;
- integration with configuration.

### Negative

- runtime cost;
- discipline needed to avoid modeling ephemeral objects unnecessarily.

---

# ADR-0004: Adopt lightweight hexagonal architecture

## Status

Accepted

## Date

2026-07-27

## Context

The TUI must be testable without filesystem, CLI, Git, or real agents.

## Decision

The following will be separated:

```text
domain
application
infrastructure
presentation
```

Via ports and adapters.

## Alternatives considered

### Simple technical module architecture

Lower initial complexity, but greater coupling.

### Strict Clean Architecture

Excessive for the initial size.

### Traditional MVC

Does not represent integrations and processes well.

## Consequences

### Positive

- testability;
- interchangeable adapters;
- decoupled UI.

### Negative

- more contracts;
- risk of over-architecture.

## Constraint

The architecture will be lightweight, without artificial layers.

---

# ADR-0005: Use asyncio for concurrency

## Status

Accepted

## Date

2026-07-27

## Context

The application must:

- watch files;
- run processes;
- stream output;
- cancel;
- keep the UI responsive.

## Decision

`asyncio` will be used as the runtime.

Textual will operate on the same async model.

## Alternatives considered

### Trio

Excellent structured concurrency, but introduces another runtime.

### AnyIO

Adds abstraction without initial need.

### Threads

Useful for specific blocking calls, not as a central model.

## Consequences

### Positive

- standard;
- async subprocesses;
- TaskGroup;
- Textual integration.

### Negative

- discipline in cancellation;
- care with blocking calls.

---

# ADR-0006: Use TOML for configuration

## Status

Accepted

## Date

2026-07-27

## Context

Configuration must be:

- readable;
- versionable;
- structured;
- compatible with standard Python.

## Decision

Configuration will be stored in TOML.

Reading via `tomllib`.

Writing via a specific library.

## Alternatives considered

### YAML

More flexible, but more complex and prone to ambiguity.

### JSON

Less friendly for manual editing.

### INI

Insufficient for complex structures.

## Consequences

### Positive

- readable;
- modern standard;
- good Python integration.

### Negative

- writing not included in stdlib.

---

# ADR-0007: Use SQLite for operational history

## Status

Accepted

## Date

2026-07-27

## Context

OPSX TUI needs to persist:

- executions;
- events;
- results;
- affected files;
- recovery;
- retention.

## Decision

SQLite will be the local operational persistence.

## Alternatives considered

### JSON per execution

Simple, but difficult to query and retain.

### log files only

Insufficient for relationships and recovery.

### PostgreSQL

Excessive for a local application.

## Consequences

### Positive

- transactions;
- queries;
- portable;
- local.

### Negative

- migrations;
- concurrency must be managed.

---

# ADR-0008: Keep OpenSpec as source of truth

## Status

Accepted

## Date

2026-07-27

## Context

Kanban and persistence could duplicate methodological state.

## Decision

OpenSpec will be the authoritative source for:

- specs;
- changes;
- tasks;
- archive;
- artifacts.

OPSX TUI will store only operational data.

## Alternatives considered

### Persist Kanban state

Facilitates UI, but creates inconsistencies.

### Duplicate tasks in SQLite

Improves queries, but breaks authority.

## Consequences

### Positive

- consistency;
- interoperability;
- less lock-in.

### Negative

- recomputation;
- parsing;
- dependency on structure.

---

# ADR-0009: Separate OpenSpec CLI from OPSX actions

## Status

Accepted

## Date

2026-07-27

## Context

The CLI and agent actions are different surfaces.

## Decision

They will be modeled as different executors:

```text
OpenSpecCLIAdapter
OPSXActionExecutor
```

## Alternatives considered

### A single CommandRunner

Hides important differences.

### Treating slash commands as shell

Incorrect and risky.

## Consequences

### Positive

- correct semantics;
- adaptability;
- security.

### Negative

- more complex catalog.

---

# ADR-0010: Prohibit shell execution

## Status

Accepted

## Date

2026-07-27

## Context

Dynamic command construction generates injection risk.

## Decision

The following is prohibited:

```text
shell=True
create_subprocess_shell
os.system
```

The following will be used:

```text
asyncio.create_subprocess_exec
```

## Alternatives considered

### Shell with escaping

Difficult to guarantee and platform-dependent.

## Consequences

### Positive

- reduces injection;
- explicit arguments.

### Negative

- pipelines require explicit implementation.

---

# ADR-0011: Use keyring or environment for secrets

## Status

Accepted

## Date

2026-07-27

## Context

Providers and agents may require credentials.

## Decision

Secrets will be obtained via:

- keyring;
- environment variables;
- agent's own authentication.

They will not be stored in TOML or SQLite.

## Alternatives considered

### Custom encrypted config

Complex and error-prone.

### Plain text

Unacceptable.

## Consequences

### Positive

- less exposure;
- system integration.

### Negative

- platform differences.

---

# ADR-0012: Use immutable snapshots

## Status

Accepted

## Date

2026-07-27

## Context

The workspace changes while the UI represents it.

## Decision

Reads will produce immutable Pydantic snapshots.

## Alternatives considered

### Shared mutable objects

Simpler, but risky with async.

### Global state

Difficult to test.

## Consequences

### Positive

- determinism;
- comparison;
- reactivity;
- concurrent safety.

### Negative

- increased object creation.

---

# ADR-0013: Model backends by capabilities

## Status

Accepted

## Date

2026-07-27

## Context

Agents differ in functions.

## Decision

Each backend will declare `BackendCapabilities`.

Operations will require capabilities.

## Alternatives considered

### Rigid interface with assumed support

Fails with incomplete backends.

### Name-based conditionals

Coupling.

## Consequences

### Positive

- extensibility;
- precise UI;
- compatibility.

### Negative

- more validations.

---

# ADR-0014: Validate results functionally

## Status

Accepted

## Date

2026-07-27

## Context

A process may terminate with exit code 0 without fulfilling the action.

## Decision

The following will be separated:

```text
technical_success
functional_success
```

Validation will use evidence.

## Alternatives considered

### Trusting stdout

Unreliable.

### Trusting only exit code

Insufficient.

## Consequences

### Positive

- reliable results;
- better lifecycle.

### Negative

- more logic per operation.

---

# ADR-0015: Prioritize degraded read mode

## Status

Accepted

## Date

2026-07-27

## Context

The user may not have:

- OpenSpec CLI;
- agent;
- Git;
- keyring.

## Decision

OPSX TUI will continue to function in read mode as long as it can interpret the filesystem.

## Alternatives considered

### Block startup

Reduces usefulness.

### Automatically install dependencies

Risky.

## Consequences

### Positive

- immediate usefulness;
- diagnostics;
- less dependency.

### Negative

- more partial states.

---

# 9. Relationship with future changes

A change that modifies a decision must include:

```text
ADR Impact:
- creates ADR;
- supersedes ADR;
- not applicable.
```

Example in `proposal.md`:

```markdown
## Architectural decisions

This change supersedes ADR-0007.
```

---

# 10. ADR Review

An ADR must be reviewed when:

- OpenSpec changes;
- Textual changes;
- a remote server is added;
- multi-user is added;
- distributed execution is added;
- a Python incompatibility exists;
- a security risk changes;
- a dependency becomes obsolete;
- the decision causes repeated problems.

---

# 11. ADR quality criteria

A valid ADR must:

1. have context;
2. have a decision;
3. have alternatives;
4. have consequences;
5. have status;
6. have a date;
7. not hide risks;
8. be concise;
9. link related ADRs;
10. indicate review conditions.

---

# 12. Constraints for the implementing agent

The agent must not:

- silently revert an accepted ADR;
- edit history to hide a decision;
- create ADRs for trivial details;
- introduce a major dependency without an ADR;
- change architecture without recording the decision;
- mark as Accepted without review;
- delete superseded ADRs;
- confuse ADR with spec;
- use an ADR to replace functional requirements;
- ignore negative consequences.

---

# 13. Possible upcoming ADRs

Must not be created yet unless there is a real need:

```text
0016 - plugin strategy
0017 - OpenAI-compatible provider
0018 - worktrees per change
0019 - Windows support
0020 - log persistence format
0021 - SQLite migration strategy
0022 - embedded editor
0023 - remote execution
```

---

# 14. Recommended structure

```text
docs/
├── 09-architecture-decision-records.md
└── adr/
    ├── 0001-use-textual.md
    ├── 0002-support-python-311.md
    ├── 0003-use-pydantic.md
    ├── 0004-lightweight-hexagonal-architecture.md
    ├── 0005-use-asyncio.md
    ├── 0006-use-toml-configuration.md
    ├── 0007-use-sqlite-for-history.md
    ├── 0008-openspec-source-of-truth.md
    ├── 0009-separate-cli-and-opsx-actions.md
    ├── 0010-prohibit-shell-execution.md
    ├── 0011-secure-secret-storage.md
    ├── 0012-immutable-snapshots.md
    ├── 0013-capability-based-backends.md
    ├── 0014-functional-result-validation.md
    └── 0015-read-only-degraded-mode.md
```

The consolidated document may be kept as an index, while individual ADRs are created when implementation begins.

---

# 15. Summary

ADRs must answer:

```text
Why does this architecture exist?
Why was another option not chosen?
What cost are we accepting?
When should we review it?
```

The main rule is:

```text
An important decision must not live only in the agent's memory.
```
