## 1. Directory structure

- [x] 1.1 Create `presentation/widgets/` with `__init__.py`
- [x] 1.2 Create `presentation/views/` with `__init__.py`

## 2. Shell chrome widgets

- [x] 2.1 Create `presentation/widgets/opsx_header.py` with `OpsxHeader(Widget)` — app name left, project path center (truncated >50), active view right
- [x] 2.2 Implement `render()` or `compose()` for `OpsxHeader` with reactive `active_view: reactive[str]`
- [x] 2.3 Create `presentation/widgets/opsx_footer.py` with `OpsxFooter(Footer)` — wrapping Textual `Footer` with shell bindings

## 3. Six empty views

- [x] 3.1 Create `presentation/views/board_view.py` — `BoardView(Widget)` with centered "Board" label
- [x] 3.2 Create `presentation/views/specs_view.py` — `SpecsView(Widget)` with centered "Specs" label
- [x] 3.3 Create `presentation/views/changes_view.py` — `ChangesView(Widget)` with centered "Changes" label
- [x] 3.4 Create `presentation/views/run_view.py` — `RunView(Widget)` with centered "Runner" label
- [x] 3.5 Create `presentation/views/logs_view.py` — `LogsView(Widget)` with centered "Logs" label
- [x] 3.6 Create `presentation/views/settings_view.py` — `SettingsView(Widget)` with centered "Settings" label

## 4. Shell screen

- [x] 4.1 Create `presentation/shell_screen.py` — `ShellScreen(Screen)` with `__init__(self, opsx_project: OpenSpecProject)`
- [x] 4.2 Compose `ShellScreen`: `OpsxHeader` dock top, `TabbedContent` (6 `TabPane` views) in center, `OpsxFooter` dock bottom
- [x] 4.3 Wire key bindings: `1`–`6` to switch tabs, `q` quit, `?` help, `ctrl+c` quit
- [x] 4.4 Implement `action_switch_view(view: str)` — sets `TabbedContent.active`, updates header `active_view`
- [x] 4.5 Update header `active_view` reactive on tab change via `on_tabbed_content_tab_activated`

## 5. Help modal

- [x] 5.1 Create `presentation/help_modal.py` — `HelpModal(Screen)` with keyboard bindings table
- [x] 5.2 Implement dismiss-on-any-key via `on_key` calling `self.dismiss()`

## 6. Error modal

- [x] 6.1 Create `presentation/error_modal.py` — `ErrorModal(Screen)` with error message and exit button

## 7. App flow update

- [x] 7.1 Modify `OpsxTuiApp._load_workspace` to push `ShellScreen(opsx_project)` instead of `"welcome"`
- [x] 7.2 Remove `WelcomeScreen` class from `app.py`
- [x] 7.3 Remove `InteractiveProjectScreen` import and all interactive screen usage from app.py; replace with exit on no project
- [x] 7.4 Remove `presentation/project_screen.py` file
- [x] 7.5 Remove `presentation/cli_arg_discoverer.py` (unused after interactive removal — CLI discovery is via `__main__.py` argparse)
- [x] 7.6 Remove the `SCREENS` dict from `OpsxTuiApp` (no longer needed; `push_screen` takes class directly)

## 8. Tests

- [x] 8.1 Test `OpsxHeader` renders with app name, project path, active view
- [x] 8.2 Test `OpsxHeader` truncates long project paths
- [x] 8.3 Test `OpsxHeader` reactive `active_view` updates on change
- [x] 8.4 Test each view widget renders its title label
- [x] 8.5 Test `ShellScreen` composes all chrome elements
- [x] 8.6 Test key `1`–`6` switches tabs in `ShellScreen`
- [x] 8.7 Test key `q` exits app
- [x] 8.8 Test `?` pushes `HelpModal`
- [x] 8.9 Test `HelpModal` dismisses on any key
- [x] 8.10 Test `ErrorModal` displays error message
- [x] 8.11 Test app flow: successful load pushes `ShellScreen`
- [x] 8.12 Test app flow: no valid project exits cleanly
- [x] 8.13 Test all existing tests still pass

## 9. Quality verification

- [x] 9.1 Run `ruff check .` and fix issues
- [x] 9.2 Run `mypy src` and fix issues
- [x] 9.3 Verify all existing tests still pass