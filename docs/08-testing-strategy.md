# Testing Strategy — OPSX TUI

## 1. Purpose

This document defines the testing strategy for **OPSX TUI**.

Its goal is to establish:

- what must be tested;
- at what level it should be tested;
- which tools will be used;
- how adapters will be validated;
- how the TUI will be tested;
- how OpenSpec, Git, agents, and processes will be simulated;
- how errors, security, and compatibility will be covered;
- which fixtures must exist;
- which quality gates must be met before archiving a change.

This document is normative for:

- feature development;
- task definition;
- code review;
- CI;
- `/opsx:verify`;
- contract tests;
- regression tests;
- version publishing.

---

# 2. Quality Objectives

The strategy must ensure that OPSX TUI is:

1. Correct.
2. Deterministic.
3. Secure.
4. Compatible.
5. Observable.
6. Recoverable.
7. Testable without a real terminal.
8. Testable without real agents.
9. Testable without OpenSpec installed.
10. Resilient to incomplete structures.
11. Stable against filesystem changes.
12. Non-blocking.
13. Coherent between domain, application, and infrastructure.
14. Compatible with Python 3.11 through 3.14.
15. Publishable with confidence.

---

# 3. Principles

## 3.1 Testing Pyramid

The majority of coverage should be in unit tests.

```text
          E2E
        Integration
      Contract tests
     Unit tests
```

## 3.2 Boundary Testing

Especially test:

- filesystem;
- CLI;
- subprocesses;
- Git;
- SQLite;
- keyring;
- configuration;
- agents;
- providers;
- events;
- paths.

## 3.3 Pure Domain

Domain rules must be testable without:

- Textual;
- real filesystem;
- processes;
- network;
- SQLite;
- Git;
- OpenSpec CLI;
- Codex CLI.

## 3.4 Reproducible Fixtures

Tests must not depend on a personal project or on an uncontrolled local environment.

## 3.5 No Real Services in CI

By default, CI must not require:

- API keys;
- authenticated Codex;
- paid providers;
- external network;
- remote repositories.

## 3.6 Errors as First-Class Cases

Every feature must include:

- happy path;
- expected error;
- invalid input;
- cancellation;
- timeout;
- partial state;
- recovery.

## 3.7 Minimum Real Compatibility

Python 3.11 must always be tested.

Developing only on Python 3.14 is not sufficient.

---

# 4. Tools

## 4.1 Main Framework

```text
pytest
```

## 4.2 Async

```text
pytest-asyncio
```

## 4.3 Coverage

```text
coverage.py
pytest-cov
```

## 4.4 Property-Based Testing

```text
Hypothesis
```

## 4.5 Mocking

Preferences:

- fakes;
- stubs;
- simulated adapters;
- limited monkeypatch;
- `unittest.mock` where appropriate.

## 4.6 TUI

Textual's testing tools will be used:

- `run_test`;
- pilot;
- simulated events;
- widget queries;
- snapshots where they add value.

## 4.7 Static Quality

```text
Ruff
MyPy
```

## 4.8 Security

Depending on maturity:

```text
Bandit
pip-audit
```

These tools do not replace functional security tests.

---

# 5. Testing Levels

# 5.1 Unit Tests

## Objective

Validate functions, models, and rules in isolation.

## Primary Coverage

- Pydantic models;
- parsers;
- lifecycle;
- progress;
- fingerprints;
- configuration;
- redaction;
- error normalization;
- backend selection;
- command catalog;
- filters;
- path validation;
- policies;
- view models.

## Characteristics

- fast;
- deterministic;
- no real I/O when possible;
- no terminal;
- no external processes.

---

# 5.2 Contract Tests

## Objective

Ensure that all implementations of a contract behave identically.

## Main Contracts

- `WorkspaceReader`;
- `WorkspaceWatcher`;
- `OpenSpecCLIAdapter`;
- `AgentBackend`;
- `ProcessRunner`;
- `ExecutionRepository`;
- `SecretStore`;
- `GitInspector`;
- `ResultValidator`.

## Rule

Each concrete implementation must run the same contractual suite.

Example:

```python
class AgentBackendContract:
    async def test_healthcheck(self, backend):
        ...

    async def test_streaming(self, backend):
        ...

    async def test_cancel(self, backend):
        ...
```

---

# 5.3 Integration Tests

