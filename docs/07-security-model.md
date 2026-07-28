# Security Model — OPSX TUI

## 1. Purpose

This document defines the security model of **OPSX TUI**.

Its goal is to establish:

- which assets must be protected;
- which components are trusted and which are not;
- what the trust boundaries are;
- which threats must be considered;
- which controls are mandatory;
- which operations require confirmation;
- how paths, secrets, processes, and configurations are protected;
- how risk is reduced when executing agents;
- how events are recorded without exposing sensitive information;
- how the application must react to unsafe situations.

This document is normative for:

- process execution;
- OpenSpec integration;
- agent backends;
- LLM providers;
- configuration;
- persistence;
- Git integration;
- path handling;
- logs;
- confirmation UI;
- security tests;
- operational policy definition.

---

# 2. Scope

The model covers:

- local application;
- open project;
- OpenSpec workspace;
- filesystem;
- child processes;
- OpenSpec CLI;
- agents;
- providers;
- Git;
- SQLite;
- keyring;
- global configuration;
- per-project configuration;
- environment variables;
- logs;
- history;
- external editor.

It does not initially cover:

- multi-user collaboration;
- web server;
- distributed remote execution;
- enterprise authentication;
- role-based access control;
- disk encryption;
- operating system security;
- LLM provider internal security.

---

# 3. Security objectives

OPSX TUI must protect:

1. Workspace integrity.
2. Secret confidentiality.
3. Spec and change integrity.
4. Execution traceability.
5. Explicit user control.
6. Separation between reading and writing.
7. Reasonable process isolation.
8. Configuration consistency.
9. Log privacy.
10. Recovery from partial executions.
11. Prevention of arbitrary commands.
12. Prevention of writes outside the project.

---

# 4. Protected assets

## 4.1 Source code

Includes:

- application code;
- tests;
- configurations;
- scripts;
- declared dependencies;
- infrastructure files.

Risks:

- unauthorized modification;
- deletion;
- corruption;
- out-of-scope changes.

## 4.2 OpenSpec artifacts

Includes:

- specs;
- proposals;
- designs;
- tasks;
- delta specs;
- archived changes;
- OpenSpec configuration.

Risks:

- loss;
- accidental editing;
- incorrect archive;
- duplication;
- inconsistency.

## 4.3 Secrets

Includes:

- API keys;
- tokens;
- credentials;
- cookies;
- certificates;
- private keys;
- sensitive variables.

Risks:

- exposure in logs;
- persistence in TOML;
- inheritance to processes;
- sending to the agent;
- inclusion in prompts.

## 4.4 Operational history

Includes:

- executions;
- events;
- results;
- errors;
- affected files;
- metadata.

Risks:

- information exposure;
- manipulation;
- unlimited growth;
- sensitive content.

## 4.5 Configuration

Includes:

- global configuration;
- project configuration;
- backends;
- providers;
- policies;
- commands;
- paths.

Risks:

- malicious configuration;
- fake executables;
- dangerous overrides;
- permission escalation.

---

# 5. Actors and components

## 5.1 User

Considered authorized to operate the project, but may make mistakes.

Associated threats:

- confirming without reviewing;
- choosing the wrong project;
- using a broad sandbox;
- running on a dirty working tree.

## 5.2 OPSX TUI

Coordinating component.

Must minimize privileges and validate inputs.

## 5.3 Project

Not considered trusted by default.

May contain:

- malicious configuration;
- symlinks;
- scripts;
- prompts;
- manipulated files;
- dangerous names.

## 5.4 OpenSpec CLI

External component.

Must validate:

- path;
- version;
- behavior;
- output;
- return code.

## 5.5 Agent Backend

High-capability component.

Can:

- read;
- write;
- execute;
- use network;
- modify Git;
- access the environment.

Must be treated as a potentially risky component.

## 5.6 LLM Provider

External service.

May receive:

- prompts;
- code fragments;
- context;
- metadata.

