# Functional Product Contract — OPSX TUI

## 1. Purpose

This document defines the functional contract of **OPSX TUI**, a terminal application to visualize, understand, and operate OpenSpec projects from a TUI interface inspired by tools like `bpytop`.

The purpose of this contract is to precisely establish:

- what problem the product solves;
- who its users are;
- what capabilities it must offer;
- what behaviors are mandatory;
- what is out of scope;
- how the interface should behave;
- what the MVP functional criteria are;
- which rules must not be reinterpreted by the implementing agent.

This document is normative for implementation. In case of conflict between an improvised decision during development and this contract, this document prevails, unless there is a subsequent ADR that explicitly modifies the decision.

---

# 2. Product Vision

## 2.1 Definition

OPSX TUI is a terminal tool that allows opening an OpenSpec project, visualizing its specifications, changes, tasks, and states, executing local OpenSpec commands, and delegating OPSX actions to configured agents.

The tool must function as an **operational control center for OpenSpec**.

## 2.2 Vision Statement

> OPSX TUI must allow a person to understand and operate a complete OpenSpec project without depending on manually navigating between folders, Markdown files, terminal commands, and multiple agents.

## 2.3 Value Proposition

OPSX TUI delivers value through five main capabilities:

1. **Visibility**  
   Presents specs, changes, tasks, artifacts, and states in a single interface.

2. **Understanding**  
   Explains why each change is in a given state.

3. **Operation**  
   Allows executing OpenSpec commands and OPSX actions from a central point.

4. **Control**  
   Keeps the user informed before, during, and after each execution.

5. **Traceability**  
   Records executions, results, affected files, errors, and verifications.

---

# 3. Problem It Solves

Daily use of OpenSpec typically requires combining:

- filesystem navigation;
- reading multiple Markdown files;
- executing CLI commands;
- interacting with programming agents;
- manual task tracking;
- state review;
- Git inspection;
- log analysis;
- result validation.

This produces several problems:

- poor global visibility of project state;
- difficulty knowing which changes are ready or blocked;
- risk of executing actions on the wrong change;
- dispersion across tools;
- lack of traceability;
- inconsistency between agents;
- difficulty operating multiple changes simultaneously;
- excessive dependence on memorized commands;
- poor clarity for users who know the business but not the internal OpenSpec structure.

OPSX TUI must reduce that fragmentation and turn the OpenSpec project into a coherent operational experience.

---

# 4. Target Users

## 4.1 Primary User: Individual Developer

A person who uses OpenSpec to build software and works with one or more programming agents.

Needs:

- review active changes;
- know what is missing;
- execute actions;
- inspect results;
- avoid errors on the repository;
- maintain traceability;
- switch projects quickly.

## 4.2 Secondary User: Technical Lead

A person who needs to review the state of multiple changes, validate quality, and decide what should advance.

Needs:

- global vision;
- detect blocked changes;
- review requirements;
- review tasks;
- know validations;
- inspect history;
- identify risks.

## 4.3 Secondary User: Functional Analyst or Technical Product Owner

A person who reviews proposals, requirements, and scenarios, although they do not necessarily execute code.

Needs:

- read specs;
- compare changes;
- review proposals;
- understand states;
- validate scope;
- avoid depending on complex commands.

## 4.4 Advanced User: Multi-Agent Operator

A person who uses Codex, Claude Code, Gemini CLI, or other agents.

Needs:

- configure backends;
- select models;
- apply policies per operation;
- compare results;
- switch provider;
- review authentication errors;
- control sandbox and approvals.

---

# 5. Functional Principles

OPSX TUI must respect the following principles.

## 5.1 OpenSpec Is the Source of Truth

The tool must not create a parallel methodological system.

OpenSpec owns:

- specs;
- proposals;
- designs;
- tasks;
- active changes;
- archived changes;
- artifacts;
- requirements;
- scenarios;
- derivable methodological state.

OPSX TUI may read, represent, and operate on that data, but must not duplicate it as an authoritative source.

