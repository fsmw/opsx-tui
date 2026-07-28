## Why

The app currently opens a bare `WelcomeScreen` with a label and some stats — no navigation, no chrome, no way to access different views. Before any view (Board, Specs, Changes, Runner, Logs, Settings) can be built, there must be a shell that hosts them: a header, a navigation mechanism, a content area that swaps between views, a footer with keyboard hints, and a help overlay. This change builds that shell so every subsequent view has a place to live.

## What Changes

- Create `ShellScreen` — the main application screen that hosts the shell chrome (header, tab bar, content area, footer).
- Create a custom `OpsxHeader` widget with app name, project path, and active view title.
- Create a tab bar (or tab-like navigation row) below the header for switching between 6 views: **Board, Specs, Changes, Runner, Logs, Settings**.
- Create 6 empty view widgets — `BoardView`, `SpecsView`, `ChangesView`, `RunView`, `LogsView`, `SettingsView` — as `Widget` subclasses mounted into the content area.
- Create a `HelpModal` screen (overlay) triggered by `?`, dismissable with any key.
- Create `OpsxFooter` wrapping Textual's built-in `Footer` widget for binding display.
- Update `OpsxTuiApp` to push `ShellScreen` instead of `WelcomeScreen` after project discovery + workspace load. Pass `OpenSpecProject` to the shell screen.
- Remove `WelcomeScreen` (replaced by `ShellScreen` + `BoardView` as default).
- Wire keyboard navigation: `1`–`6` for views, `q` for quit, `?` for help, `Ctrl+C` for quit.
- Add error handling via Textual `notify()` for non-fatal errors and an `ErrorModal` screen for critical errors.
- Create `presentation/views/` directory to host the 6 view widgets.
- Create `presentation/widgets/` directory to host shell chrome widgets (header, footer).

## Capabilities

### New Capabilities
- `tui-shell`: Application shell with header, tab navigation, content area, footer, help modal, and 6 empty views.

### Modified Capabilities
- `project-foundation`: Update `OpsxTuiApp` to push `ShellScreen` instead of `WelcomeScreen` after load.

## Impact

- New files: `presentation/shell_screen.py`, `presentation/widgets/opsx_header.py`, `presentation/widgets/opsx_footer.py`, `presentation/views/*.py`, `presentation/help_modal.py`, `presentation/error_modal.py`.
- Modified files: `presentation/app.py` (app flow, bindings), `pyproject.toml` (TCSS if needed).
- Removed files: `presentation/project_screen.py` (WelcomeScreen replaced by BoardView).
- Does NOT implement actual view content — all 6 views are empty placeholders.
- Does NOT add keyboard navigation beyond view switching (`1-6`), quit (`q`), and help (`?`). Other bindings (search, palette, vim arrows) are deferred.