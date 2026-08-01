## Purpose

Render the lifecycle state of active OpenSpec changes as a keyboard-navigable Kanban board in the Board tab: one column per lifecycle state, change cards with progress/artifact/metadata signals, deterministic ordering, and reactive refresh from the workspace watcher. The board is strictly read-only regarding lifecycle state — it never assigns or mutates a change's `ChangeStatus`.

---

## Requirements

### Requirement: Board view with lifecycle columns

The system SHALL render a Kanban board in the Board tab with one column per active lifecycle state: `draft`, `planning`, `ready`, `applying`, `verification`, `ready-to-archive`, `blocked`, in that order. Archived changes SHALL NOT appear on the board. An `unknown` column SHALL be rendered only when at least one change is assessed as `unknown`.

#### Scenario: Columns mirror lifecycle states
- **WHEN** the Board tab is active and the workspace has active changes in multiple states
- **THEN** the board SHALL show a column for each of draft, planning, ready, applying, verification, ready-to-archive, and blocked

#### Scenario: No archived changes on board
- **GIVEN** a workspace with archived changes
- **WHEN** the board is rendered
- **THEN** no archived change SHALL appear in any column

#### Scenario: Unknown column only when needed
- **WHEN** no change is assessed as `unknown`
- **THEN** no unknown column SHALL be rendered

---

### Requirement: Column ordering is fixed

Columns SHALL appear in the fixed order: Draft, Planning, Ready, Applying, Verification, Ready to Archive, Blocked, then Unknown (if present). The board SHALL NOT derive column order from a state machine or from stored state.

#### Scenario: Fixed column order
- **WHEN** the board is rendered
- **THEN** the first column SHALL be Draft and the last rendered state column SHALL be Blocked (followed by Unknown only if non-empty)

---

### Requirement: Change cards

The board SHALL render each active change as a card inside the column matching its assessed `ChangeStatus`. Each card SHALL display the change name, its state, its task progress, and artifact presence indicators.

#### Scenario: Card in matching column
- **GIVEN** a change assessed as `applying`
- **WHEN** the board is rendered
- **THEN** the change SHALL appear as a card in the Applying column

#### Scenario: Card shows name and state
- **WHEN** a card is rendered
- **THEN** the card SHALL show the change name and a state indicator (abbreviation) for the change's assessed state

#### Scenario: Card shows task progress
- **GIVEN** a change whose `parsed_tasks` has 3 of 7 tasks completed
- **WHEN** the card is rendered
- **THEN** the card SHALL show a progress indicator reflecting 3/7

#### Scenario: Card shows artifact indicators
- **GIVEN** a change with proposal and design present but delta specs missing
- **WHEN** the card is rendered
- **THEN** the card SHALL show a marker for each present artifact and a distinct marker for each missing artifact

#### Scenario: No-tasks rendering
- **GIVEN** a change with `parsed_tasks.total == 0` or no parsed tasks
- **WHEN** the card is rendered
- **THEN** the card SHALL NOT render 0% or 100% progress, and SHALL indicate that no tasks exist

---

### Requirement: Metadata signals on cards

Cards SHALL display metadata signals when present, matching the change-browser conventions: priority prefix for HIGH/URGENT, favorite star, and first tag (truncated). Card formatting SHALL be shared with the changes list so both widgets use the same formatting rules.

#### Scenario: Priority prefix
- **GIVEN** a change with priority URGENT
- **WHEN** the card is rendered
- **THEN** the card SHALL show the urgent marker before the change name

#### Scenario: Favorite star
- **GIVEN** a change with favorite True
- **WHEN** the card is rendered
- **THEN** the card SHALL show the favorite marker before the change name

#### Scenario: Shared formatting
- **WHEN** the board and the changes list both render the same change
- **THEN** they SHALL use the same formatting helpers for state abbreviation, progress, and metadata prefixes

---

### Requirement: Warning markers on cards

Cards SHALL display a warning marker when the change has diagnostics in `artifact_diagnostics` or is assessed as `blocked`.

#### Scenario: Diagnostic warning
- **GIVEN** a change with a non-empty `artifact_diagnostics`
- **WHEN** the card is rendered
- **THEN** the card SHALL show a warning indicator

#### Scenario: Blocked card marker
- **GIVEN** a change assessed as `blocked`
- **WHEN** the card is rendered
- **THEN** the card SHALL show an alert indicator and SHALL NOT hide the underlying methodological state

---

### Requirement: Vertical navigation within a column

The system SHALL support vertical navigation between cards inside the focused column using Up and Down arrow keys. The focused card SHALL be visually highlighted.

#### Scenario: Move focus down
- **GIVEN** a column with multiple cards and focus on the first card
- **WHEN** the user presses Down
- **THEN** focus SHALL move to the next card in the same column

#### Scenario: Move focus up
- **GIVEN** a column with focus on the second card
- **WHEN** the user presses Up
- **THEN** focus SHALL move to the previous card in the same column

#### Scenario: Focus highlight
- **WHEN** a card has focus
- **THEN** the focused card SHALL be visually distinguished from unfocused cards

---

### Requirement: Horizontal navigation between columns