Minimization policy must be applied.

## 5.7 Operating system

Considered a trusted base, but OPSX TUI must not assume complete protection.

---

# 6. Trust boundaries

```text
┌──────────────────────────────────────┐
│ User                                 │
└───────────────┬──────────────────────┘
                │
                ▼
┌──────────────────────────────────────┐
│ OPSX TUI                             │
│ domain + application + UI            │
└───────┬───────────┬───────────┬──────┘
        │           │           │
        ▼           ▼           ▼
  Filesystem   OpenSpec CLI   Agent Backend
        │           │           │
        └───────────┴───────────┘
                    │
                    ▼
                Provider LLM
```

Every crossing requires validation.

---

# 7. Operation classification

## 7.1 Safe read

Examples:

- list specs;
- read changes;
- view logs;
- query version;
- search;
- filter;
- healthcheck.

Does not require confirmation.

## 7.2 Limited write

Examples:

- save own configuration;
- save local metadata;
- persist history;
- change preferences.

May require validation, but not confirmation in all cases.

## 7.3 Methodological write

Examples:

- propose;
- continue;
- fast-forward;
- sync;
- archive.

Requires confirmation.

## 7.4 Code write

Examples:

- apply;
- test generation;
- refactor;
- agent execution with workspace write.

Requires confirmation and prior controls.

## 7.5 Destructive operation

Examples:

- delete;
- clean worktree;
- overwrite configuration;
- reset;
- irreversible archive;
- unrestricted execution.

Requires reinforced confirmation.

---

# 8. Confirmations

## 8.1 Simple confirmation

Must show:

- operation;
- project;
- change;
- backend;
- model;
- permissions.

## 8.2 Reinforced confirmation

Must also show:

- working tree;
- files at risk;
- sandbox;
- network access;
- allowed paths;
- warnings;
- consequences.

## 8.3 Text confirmation

For high-risk operations, typing may be required:

```text
ARCHIVE
DELETE
UNRESTRICTED
```

## 8.4 Rule

A confirmation must not be reused for a different operation.

---

# 9. Subprocess security

## 9.1 Allowed API

```python
asyncio.create_subprocess_exec
```

## 9.2 Prohibited

```python
shell=True
create_subprocess_shell
os.system
subprocess.run(..., shell=True)
```

## 9.3 Arguments

Each argument must be passed as a separate element.

## 9.4 Executables

The executable path must:

- be resolved;
- be validated;
- be displayed;
- be compared with configuration;
- be verified before execution.

## 9.5 CWD

Every execution must define `cwd`.

Must not depend on the application's global directory.

## 9.6 Environment

The environment must be built via allowlist.

Must not be inherited blindly.

---

# 10. Path policy

## 10.1 Normalization

Every path must:

- be made absolute;
- be resolved;
- be validated;
- be compared with project root;
- preserve a safe relative version.

## 10.2 Allowed writes

By default:

```text
project_root/**
```

## 10.3 Prohibited writes

- outside the project;
- full home directory;
- `/etc`;
- `/usr`;
- `/var`;
- paths of other projects;
- sockets;
- devices;
- sensitive mounts.

## 10.4 Symlinks

Every symlink must be classified:

- internal;
- external;
- broken;
- circular.

External symlink:

- warning;
- blocked by default for writing.

## 10.5 Path traversal

Entries such as:

```text
../../
```

must be normalized and validated.

---

# 11. Sandbox

## 11.1 Modes

```text
read-only
workspace-write
unrestricted
backend-default
```

## 11.2 Default

```text
workspace-write
```

for modifying operations when the backend supports it.

## 11.3 Read-only

For:

- explore;
- inspect;
- validate;
- review.

## 11.4 Unrestricted

Only with:

- policy enabled;
- reinforced confirmation;
- reason;
- log;
- persistent warning.

## 11.5 Truthfulness

The UI must not claim a sandbox exists if the backend does not guarantee it.

---

# 12. Network policy

