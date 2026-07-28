## ADDED Requirements

### Requirement: Print summary
The system SHALL print a summary of all requirements and scenarios.

#### Scenario: No requirements
- **WHEN** there are no requirements
- **THEN** the summary says "No requirements found"

#### Scenario: One requirement with scenarios
- **WHEN** there is one requirement with two scenarios
- **THEN** the summary shows the requirement name and both scenario names

### Requirement: Validate input
The system SHALL validate all input before processing.

#### Scenario: Empty input
- **WHEN** the input is empty
- **THEN** the system returns an error

### Requirement: Log operations
The system SHALL log all operations.

#### Scenario: Operation logged
- **WHEN** an operation completes
- **THEN** a log entry is created