The system SHALL support horizontal navigation between columns using Left and Right arrow keys. When focus is at the edge of a column and the user presses the corresponding arrow, focus SHALL move to the first card of the adjacent column (or the column header if the adjacent column is empty).

#### Scenario: Move to next column
- **GIVEN** focus on a card in the Draft column and a Planning column with at least one card
- **WHEN** the user presses Right
- **THEN** focus SHALL move to a card in the Planning column

#### Scenario: Move to previous column
- **GIVEN** focus on a card in the Applying column
- **WHEN** the user presses Left
- **THEN** focus SHALL move to a card in the previous column

#### Scenario: Edge handling on empty adjacent column
- **GIVEN** an adjacent column with no cards
- **WHEN** the user navigates into it
- **THEN** focus SHALL move to that column's header so the column remains reachable

---

### Requirement: Open change detail

The system SHALL open the change detail for the focused card when the user presses Enter. The detail SHALL be rendered by the existing `ChangeDetailPanel` for the selected change. Closing the detail SHALL return focus to the board preserving card selection.

#### Scenario: Enter opens detail
- **GIVEN** focus on a card
- **WHEN** the user presses Enter
- **THEN** a change detail view SHALL be shown for that change

#### Scenario: Escape closes detail
- **WHEN** the change detail is open and the user presses Escape
- **THEN** the detail SHALL close and focus SHALL return to the previously selected card

---

### Requirement: Reactive refresh

The board SHALL re-render when the workspace snapshot changes (as delivered by the workspace watcher). Card positions, column membership, counts, and progress SHALL reflect the latest snapshot.

#### Scenario: Change moves column after update
- **GIVEN** a change assessed as `ready`
- **WHEN** the workspace changes so the same change is assessed as `applying`
- **THEN** the board SHALL move that change's card to the Applying column

#### Scenario: New change appears
- **WHEN** a new active change appears in the workspace snapshot
- **THEN** the board SHALL render a card for it in the appropriate column

#### Scenario: Column count updates
- **GIVEN** a column header displaying a count of its cards
- **WHEN** a card enters or leaves that column on refresh
- **THEN** the header count SHALL update accordingly

---

### Requirement: Deterministic sorting within columns

The system SHALL sort cards within each column deterministically. Default sort key order SHALL be: priority descending, then blocked changes first, then favorite, then change name ascending. The user-assigned `metadata.order` SHALL take precedence over the default key when present. Sorting SHALL NOT alter lifecycle state.

#### Scenario: Priority sorts first
- **GIVEN** two cards in the same column with URGENT and NORMAL priority
- **WHEN** the column is rendered
- **THEN** the URGENT card SHALL appear before the NORMAL card

#### Scenario: Name tie-break
- **GIVEN** two cards in the same column with equal priority and no `metadata.order`
- **WHEN** the column is rendered
- **THEN** the card whose name sorts earlier SHALL appear first

#### Scenario: User order overrides
- **GIVEN** two cards in the same column with `metadata.order` 2 and 1 respectively
- **WHEN** the column is rendered
- **THEN** the card with order 1 SHALL appear first

#### Scenario: Sorting does not change state
- **WHEN** cards are re-sorted
- **THEN** each change's assessed `state` SHALL remain unchanged

---

### Requirement: Collapsible columns

The system SHALL allow the user to collapse and expand the focused column by pressing `c`. A collapsed column SHALL show only its header (including its card count) and SHALL hide its cards. Collapse state is a transient visual state and SHALL NOT be persisted and SHALL NOT affect lifecycle.

#### Scenario: Collapse hides cards
- **GIVEN** a focused column with cards
- **WHEN** the user presses `c`
- **THEN** the column SHALL hide its cards and show only the header

#### Scenario: Expand restores cards
- **GIVEN** a collapsed column with focus on its header
- **WHEN** the user presses `c` again
- **THEN** the column SHALL restore its cards

#### Scenario: Collapse is not persisted
- **WHEN** the application restarts or the board is rebuilt
- **THEN** columns SHALL render expanded by default

---

### Requirement: Narrow-terminal adaptation

The board SHALL remain usable on narrow terminals. When the total column width exceeds the available width, the board SHALL provide horizontal scrolling and columns SHALL remain reachable via horizontal navigation. Card content SHALL truncate rather than overflow the column width.

#### Scenario: Horizontal scroll on narrow terminals
- **GIVEN** a terminal narrower than the combined column widths
- **WHEN** the board is rendered
- **THEN** columns beyond the visible width SHALL be reachable by scrolling horizontally

#### Scenario: Card truncation
- **GIVEN** a card whose content exceeds the column width
- **WHEN** the card is rendered
- **THEN** the card SHALL truncate its content and SHALL NOT cause horizontal overflow of the column

---

### Requirement: No manual state assignment

The board SHALL NOT allow assigning lifecycle state by dragging or moving cards. No interaction on the board SHALL mutate a change's assessed `ChangeStatus`.

#### Scenario: No drag to reassign
- **WHEN** the user attempts to drag or move a card to a different column
- **THEN** the change's assessed state SHALL remain unchanged and no state assignment SHALL occur