## 5.2 The User Maintains Control

The tool must not execute major modifying actions without the user knowing:

- what operation will be performed;
- on which project;
- on which change;
- with which backend;
- with which model;
- what command or instruction will be sent;
- what permissions the agent will have;
- whether there are risks.

## 5.3 State Must Be Explainable

Each Kanban state must show observable reasons.

Example:

```text
State: Applying

Reasons:
- Proposal available.
- Design available.
- Delta specs available.
- 7 of 11 tasks completed.
```

Opaque or unsubstantiated states are not accepted.

## 5.4 Operations Must Be Observable

Every execution must allow knowing:

- when it started;
- what process was executed;
- what output it produced;
- what files it affected;
- how long it lasted;
- how it ended;
- whether it was cancelled;
- whether it requires review.

## 5.5 Reading Before Automation

OPSX TUI's primary responsibility is to correctly represent OpenSpec.

Agent automation must not compromise the fidelity of workspace reading.

## 5.6 Security by Default

Modifying actions must assume there is risk.

The application must be conservative regarding:

- dirty working tree;
- unknown commands;
- paths outside the workspace;
- simultaneous processes;
- absent credentials;
- invalid configurations;
- version errors;
- incomplete artifacts.

---

# 6. Product Objectives

## 6.1 Functional Objectives

OPSX TUI must allow:

1. Detecting an OpenSpec project.
2. Reading canonical specs.
3. Reading active changes.
4. Reading archived changes.
5. Reading proposals, designs, tasks, and delta specs.
6. Showing task progress.
7. Inferring and explaining the state of each change.
8. Visualizing changes on a Kanban board.
9. Opening the detail of a change.
10. Searching specs and changes.
11. Executing local OpenSpec commands.
12. Executing OPSX actions via an agent.
13. Configuring backends and models.
14. Showing real-time output.
15. Canceling processes.
16. Maintaining history.
17. Showing Git state.
18. Applying security controls.
19. Recovering after an unexpected shutdown.
20. Operating entirely via keyboard.

## 6.2 Relevant Non-Functional Objectives

- Reasonable startup time on medium-sized projects.
- Non-blocking interface.
- Compatibility with Python 3.11 through 3.14.
- Full functionality without a mouse.
- Bounded memory usage.
- Understandable errors.
- Extensible architecture.
- Automated tests.
- Portable configuration.

---

# 7. Functional Scope

## 7.1 Included in the Product

### Navigation

- project selection;
- recent projects;
- navigation between views;
- keyboard navigation;
- contextual help;
- command palette.

### OpenSpec Reading

- canonical specs;
- active changes;
- archived changes;
- proposals;
- designs;
- tasks;
- delta specs;
- OpenSpec configuration;
- structure diagnostics.

### Visualization

- Kanban board;
- change detail;
- spec browser;
- Markdown viewer;
- progress;
- states;
- logs;
- history.

### Operation

- OpenSpec CLI commands;
- OPSX actions;
- agent backends;
- async execution;
- cancellation;
- confirmations;
- pre-execution validations.

### Configuration

- global configuration;
- per-project configuration;
- default backend;
- model per operation;
- timeouts;
- approvals;
- themes;
- interface preferences.

### Security

- Git inspection;
- working tree;
- confirmations;
- path control;
- secret redaction;
- incompatible execution blocking.

## 7.2 Out of Initial Scope

Not included in the MVP:

- full Markdown editor;
- Git replacement;
- remote project hosting;
- real-time multi-user collaboration;
- cloud synchronization;
- visual spec editing via forms;
- enterprise permission management;
- web server;
- mobile application;
- distributed execution;
- plugin marketplace;
- automatic OpenSpec file editing without explicit action;
- creation of an alternative methodology to OpenSpec.

---

# 8. Main Use Cases

# 8.1 Opening an OpenSpec Project

## Actor

User.

## Main Flow

