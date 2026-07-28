## ADDED Requirements

### Requirement: Handle errors
The system SHALL handle errors gracefully.

#### Scenario: Error caught
- **WHEN** an error occurs
- **THEN** it is caught and logged

#### Scenario: Missing when
- **THEN** this scenario has no WHEN clause

#### Scenario: Recovered
- **WHEN** the system recovers
- **THEN** normal operation resumes

### Requirement: with empty name

- **WHEN** no name is given
- **THEN** the requirement has empty name

#### Scenario: Empty name handled
- **WHEN** the name is empty
- **THEN** a warning is emitted