## 12.1 Modes

```text
deny
restricted
allow
backend-default
```

## 12.2 Default

For local operations:

```text
deny
```

if the backend allows control.

## 12.3 Restricted

May allow:

- configured provider;
- defined repositories;
- specific endpoints.

## 12.4 Transparency

If the network cannot be controlled:

- show limitation;
- do not simulate compliance;
- apply organizational policy.

---

# 13. Secrets

## 13.1 Storage

Allowed:

- keyring;
- environment variables;
- CLI's own authentication;
- temporary in-memory credentials.

Prohibited:

- TOML;
- YAML;
- plain-text SQLite;
- logs;
- persisted prompts;
- events.

## 13.2 Detection

Initial patterns:

```text
*_API_KEY
*_TOKEN
*_SECRET
*_PASSWORD
*.pem
*.key
.env
credentials*
secrets*
```

## 13.3 Redaction

Format:

```text
<redacted>
```

## 13.4 Propagation

A secret must only be delivered to the process that requires it.

## 13.5 UI

Must show:

```text
Configured
Not configured
Environment variable
Keyring
```

Never the full value.

---

# 14. Configuration security

## 14.1 Global

Considered more trusted than project configuration.

## 14.2 Project

Must be treated as untrusted until validated.

May contain:

- arbitrary executable;
- paths;
- backend;
- flags;
- variables;
- commands.

## 14.3 Safe precedence

A project configuration must not be able to:

- disable mandatory global confirmations;
- enable unrestricted without policy;
- store secrets;
- point outside the workspace;
- override prohibited executables;
- enable shell.

## 14.4 Schema version

Every file must declare:

```toml
schema_version = 1
```

## 14.5 Unknown keys

- preserve where applicable;
- warn;
- do not execute unknown behavior.

---

# 15. Agent security

## 15.1 Risks

The agent can:

- execute commands;
- modify files;
- follow malicious instructions;
- read secrets;
- send data;
- delete content;
- change Git;
- expand scope.

## 15.2 Controls

- sandbox;
- allowed paths;
- network policy;
- filtered environment;
- explicit prompt;
- scope;
- confirmation;
- watcher;
- Git diff;
- time limits;
- cancellation;
- post-validation.

## 15.3 Prompt injection from repository

The repository may contain text that attempts to instruct the agent.

OPSX TUI must:

- treat project content as data;
- include hierarchy instruction;
- not elevate found instructions;
- limit permissions;
- record actions.

## 15.4 Scope control

Every request must declare:

- change;
- objective;
- paths;
- expected files;
- prohibitions;
- DoD;
- do not expand scope.

---

# 16. Provider security

## 16.1 Minimization

Send only the necessary context.

## 16.2 Sensitivity

Before sending:

- redact secrets;
- exclude sensitive files;
- warn if private code is sent;
- apply network policy.

## 16.3 Logs

Do not log full prompts by default when they contain code or sensitive data.

## 16.4 Configuration

Every provider must declare:

- endpoint;
- region if applicable;
- policy;
- model;
- credential source.

---

# 17. Git as a security control

## 17.1 Prior inspection

Before modifying operations:

- branch;
- HEAD;
- dirty;
- staged;
- unstaged;
- untracked;
- conflicts.

## 17.2 Initial policy

- Git conflict blocks apply;
- dirty generates warning;
- optional checkpoint;
- detached HEAD generates warning;
- destructive operation requires confirmation.

## 17.3 Checkpoint

Never automatic without confirmation.

Must show included files.

## 17.4 After execution

- compute diff;
- show files;
- detect out-of-scope changes;
- record base commit.

---

# 18. Secure persistence

## 18.1 SQLite

Must contain:

- IDs;
- timestamps;
- states;
- summaries;
- redacted events;
- affected files;
- references.

Must not contain:

- API keys;
- tokens;
- full sensitive content;
- full environment;
- private keys.

## 18.2 Permissions