1. The user runs `opsx-tui`.
2. The application attempts to detect the root.
3. If it finds a valid project, it opens it.
4. It loads the workspace.
5. It shows the board.
6. It presents non-critical diagnostics.

## Alternatives

- The user provides `--project`.
- The path comes from `OPSX_TUI_PROJECT`.
- A recent project is selected.
- A folder selector opens.
- OpenSpec initialization is offered.

## Result

The user visualizes the project without any file being modified.

---

# 8.2 Reviewing the Kanban Board

## Actor

User.

## Main Flow

1. The user opens the Board view.
2. The application groups changes by state.
3. Each card shows:
   - name;
   - progress;
   - artifacts;
   - alerts;
   - priority;
   - active backend if applicable.
4. The user navigates between columns.
5. They open the detail of a change.

## Result

The user understands the global state of the project.

---

# 8.3 Reviewing a Spec

## Actor

User.

## Main Flow

1. The user opens Specs.
2. They select a capability.
3. They see its requirements.
4. They browse scenarios.
5. They review related changes.
6. They can open the file in `$EDITOR`.

## Result

The user understands the expected canonical behavior of the product.

---

# 8.4 Reviewing a Change

## Actor

User.

## Main Flow

1. The user selects a change.
2. The application shows:
   - state;
   - reasons;
   - progress;
   - proposal;
   - design;
   - delta specs;
   - tasks;
   - verifications;
   - recent executions;
   - risks;
   - available actions.
3. The user navigates between artifacts.

## Result

The user understands what is intended to be built, what has been done, and what is missing.

---

# 8.5 Executing a Local OpenSpec Command

## Actor

User.

## Main Flow

1. The user opens the palette.
2. They select a local operation.
3. The application validates availability.
4. It shows a preview.
5. It requests confirmation if applicable.
6. It executes the command.
7. It shows output.
8. It records the result.
9. It refreshes the workspace.

## Result

The command is executed in an observable and controlled manner.

---

# 8.6 Executing an OPSX Action via Agent

## Actor

User.

## Main Flow

1. The user selects a change.
2. They choose an action, e.g. `apply`.
3. The application selects the configured backend.
4. It validates:
   - backend;
   - authentication;
   - model;
   - Git;
   - permissions;
   - active process.
5. It shows the instruction.
6. It requests confirmation.
7. It executes the agent.
8. It streams events.
9. It watches file changes.
10. It validates the result.
11. It updates the state.
12. It records the execution.

## Result

The action is executed without losing control or traceability.

---

# 8.7 Canceling an Execution

## Actor

User.

## Main Flow

1. The user requests cancellation.
2. The application confirms when there is risk.
3. It sends a termination signal.
4. It waits for a configurable period.
5. It forces termination if the process does not respond.
6. It marks the execution as cancelled.
7. It refreshes the workspace.
8. It shows possible inconsistencies.

## Result

The process stops or is marked as uncontrollable.

---

# 8.8 Configuring a Backend

## Actor

Advanced user.

## Main Flow

1. The user opens Settings.
2. They create or edit a backend.
3. They define:
   - type;
   - executable or endpoint;
   - model;
   - approvals;
   - sandbox;
   - timeout.
4. The application validates.
5. It runs a healthcheck.
6. It saves the non-sensitive configuration.
7. It saves secrets in keyring or uses environment variables.

## Result

The backend becomes available for compatible operations.

---

# 8.9 Consulting History

## Actor

User.

## Main Flow

1. The user opens Runs or Logs.
2. They filter by project, change, operation, or result.
3. They select an execution.
4. They review:
   - timestamps;
   - backend;
   - model;
   - output;
   - files;
   - exit code;
   - summary;
   - errors.

## Result

The user can audit what happened.

---

# 9. Product Screens

# 9.1 Board

## Purpose

Show the global state of changes.

## Content

- columns;
- cards;
- filters;
- search;
- progress;
- alerts;
- change counter;
- watcher status;
- active project.

## Actions