## Objective

Validate interaction between real components.

## Examples

- filesystem + parser;
- SQLite + repository;
- subprocess runner + fake executable;
- Git + temporary repository;
- watcher + temporary files;
- configuration + simulated platformdirs;
- backend + fake process;
- lifecycle + verification repository.

## Rule

They must use temporary, isolated resources.

---

# 5.4 TUI Tests

## Objective

Validate observable behavior of the interface.

## Coverage

- navigation;
- focus;
- shortcuts;
- modals;
- empty states;
- errors;
- refresh;
- card selection;
- detail opening;
- confirmations;
- streaming output;
- cancellation;
- configuration.

## Rule

The TUI must consume fake services.

It must not require OpenSpec nor real agents.

---

# 5.5 End-to-End Tests

## Objective

Validate high-value complete flows.

## Initial Flows

1. Open project.
2. Read workspace.
3. Show Kanban.
4. Open change.
5. Execute simulated local command.
6. Execute simulated OPSX action.
7. Show events.
8. Persist result.
9. Refresh lifecycle.

## Quantity

Few, stable, and focused.

---

# 5.6 Compatibility Tests

## Versions

```text
Python 3.11
Python 3.12
Python 3.13
Python 3.14
```

## Initial Target Platforms

- Linux primary.
- macOS recommended.
- Windows based on effective support.

## Rule

Linux + Python 3.11 is the mandatory minimum gate.

---

# 5.7 Regression Tests

Every fixed bug must add a test that fails before the fix.

---

# 6. Test Directory Organization

```text
tests/
├── unit/
│   ├── domain/
│   ├── application/
│   ├── presentation/
│   └── security/
│
├── contract/
│   ├── workspace_reader/
│   ├── agent_backend/
│   ├── process_runner/
│   ├── repositories/
│   └── git_inspector/
│
├── integration/
│   ├── filesystem/
│   ├── openspec_cli/
│   ├── sqlite/
│   ├── git/
│   ├── watchers/
│   └── processes/
│
├── tui/
│   ├── test_board.py
│   ├── test_specs.py
│   ├── test_change_detail.py
│   ├── test_runner.py
│   └── test_settings.py
│
├── e2e/
│   └── test_primary_flows.py
│
├── fixtures/
│   ├── openspec/
│   ├── lifecycle/
│   ├── backends/
│   ├── git/
│   └── config/
│
└── conftest.py
```

---

# 7. OpenSpec Fixtures

## 7.1 Minimum Structures

```text
tests/fixtures/openspec/
├── empty-project/
├── valid-project/
├── project-without-config/
├── malformed-config/
├── no-specs/
├── no-changes/
├── active-change/
├── incomplete-change/
├── applying-change/
├── verified-change/
├── archived-change/
├── malformed-tasks/
├── unknown-artifact/
├── symlink-internal/
└── symlink-external/
```

## 7.2 `valid-project` Fixture

Must contain:

- config;
- at least two specs;
- two changes;
- proposal;
- design;
- tasks;
- delta specs;
- archive.

## 7.3 Incomplete Fixture

Must contain realistic combinations:

- proposal without design;
- tasks without proposal;
- delta spec without target;
- simulated unreadable file;
- unknown Markdown.

## 7.4 Rule

Fixtures must be small and readable.

They must not contain real sensitive data.

---

# 8. Lifecycle Fixtures

```text
tests/fixtures/lifecycle/
├── draft-empty/
├── draft-invalid-proposal/
├── planning-missing-design/
├── planning-empty-tasks/
├── ready/
├── applying/
├── verification-not-run/
├── verification-failed/
├── ready-to-archive/
├── stale-verification/
├── blocked-manual/
├── blocked-git/
├── archived-complete/
├── archived-incomplete/
└── unknown-structure/
```

Each fixture must document:

- input;
- expected state;
- expected reasons;
- warnings;
- available actions.

---

# 9. Backend Fixtures

```text
tests/fixtures/backends/
├── healthy/
├── not-found/
├── auth-required/
├── incompatible/
├── success/
├── failure/
├── timeout/
├── cancelled/
├── noisy-output/
├── malformed-events/
├── path-violation/
└── secret-output/
```

## 9.1 Fake Executables

Temporary scripts can be created that:

- write stdout;
- write stderr;
- sleep;
- fail;
- create files;
- ignore signals;
- filter secrets;
- write out of scope.

---

# 10. Domain Tests

# 10.1 Project

- absolute root;
- openspec inside the project;
- invalid project;
- optional Git;
- diagnostics.

# 10.2 Workspace

- immutable snapshot;
- stable fingerprint;
- fingerprint changes with content;
- incomplete artifacts;
- unknown artifacts;
- paths.

# 10.3 Tasks

- empty checkbox;
- checked checkbox;
- `x` and `X`;
- indentation;
- identifiers;
- sections;
- invalid lines;
- progress;
- zero tasks.

# 10.4 Lifecycle

- all states;
- precedence;
- blocked;
- underlying;
- stale verification;
- archived;
- unknown;
- actions.

# 10.5 Commands

- availability;
- capabilities;
- confirmation;
- mutation;
- parameters;
- version.

# 10.6 Execution

- valid states;
- transitions;
- sequence;
- result;
- cancellation;
- timeout;
- interrupted.

---

# 11. Property-Based Testing

Hypothesis should be used where clear invariants exist.

## 11.1 Paths

Properties:

- no external path passes validation;
- normalization is idempotent;
- path traversal does not escape root.

## 11.2 Lifecycle

Properties:

- archived dominates;
- ready requires tasks;
- applying requires completed and pending;
- verification has no pending;
- ready-to-archive requires current verify;
- same input → same output.

## 11.3 Redaction

Properties:

- known secrets do not remain;
- multiple secrets are redacted;
- non-sensitive text is preserved.

## 11.4 Events

Properties:

- ordered sequence;
- valid timestamps;
- stable serialization.

---

# 12. Filesystem Tests

## 12.1 Reading

- valid file;
- missing file;
- permissions;
- encoding;
- empty content;
- large file;
- atomic replacement.

## 12.2 Symlinks

- internal;
- external;
- broken;
- circular.

## 12.3 Watcher

- create;
- modify;
- delete;
- move;
- multiple events;
- debounce;
- clean stop;
- partial write.

## 12.4 Concurrency

- refresh during execution;
- rapidly modified files;
- consistent snapshot.

---

# 13. Configuration Tests

## 13.1 Precedence

```text
defaults
< global
< project
< environment
< CLI
< session
```

## 13.2 Cases

- missing config;
- invalid TOML;
- unknown schema;
- unknown key;
- secret in config;
- project policy attempting to relax global;
- migration.

## 13.3 Platformdirs

Paths must be simulated to avoid writing to the real home dir.

---

# 14. Subprocess Tests

## 14.1 Mandatory Cases

- successful spawn;
- missing executable;
- permission denied;
- stdout;
- stderr;
- exit code;
- timeout;
- cancellation;
- process ignores SIGINT;
- child process;
- abundant output;
- invalid encoding;
- cwd.

## 14.2 Security

- separated arguments;
- no shell;
- filtered env;
- executable path;
- simulated command injection.

---

# 15. OpenSpec CLI Tests

## 15.1 Fake Adapter

Must simulate:

- version;
- capabilities;
- status;
- validate;
- JSON output;
- text output;
- error.

## 15.2 Cases

- missing CLI;
- supported version;
- partial version;
- unknown version;
- invalid JSON;
- filesystem/CLI discrepancy;
- command unavailable;
- exit 0 with invalid output;
- timeout.

## 15.3 Tests with Real CLI

Optional and separate.

Must run only if:

```text
OPENSPEC_INTEGRATION_TESTS=1
```

---

# 16. AgentBackend Tests

All backends must pass contract tests.

## 16.1 Healthcheck

- available;
- degraded;
- auth required;
- incompatible;
- misconfigured.

## 16.2 Capabilities

- consistent;
- not assumed;
- incompatible operation.

## 16.3 Execute

- events;
- streaming;
- stdout;
- stderr;
- success;
- failure;
- result.

## 16.4 Cancel

- cooperative;
- force;
- unsupported;
- partial files.

## 16.5 Security

- allowed paths;
- env;
- secrets;
- sandbox;
- network policy.

---

# 17. Codex CLI Backend Tests

## 17.1 Without Real Codex

Primary behavior must be tested with a fake executable.

## 17.2 Cases

- detection;
- version;
- authentication required;
- model;
- flags;
- prompt;
- cwd;
- sandbox;
- approvals;
- streaming;
- cancellation.