The file must be created with restrictive permissions per platform.

## 18.3 Retention

Apply:

- limits;
- purge;
- compaction;
- secure export.

## 18.4 Integrity

Recommended:

- transactions;
- WAL;
- constraints;
- versioned migrations.

---

# 19. Logs

## 19.1 Levels

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

## 19.2 DEBUG

May include technical details, but not secrets.

## 19.3 Redaction

Apply before:

- console;
- file;
- SQLite;
- export.

## 19.4 Stack traces

Available for diagnostics, but must not show sensitive variables.

## 19.5 Export

Must warn that it may contain:

- paths;
- names;
- messages;
- fragments.

---

# 20. Sensitive files

## 20.1 Initial list

```text
.env
.env.*
*.pem
*.key
id_rsa
id_ed25519
credentials.json
secrets.*
config/private/**
```

## 20.2 Operations

- no full preview;
- do not persist content;
- do not send to provider by default;
- do not include in prompts;
- warning when modified.

## 20.3 Overrides

Only via explicit policy.

---

# 21. Concurrent execution prevention

## 21.1 Locks

One modifying operation per workspace.

## 21.2 Scope

Locks per:

- project;
- workspace;
- change;
- operation.

## 21.3 Recovery

Orphan locks must be detected and cleaned with evidence.

## 21.4 Persistence

A lock must not depend only on memory if it can survive a crash.

---

# 22. Cancellation and consistency

## 22.1 Cancel does not revert

The UI must indicate this explicitly.

## 22.2 After cancellation

- refresh;
- Git diff;
- detect partials;
- invalidate verification;
- log;
- mark review required.

## 22.3 Uncontrollable process

If it cannot be terminated:

- warn;
- mark unknown;
- do not release lock prematurely;
- show PID when safe.

---

# 23. Executable trust policy

## 23.1 Allowed sources

- PATH;
- configured global path;
- validated per-project path;
- controlled virtual environment.

## 23.2 Project path

An executable inside the project is less trusted.

Must require:

- confirmation;
- hash;
- policy;
- warning.

## 23.3 Version check

Whenever possible.

## 23.4 Executable change

If hash or path changes:

- invalidate healthcheck;
- request review.

---

# 24. Main threats

## 24.1 Command injection

Mitigation:

- no shell;
- separate arguments;
- command catalog;
- validation.

## 24.2 Path traversal

Mitigation:

- normalization;
- root checks;
- symlink policy.

## 24.3 Secret leakage

Mitigation:

- keyring;
- redaction;
- allowlist;
- minimization.

## 24.4 Malicious project config

Mitigation:

- schema;
- global policies;
- do not execute arbitrary commands.

## 24.5 Prompt injection

Mitigation:

- content as data;
- permissions;
- scope;
- validation.

## 24.6 Agent overreach

Mitigation:

- sandbox;
- allowed paths;
- Git diff;
- cancellation.

## 24.7 Supply chain

Mitigation:

- lockfiles;
- hashes;
- versions;
- minimal dependencies;
- review.

## 24.8 Log poisoning

Mitigation:

- sanitize control characters;
- limits;
- safe encoding.

## 24.9 Resource exhaustion

Mitigation:

- timeouts;
- bounded queues;
- log limits;
- concurrency limits.

## 24.10 Destructive Git commands

Mitigation:

- not allowed by default;
- reinforced confirmation;
- checkpoint.

---

# 25. Pre-execution controls

Mandatory checklist:

```text
[ ] Valid project
[ ] Valid change
[ ] Supported operation
[ ] Healthy backend
[ ] Valid model
[ ] Authentication available
[ ] Allowed paths
[ ] Known sandbox
[ ] Known network policy
[ ] Git inspected
[ ] No conflicts
[ ] No incompatible process
[ ] Confirmation obtained
```

---

# 26. Post-execution controls