- open change;
- search;
- filter;
- execute contextual action;
- switch project;
- refresh.

---

# 9.2 Specs

## Purpose

Explore canonical specifications.

## Content

- capability tree;
- requirements;
- scenarios;
- Markdown view;
- related changes;
- paths.

## Actions

- search;
- open file;
- navigate to change;
- compare with delta.

---

# 9.3 Changes

## Purpose

Show a structured list of active and archived changes.

## Content

- name;
- state;
- progress;
- last modified;
- artifacts;
- priority;
- tags;
- risks.

## Actions

- sort;
- filter;
- open;
- archive;
- compare;
- change local metadata.

---

# 9.4 Change Detail

## Purpose

Concentrate all information about a change.

## Sections

- summary;
- lifecycle;
- proposal;
- design;
- specs;
- tasks;
- executions;
- verification;
- Git;
- metadata;
- diagnostics.

## Actions

- explore;
- propose;
- continue;
- fast-forward;
- apply;
- verify;
- sync;
- archive;
- open editor;
- view diff;
- block;
- cancel process.

---

# 9.5 Runner

## Purpose

Execute an operation and show its output.

## Content

- operation;
- project;
- change;
- backend;
- model;
- approvals;
- sandbox;
- command or prompt;
- output;
- duration;
- status;
- affected files.

## Actions

- execute;
- cancel;
- copy output;
- export;
- clear;
- repeat.

---

# 9.6 Logs / Runs

## Purpose

Consult previous executions.

## Content

- history;
- filters;
- details;
- events;
- errors;
- files;
- results.

## Actions

- open;
- export;
- repeat;
- delete according to policy;
- mark for review.

---

# 9.7 Settings

## Purpose

Manage global and project configuration.

## Sections

- general;
- interface;
- projects;
- OpenSpec;
- agents;
- models;
- security;
- Git;
- history;
- themes;
- diagnostics.

---

# 9.8 Help

## Purpose

Show shortcuts and available actions.

## Content

- global shortcuts;
- view shortcuts;
- glossary;
- basic diagnostics;
- version.

---

# 10. Navigation

## 10.1 Principles

- Every main function must be accessible via keyboard.
- Active focus must be visible.
- Shortcuts must be context-dependent.
- Text fields must receive keys without interference.
- Dangerous actions must not use a single key without confirmation.
- `Esc` must close the current modal.
- `q` must exit when there is no modal capturing the action.
- `Ctrl+C` must cancel the active execution or request confirmation to exit.

## 10.2 Initial Global Shortcuts

| Key | Action |
|---|---|
| `1` | Board |
| `2` | Specs |
| `3` | Changes |
| `4` | Runner |
| `5` | Logs |
| `6` | Settings |
| `Ctrl+P` | Palette |
| `/` | Search |
| `r` | Refresh |
| `g` | Switch project |
| `?` | Help |
| `q` | Exit |
| `Esc` | Close modal |

## 10.3 Board

| Key | Action |
|---|---|
| `h/l` | Previous/next column |
| `j/k` | Next/previous card |
| `Enter` | Open change |
| `f` | Filters |
| `a` | Main contextual action |
| `b` | Block or unblock |
| `e` | Open in editor |

---

# 11. Kanban States

## 11.1 Draft

The change exists, but does not yet have a sufficient functional proposal.

Typical evidence:

- folder created;
- proposal absent or incomplete;
- base artifacts not available.

## 11.2 Planning

The proposal exists, but artifacts needed to begin implementation are missing.

Typical evidence:

- proposal present;
- design, delta specs, or tasks incomplete.

## 11.3 Ready

Required artifacts are available and implementation has not yet begun.

Typical evidence:

- proposal;
- design;
- delta specs;
- tasks;
- zero tasks completed;
- no blocks.

## 11.4 Applying

Implementation is in progress.

Typical evidence:

- at least one task completed;
- at least one task pending.

## 11.5 Verification

Tasks are complete and the change requires verification.

