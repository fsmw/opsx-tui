## Purpose

Filter the workspace's changes and board by lifecycle state, text, tag, and archive visibility. Filtering is purely presentational: criteria are AND-ed, active filters are indicated, a single action clears them, and no filter operation mutates change state, metadata, artifacts, or any canonical OpenSpec data.

---

## Requirements

### Requirement: Filter by state

The system SHALL filter changes by lifecycle state using a multi-select state filter. When the state filter is empty, changes of all states SHALL be included.

#### Scenario: Single state filter
- **GIVEN** active changes in states draft, ready, and applying
- **WHEN** the user selects only the `ready` state
- **THEN** only changes assessed as `ready` SHALL be shown

#### Scenario: Multiple states
- **GIVEN** active changes in states draft, ready, and applying
- **WHEN** the user selects `draft` and `applying`
- **THEN** changes in draft and applying SHALL be shown and ready changes SHALL be hidden

#### Scenario: Empty state filter means all
- **WHEN** no state is selected in the filter
- **THEN** changes of every state SHALL be shown

### Requirement: Filter by text

The system SHALL filter changes by case-insensitive text matching against the change name. An empty text filter SHALL match all changes.

#### Scenario: Text substring match
- **GIVEN** changes named `fix-bug`, `add-feature`, and `board-refactor`
- **WHEN** the user enters `feat`
- **THEN** `add-feature` SHALL be shown and the others SHALL be hidden

#### Scenario: Case-insensitive match
- **GIVEN** a change named `Auth-Fix`
- **WHEN** the user enters `auth`
- **THEN** the change SHALL be shown

#### Scenario: Empty text shows all
- **WHEN** the text filter is empty
- **THEN** all changes SHALL be shown

### Requirement: Filter by tag

The system SHALL filter changes by tags from the change metadata. When multiple tags are provided, a change SHALL match only if it has every tag. Changes without metadata SHALL NOT match a non-empty tag filter.

#### Scenario: Single tag filter
- **GIVEN** changes with tags `ui` and `backend`
- **WHEN** the user filters by tag `ui`
- **THEN** only changes tagged `ui` SHALL be shown

#### Scenario: Multiple tags require all
- **GIVEN** changes tagged (`ui`, `urgent`) and (`ui`,)
- **WHEN** the user filters by tags `ui` and `urgent`
- **THEN** only the change with both tags SHALL be shown

#### Scenario: No metadata never matches
- **GIVEN** a change with no metadata
- **WHEN** the user filters by any tag
- **THEN** that change SHALL be hidden

### Requirement: Show or hide archived changes

The system SHALL provide a toggle that includes or excludes archived changes. Archived changes SHALL be hidden by default. When included, archived changes SHALL be shown separately from active-state content and SHALL never appear in active lifecycle columns.

#### Scenario: Hidden by default
- **GIVEN** a workspace with archived changes
- **WHEN** no archive toggle is applied
- **THEN** archived changes SHALL NOT be shown

#### Scenario: Toggle includes archived
- **GIVEN** the archive toggle is enabled
- **WHEN** the user views the changes list
- **THEN** archived changes SHALL be shown separately from active changes

#### Scenario: Archived never in active columns
- **GIVEN** the archive toggle is enabled on the board
- **WHEN** the board is rendered
- **THEN** archived changes SHALL appear in a separate archived section and SHALL NOT appear in active lifecycle columns

### Requirement: Combined filters are AND-ed

When multiple filter criteria are active simultaneously, a change SHALL be shown only if it satisfies all of them.

#### Scenario: State and text combined
- **GIVEN** a change `fix-bug` in state `applying` and a change `fix-ui` in state `ready`
- **WHEN** the user filters by state `applying` and text `fix`
- **THEN** only `fix-bug` SHALL be shown

#### Scenario: State, text, and tag combined
- **GIVEN** a change tagged `ui` in state `ready` named `board-fix`
- **WHEN** the user filters by state `ready`, text `fix`, and tag `ui`
- **THEN** `board-fix` SHALL be shown

### Requirement: Indicate active filters

The system SHALL display an indicator of active filters whenever any filter criterion is set. When no filters are active, the system SHALL indicate that no filters are applied.

#### Scenario: Indicator when filters active
- **GIVEN** a text filter with a non-empty value
- **WHEN** the filter indicator is rendered
- **THEN** it SHALL indicate that filters are active

#### Scenario: Indicator when no filters
- **GIVEN** an empty state filter, empty text filter, empty tag filter, and the archive toggle off
- **WHEN** the filter indicator is rendered
- **THEN** it SHALL indicate that no filters are applied

### Requirement: Clear filters

The system SHALL provide a single action that clears all active filters at once, restoring the unfiltered view.

#### Scenario: Clear resets all criteria
- **GIVEN** state, text, and tag filters are active and the archive toggle is on
- **WHEN** the user clears filters
- **THEN** all criteria SHALL be reset to empty and the archive toggle SHALL return to its default (hidden)

#### Scenario: Clearing does not change lifecycle state
- **WHEN** filters are cleared
- **THEN** each change's assessed `state` SHALL remain unchanged

### Requirement: Filtering does not mutate data

Filtering SHALL be a purely presentational operation. It SHALL NOT modify change state, metadata, artifacts, or any canonical OpenSpec data.

#### Scenario: Filter leaves data intact
- **GIVEN** a filtered view
- **WHEN** filters change or are cleared
- **THEN** the underlying workspace snapshot and change metadata SHALL be unchanged

### Requirement: Board state filter hides columns

On the board, a non-empty state filter SHALL hide columns whose state is not selected. Clearing the state filter SHALL restore all columns.

#### Scenario: State filter hides non-matching columns
- **GIVEN** a board with Draft and Ready columns
- **WHEN** the user filters by state `ready`
- **THEN** the Draft column SHALL be hidden and the Ready column SHALL remain

#### Scenario: Clearing restores columns
- **GIVEN** the board with the state filter set to `ready`
- **WHEN** the user clears filters
- **THEN** the Draft column SHALL be restored

### Requirement: Board text and tag filters hide cards

On the board, text and tag filters SHALL hide cards that do not match while leaving columns visible (unless the state filter hides them).

#### Scenario: Text filter on board
- **GIVEN** a Ready column with cards `fix-bug` and `add-feature`
- **WHEN** the user filters by text `fix`
- **THEN** the card `fix-bug` SHALL remain and `add-feature` SHALL be hidden from that column

#### Scenario: Tag filter on board
- **GIVEN** a Ready column with a card tagged `urgent` and a card with no tags
- **WHEN** the user filters by tag `urgent`
- **THEN** only the tagged card SHALL remain
