## ADDED Requirements

### Requirement: ChangeMetadata model
The system SHALL provide a `ChangeMetadata` frozen Pydantic model with fields: priority (IntEnum 0-4), tags (tuple of strings), favorite (bool), blocked_reason (optional str), notes (optional str), order (int).

#### Scenario: Default values
- **WHEN** a `ChangeMetadata` is created with no arguments
- **THEN** priority SHALL be NORMAL(0), tags SHALL be empty, favorite SHALL be False, blocked_reason SHALL be None, notes SHALL be None, order SHALL be 0

#### Scenario: Priority validation
- **WHEN** priority is set to URGENT(4)
- **THEN** the model SHALL accept the value without error

#### Scenario: Frozen immutability
- **WHEN** attempting to modify a field after construction
- **THEN** Pydantic SHALL raise a FrozenInstanceError

### Requirement: MetadataStore Protocol
The system SHALL define a `MetadataStore` Protocol in domain/ports.py with methods: `load_all() -> dict[str, ChangeMetadata]`, `save(change_name: str, metadata: ChangeMetadata) -> None`, `delete(change_name: str) -> None`.

#### Scenario: Protocol contract
- **WHEN** a class implements `MetadataStore`
- **THEN** the protocol SHALL accept it as a valid implementation

### Requirement: TomlMetadataStore adapter
The system SHALL provide a `TomlMetadataStore` in infrastructure that persists metadata in `~/.local/share/opsx-tui/metadata/<project-hash>.toml`.

#### Scenario: Load empty store
- **WHEN** no TOML file exists yet
- **THEN** `load_all()` SHALL return an empty dict

#### Scenario: Save and reload
- **WHEN** metadata is saved for a change and then loaded
- **THEN** the returned metadata SHALL match the saved values

#### Scenario: Delete removes section
- **WHEN** a change's metadata is deleted and the file is reloaded
- **THEN** the change SHALL no longer appear in `load_all()`

#### Scenario: Corrupt file handling
- **WHEN** the TOML file contains invalid syntax
- **THEN** `load_all()` SHALL return an empty dict and not raise

### Requirement: Change model extension
The Change model SHALL gain an optional `metadata: ChangeMetadata | None` field.

#### Scenario: Backward compatibility
- **WHEN** a Change is created without metadata
- **THEN** it SHALL serialize and deserialize without error (metadata defaults to None)

#### Scenario: Metadata preserved in snapshot
- **WHEN** a Change with metadata is included in a WorkspaceSnapshot
- **THEN** the snapshot SHALL preserve the metadata field

### Requirement: Metadata merge service
The system SHALL provide a pure function `merge_metadata(snapshot, metadata_dict)` that returns a new WorkspaceSnapshot with metadata attached to matching changes.

#### Scenario: Active changes merged
- **WHEN** metadata_dict contains an entry matching an active change name
- **THEN** that change SHALL have metadata populated

#### Scenario: Archived changes merged
- **WHEN** metadata_dict contains an entry matching an archived change name
- **THEN** that change SHALL have metadata populated

#### Scenario: No matching entry
- **WHEN** a change has no entry in metadata_dict
- **THEN** its metadata SHALL remain None

#### Scenario: Pure function
- **WHEN** merge_metadata is called
- **THEN** the original snapshot SHALL remain unmodified

### Requirement: Priority indicators in ChangesView
The change list items SHALL display priority prefix (`[U]` for URGENT, `[H]` for HIGH), favorite star (`★`), and first tag (truncated to 10 chars) when metadata is present.

#### Scenario: High priority shown
- **WHEN** a change has priority HIGH or URGENT
- **THEN** the list SHALL show `[H]` or `[U]` before the change name

#### Scenario: Favorite shown
- **WHEN** a change has favorite=True
- **THEN** the list SHALL show `★` before the change name

#### Scenario: Tags shown
- **WHEN** a change has tags
- **THEN** the list SHALL show the first tag (truncated) after the change name

### Requirement: Metadata in Overview tab
The Overview tab in ChangeDetailPanel SHALL display a metadata section when metadata is present.

#### Scenario: All fields displayed
- **WHEN** a change has metadata with all fields populated
- **THEN** the Overview tab SHALL show priority name, favorite status, tags, blocked_reason, and notes

#### Scenario: No metadata section
- **WHEN** a change has no metadata
- **THEN** the Overview tab SHALL not show a metadata section

### Requirement: MetadataEditModal
The system SHALL provide a modal screen for editing change metadata, with inputs for tags (comma-separated), notes, blocked_reason, priority cycler, and favorite toggle.

#### Scenario: Save persists metadata
- **WHEN** the user edits fields and confirms
- **THEN** the MetadataStore SHALL persist the new metadata

#### Scenario: Cancel discards changes
- **WHEN** the user presses Escape
- **THEN** no changes SHALL be persisted

#### Scenario: Keyboard shortcuts
- **WHEN** the user presses `f`
- **THEN** favorite SHALL toggle

### Requirement: Visual ordering
The ChangesView SHALL sort changes by `metadata.order` (ascending), then by change name, for both active and archived changes.

#### Scenario: Order respected
- **WHEN** two changes have order 1 and 2
- **THEN** the change with order 1 SHALL appear first

#### Scenario: Unset order
- **WHEN** a change has no metadata
- **THEN** it SHALL appear after all changes with explicit order

### Requirement: No new dependencies
The implementation SHALL NOT add new Python packages. It SHALL use `tomllib` (stdlib ≥3.11), `platformdirs` (existing), `hashlib` (stdlib), and `pathlib` (stdlib).

#### Scenario: Import check
- **WHEN** the project is installed
- **THEN** no new package SHALL be required beyond existing dependencies