Typical evidence:

- all tasks complete;
- verification nonexistent, failed, or outdated.

## 11.6 Ready to Archive

Implementation and verification are complete.

Typical evidence:

- tasks complete;
- successful verification;
- artifacts unchanged since.

## 11.7 Blocked

There is a condition that prevents progress.

Examples:

- credentials;
- external dependency;
- validation error;
- Git conflict;
- pending decision;
- manual block.

`blocked` has visual precedence over active states, except `archived`.

## 11.8 Archived

The change is archived according to the actual OpenSpec structure.

## 11.9 Precedence Rule

```text
archived
blocked
ready-to-archive
verification
applying
ready
planning
draft
```

---

# 12. Kanban Functional Rules

1. Cards will not be freely moved to change methodological state.
2. State will be derived from evidence.
3. A future drag-and-drop may execute an action, but never silently edit the state.
4. The application will show state reasons.
5. A blocked change will retain its underlying methodological state.
6. An archived change will not appear among active ones unless explicitly filtered.
7. A verification is invalidated if relevant files change.
8. Progress is calculated from `tasks.md`.
9. Tasks are not duplicated in the local database.
10. Unknown states must be shown as diagnostics, not invented.

---

# 13. Execution Rules

## 13.1 Before Execution

The tool must validate:

- valid project;
- valid change;
- available operation;
- available backend;
- valid model;
- credentials;
- permissions;
- path;
- Git;
- active processes;
- version compatibility;
- configuration.

## 13.2 During Execution

The tool must:

- keep the UI responsive;
- show output;
- show duration;
- allow cancellation;
- watch files;
- prevent concurrent modifying executions;
- record events.

## 13.3 After Execution

The tool must:

- capture exit code;
- refresh the workspace;
- detect affected files;
- update lifecycle;
- record result;
- show warnings;
- not assume success based on the agent's text output.

---

# 14. Confirmation Rules

Confirmation is required for:

- apply;
- archive;
- modifying sync;
- deletion;
- worktree cleanup;
- execution with dirty working tree;
- execution with broad permissions;
- use of unvalidated backend;
- execution outside the detected project;
- configuration overwrite;
- closing with active process.

Confirmation may be omitted for:

- reading;
- search;
- filters;
- navigation;
- healthcheck;
- informational commands;
- preview;
- diagnostics.

---

# 15. Empty States and Errors

## 15.1 Project Not Found

The tool must offer:

- select folder;
- open recent;
- initialize OpenSpec;
- exit.

## 15.2 Invalid Project

It must show:

- path;
- failed validations;
- expected files;
- possible actions.

## 15.3 No Active Changes

It must show:

```text
No active changes.

[n] Create change
[a] View archived
[s] Explore specs
```

## 15.4 Backend Not Available

It must show:

- name;
- executable;
- error;
- diagnostic action;
- how to configure.

## 15.5 Failed Execution

It must show:

- operation;
- backend;
- exit code;
- summary;
- last lines;
- link to log;
- option to retry.

## 15.6 Unexpected Error

It must:

- avoid closing the application when recoverable;
- log stack trace;
- show understandable message;
- offer diagnostic export;
- avoid exposing secrets.

---

# 16. Functional Configuration

## 16.1 Hierarchy

```text
defaults
  < global configuration
  < project configuration
  < environment variables
  < CLI arguments
  < session overrides
```

## 16.2 Global Configuration

Must include:

- theme;
- editor;
- recent projects;
- default backend;
- timeout;
- history;
- confirmation preferences;
- visual configuration.

## 16.3 Per-Project Configuration

Must include:

- display name;
- preferred backend;
- model per operation;
- Git policies;
- columns;
- tags;
- security rules;
- allowed commands.

## 16.4 Secrets

Must not be stored in TOML.

Allowed:

- keyring;
- environment variables;
- provider mechanisms.

---

# 17. Persistence

## 17.1 Local Persistence

SQLite must store:

- known projects;
- executions;
- events;
- affected files;
- verifications;
- sessions;
- operational metadata.

## 17.2 Retention

Retention must be configurable.

Suggested values:

- history: 90 days;
- full logs: 30 days;
- summaries: 180 days;
- critical events: until manual deletion.

## 17.3 Non-Persisted Data

No canonical copies will be persisted of:

- specs;
- proposals;
- designs;
- tasks;
- delta specs;
- archived changes.

---

# 18. MVP Acceptance Criteria

The functional MVP corresponds to version 0.3.

## 18.1 Project

- Detects root.
- Allows explicit path.
- Handles invalid project.
- Opens recent project.

## 18.2 Reading

- Reads specs.
- Reads active changes.
- Reads archived.
- Reads proposal.
- Reads design.
- Reads tasks.
- Reads delta specs.
- Shows diagnostics.

## 18.3 UI

- Works with keyboard.
- Has Board.
- Has Specs.
- Has Change Detail.
- Has Runner.
- Has Logs.
- Has Settings.
- Renders Markdown.
- Supports narrow terminals with controlled degradation.

## 18.4 Kanban

- Shows states.
- Shows progress.
- Shows reasons.
- Updates on filesystem changes.
- Filters and searches.
- Does not duplicate OpenSpec state.

## 18.5 Execution

- Detects OpenSpec CLI.
- Executes local commands.
- Detects Codex CLI.
- Executes OPSX actions.
- Shows live output.
- Cancels.
- Records.
- Refreshes.

## 18.6 Security

- Does not use `shell=True`.
- Does not save secrets in TOML.
- Validates paths.
- Shows risks.
- Confirms modifying actions.
- Blocks incompatible concurrency.
- Inspects Git.

## 18.7 Quality

- Python 3.11 compatible.
- Unit tests.
- Integration tests.
- TUI tests.
- Ruff.
- MyPy.
- Pytest.
- Updated documentation.

---

# 19. MVP Exclusion Criteria

The MVP shall not be considered incomplete for not including:

- drag-and-drop;
- multiple direct providers;
- external plugins;
- automatic worktrees;
- community themes;
- collaboration;
- remote synchronization;
- visual spec editor;
- web dashboard;
- advanced metrics.

---

# 20. Success Metrics

OPSX TUI will be functionally successful when:

1. A user can open a project without knowing its exact structure.
2. They can identify in under a minute which changes are active.
3. They can explain why each change has its state.
4. They can execute an OPSX flow from the TUI.
5. They can review the result without leaving the application.
6. They can recover the context of a previous execution.
7. They can detect a risk before modifying the repository.
8. They can operate with keyboard.
9. The tool does not duplicate OpenSpec's source of truth.
10. Failures are observable and recoverable.

---

# 21. Mandatory Constraints for the Agent

The implementing agent must not:

- change the package name;
- change the command;
- replace Textual;
- lower the minimum version below Python 3.11;
- use `shell=True`;
- allow direct UI access to the filesystem;
- allow direct UI access to subprocesses;
- save API keys in TOML;
- create manual Kanban states as source of truth;
- duplicate tasks in SQLite;
- assume success from textual output;
- hide commands from the user;
- execute destructive actions without confirmation;
- create a plugin framework before there is a real need;
- add dependencies without justifying their purpose;
- implement functions outside the active phase.

---

# 22. Executive Summary

OPSX TUI must be a terminal tool centered on three functions:

```text
See
Understand
Operate
```

It must begin as a reliable viewer, evolve into an OpenSpec controller, and finally incorporate agents and providers.

The functional contract can be summarized as follows:

```text
OPSX TUI opens an OpenSpec project,
faithfully represents its specs and changes,
explains their state,
allows operating on them,
keeps the user in control,
and records every execution.
```

This document must be used as base context together with:

- phase plan;
- architectural decisions;
- domain model;
- OpenSpec integration contract;
- lifecycle rules;
- testing strategy;
- security model.