```text
[ ] Process finished
[ ] Exit code captured
[ ] Workspace refreshed
[ ] Git diff inspected
[ ] Out-of-scope files detected
[ ] Secrets not exposed
[ ] Functional result validated
[ ] Verification invalidated if applicable
[ ] History persisted
[ ] Locks released
```

---

# 27. Incident response

## 27.1 Minor incident

Examples:

- warning;
- degraded backend;
- unexpected file.

Action:

- log;
- inform;
- allow continuation per policy.

## 27.2 Serious incident

Examples:

- secret in output;
- external write;
- conflict;
- disallowed command.

Action:

- stop;
- block;
- redact;
- preserve evidence;
- request review.

## 27.3 Critical incident

Examples:

- exfiltration;
- mass deletion;
- process out of control;
- system modification.

Action:

- cancel;
- isolate;
- do not continue;
- show clear instructions;
- export safe diagnostics.

---

# 28. Configurable policies

## 28.1 Mandatory global

Cannot be relaxed from project:

- no shell;
- no plain-text secrets;
- path validation;
- redaction;
- unrestricted confirmation.

## 28.2 Organizational

Future:

- allowed providers;
- allowed models;
- paths;
- network;
- retention;
- plugins.

## 28.3 Project

May define:

- preferred backend;
- timeout;
- checkpoint;
- required clean tree;
- internal allowed paths.

---

# 29. Security tests

## 29.1 Unit

- path traversal;
- external symlink;
- redaction;
- malicious config;
- secret detection;
- executable validation;
- policy precedence.

## 29.2 Integration

- process with dangerous arguments;
- simulated external write;
- cancellation;
- timeout;
- abundant logs;
- filtered env;
- backend without sandbox.

## 29.3 TUI

- confirmation;
- warning;
- blocking;
- hidden secrets;
- visible unrestricted.

## 29.4 Property-based

- no allowed path outside root;
- no known secret remains;
- global policies always dominate;
- arguments are never concatenated in shell.

---

# 30. Acceptance criteria

The model is considered implemented when:

1. No shell execution exists.
2. Paths are validated.
3. External symlinks are detected.
4. Secrets are redacted.
5. Project configuration cannot relax mandatory policies.
6. Agents use sandbox when available.
7. UI shows real limitations.
8. Git is inspected before writing.
9. Risk operations are confirmed.
10. Logs contain no secrets.
11. Cancellation leaves evidence.
12. Locks prevent incompatible concurrency.
13. Security tests pass.
14. Read mode works with minimum privileges.
15. External writes generate a block.

---

# 31. Invariants

1. Never `shell=True`.
2. Never secrets in TOML.
3. Never write outside the workspace without explicit policy.
4. Never hide nonexistent sandbox.
5. Never run unrestricted without confirmation.
6. Never blindly trust project configuration.
7. Never inherit the entire environment without filtering.
8. Never persist secrets.
9. Never label cancellation as rollback.
10. Never release lock before the process finishes.
11. Never allow Git conflict for apply by default.
12. Never use textual output as sole evidence.
13. Never send sensitive files to the provider by default.
14. Never accept path traversal.
15. Never skip recording a modifying operation.

---

# 32. Constraints for the implementing agent

The agent shall not:

- add shell execution;
- store credentials;
- disable redaction;
- allow external paths for convenience;
- trust filenames;
- ignore symlinks;
- hide warnings;
- auto-execute init/update;
- enable unrestricted by default;
- inherit the entire environment;
- log full sensitive prompts;
- implement security only in UI;
- skip negative tests;
- consider Git optional for configured controls;
- mix global policy with project config.

---

# 33. Summary

OPSX TUI security is based on five controls:

```text
VALIDATE
paths, configuration, capabilities

LIMIT
permissions, network, environment, concurrency

SHOW
risks, commands, changes, limitations

CONFIRM
modifying and destructive operations

VERIFY
result, diff, files, logs, fingerprints
```

The main rule is:

```text
An agent can be powerful.
OPSX TUI must make that power visible, limited, and auditable.
```