## 17.3 Real Codex

Manual tests or optional CI.

Must not be a requirement for a normal PR.

---

# 18. Git Tests

Use temporary repositories.

## Cases

- no repo;
- clean repo;
- dirty;
- staged;
- unstaged;
- untracked;
- conflict;
- detached HEAD;
- checkpoint;
- diff before/after;
- out-of-scope files.

## Rule

Never use the real test project repository.

---

# 19. SQLite Tests

## 19.1 Cases

- create schema;
- migrate;
- insert execution;
- append events;
- transaction;
- rollback;
- interrupted execution;
- retention;
- concurrency;
- redaction.

## 19.2 Temporary DB

Each test uses an isolated database.

## 19.3 Integrity

- foreign keys;
- uniqueness;
- sequence;
- valid states.

---

# 20. Security Tests

## 20.1 Paths

- traversal;
- external symlink;
- case sensitivity;
- Unicode;
- long path.

## 20.2 Secrets

- env;
- stdout;
- stderr;
- prompt;
- metadata;
- stack trace;
- export.

## 20.3 Configuration

- arbitrary executable;
- shell flag;
- unrestricted;
- network;
- global policies.

## 20.4 Agent Overreach

Simulate:

- external write;
- deletion;
- sensitive modification;
- unexpected command.

## 20.5 Locks

- simultaneous operation;
- orphan lock;
- crash;
- recovery.

---

# 21. TUI Tests

## 21.1 Shell

- starts;
- closes;
- switches view;
- help;
- status bar;
- active project.

## 21.2 Board

- columns;
- cards;
- navigation;
- filters;
- refresh;
- empty states;
- blocked;
- unknown.

## 21.3 Specs

- tree;
- selection;
- preview;
- search;
- error.

## 21.4 Change Detail

- tabs;
- artifacts;
- tasks;
- lifecycle;
- actions;
- diagnostics.

## 21.5 Runner

- preview;
- confirmation;
- streaming;
- cancellation;
- timeout;
- result.

## 21.6 Settings

- editing;
- validation;
- hidden secrets;
- healthcheck;
- reset.

---

# 22. Snapshot Testing

May be used for:

- layouts;
- empty states;
- cards;
- modals;
- errors.

Must not be used as the only test.

Snapshots must be:

- small;
- stable;
- reviewable;
- independent of variable size when possible.

---

# 23. Performance Tests

## 23.1 Initial Objectives

- fast startup;
- responsive board;
- reasonable parsing;
- stable watcher;
- bounded logs.

## 23.2 Scenarios

- 10 specs;
- 100 specs;
- 50 changes;
- 5000 tasks;
- large log;
- multiple events.

## 23.3 Benchmarks

Not an MVP gate unless there is obvious regression.

The following may be used:

```text
pytest-benchmark
```

---

# 24. Resilience Tests

## Cases

- file disappears;
- CLI crashes;
- process dies;
- SQLite locked;
- Git changes;
- watcher fails;
- backend disconnects;
- config changes;
- terminal resizes;
- unexpected shutdown.

## Expected Result

- visible error;
- no global crash;
- recovery;
- diagnostics;
- consistent history.

---

# 25. Coverage

## 25.1 Initial Target

```text
Minimum total coverage: 80%
Domain and critical rules: 95%
Security: 90%
Critical adapters: 85%
UI: functional coverage, not just line
```

## 25.2 Exclusions

Only exclude:

- generated code;
- justified impossible branches;
- trivial wrappers.

## 25.3 Rule

Coverage does not replace quality.

---

# 26. CI

## 26.1 Minimum Jobs

```text
lint
type-check
unit-tests
contract-tests
integration-tests
tui-tests
security-checks
package-build
```

## 26.2 Python Matrix

```text
3.11
3.12
3.13
3.14
```

## 26.3 Strategy

- lint on one version;
- full tests on 3.11 and 3.14;
- reduced suite on 3.12 and 3.13;
- package build on 3.11.

## 26.4 Cache

Dependency caching allowed; no caching of results that hide failures.

---

# 27. Gates per OpenSpec Change

Before `/opsx:archive`, each change must meet:

```text
[ ] Requirements implemented
[ ] Unit tests
[ ] Contract tests if applicable
[ ] Integration tests if applicable
[ ] TUI tests if applicable
[ ] Security tests if applicable
[ ] Ruff
[ ] MyPy
[ ] Pytest
[ ] Python 3.11
[ ] Documentation
[ ] No tests skipped without reason
[ ] /opsx:verify satisfactory
```

---

# 28. Definition of Test Complete

A feature is test complete when:

1. It has a happy path.
2. It has a main error.
3. It has invalid input.
4. It has a boundary case.
5. It has regression if it fixes a bug.
6. It does not depend on uncontrolled external resources.
7. It is deterministic.
8. It passes on Python 3.11.
9. It does not leak secrets.
10. Complex fixtures are documented.

---

# 29. Skip and Xfail Policy

## 29.1 Skip

Only for:

- unsupported platform;
- optional integration;
- explicit external dependency.

## 29.2 Xfail

Must include:

- issue;
- reason;
- condition;
- date or context.

## 29.3 Prohibition

Do not use skip to hide unstable tests.

---

# 30. Flaky Tests

A flaky test must:

1. be isolated;
2. be investigated;
3. be fixed;
4. not be retried indefinitely.

Retries may only be used temporarily.

---

# 31. Test Data

Do not use:

- real credentials;
- personal repositories;
- user paths;
- sensitive names;
- private data.

Use fictional names.

---

# 32. Manual Tests

They will be documented for:

- real rendering;
- terminals;
- real Codex;
- keyring;
- signals;
- packaging;
- pipx.

Release checklist.

---

# 33. Distribution Tests

## Cases

- wheel;
- sdist;
- clean install;
- `pipx install`;
- `opsx-tui --version`;
- TCSS resources;
- entry point;
- Python 3.11;
- uninstall.

---

# 34. Migration Tests

When persistence exists:

- config schema;
- SQLite schema;
- local metadata;
- backward compatibility;
- reasonable rollback.

---

# 35. Result Reporting

CI must deliver:

- failed tests;
- coverage;
- duration;
- version;
- platform;
- log artifacts;
- security reports.

Must not publish secrets.

---

# 36. Testing Invariants

1. No test uses real home dir.
2. No test requires credentials.
3. No test writes outside temp.
4. No test uses shell.
5. No test depends on filesystem order.
6. Python 3.11 is always tested.
7. Every backend passes contract tests.
8. Every lifecycle rule has tests.
9. Every fixed vulnerability has regression.
10. Every security test validates a negative result.
11. TUI is tested with fake services.
12. E2E tests are few.
13. Fixtures are readable.
14. Skips are justified.
15. Critical coverage does not decrease without explanation.

---

# 37. Constraints for the Implementing Agent

The agent must not:

- test only happy paths;
- depend on real Codex;
- depend on real OpenSpec for unit tests;
- write tests that use the active repo;
- use long sleeps;
- hide flakes with retries;
- reduce coverage without justification;
- test domain rules only through UI;
- mock everything to the point of not testing integration;
- use giant snapshots;
- ignore Python 3.11;
- omit security;
- use real data;
- mark tests as skip for convenience;
- introduce unnecessary testing dependencies.

---

# 38. Phased Adoption Plan

## Phase 0

- pytest;
- Ruff;
- MyPy;
- Python CI;
- base unit tests.

## Phase 1

- OpenSpec fixtures;
- parsers;
- workspace;
- watchers.

## Phase 2

- Textual pilot;
- navigation;
- Markdown;
- screens.

## Phase 3

- lifecycle;
- property tests;
- Kanban.

## Phase 4

- subprocess;
- CLI contract;
- commands.

## Phase 5

- AgentBackend contract;
- fake Codex;
- cancellation.

## Phase 6

- providers;
- secrets;
- network.

## Phase 7

- SQLite;
- recovery;
- history.

## Phase 8

- Git;
- security;
- worktrees.

## Phase 9

- packaging;
- install;
- release checklist.

---

# 39. Summary

The strategy combines:

```text
UNIT TESTS
fast, deterministic rules

CONTRACT TESTS
interchangeable adapters

INTEGRATION TESTS
filesystem, Git, processes, SQLite

TUI TESTS
visible experience

E2E
critical flows

SECURITY TESTS
dangerous failures
```

The main rule is:

```text
OPSX TUI should not need a real agent to prove that it works.
```
