## Purpose

Define performance requirements for the OPSX TUI so that the UI remains responsive while interacting with the file system.

## Requirements

### Requirement: Non-blocking UI operations
The system SHALL NOT perform synchronous file I/O operations on the main UI thread during workspace snapshot generation.

#### Scenario: File system operations
- **WHEN** the system reads workspace snapshot files during startup or watcher events
- **THEN** the operation is performed in a background thread without blocking the UI event loop
