## Context

The app currently pushes a bare `WelcomeScreen` after project discovery. There is no chrome, no navigation, no way to access different views. The construction plan defines 6 initial views (Board, Specs, Changes, Runner, Logs, Settings) and a shell to host them.

The existing `OpsxTuiApp` (122 lines) handles project discovery, workspace loading, watcher lifecycle, and screen pushing. This change must integrate the shell into that flow without breaking existing functionality.

## Goals / Non-Goals

**Goals:**
- A `ShellScreen` that hosts header, tab bar, content area, and footer.
- Custom `OpsxHeader` showing app name, project path, and active view title.
- Tab bar (horizontal, below header) for switching between 6 views.
- 6 empty view widgets (`BoardView`, `SpecsView`, `ChangesView`, `RunView`, `LogsView`, `SettingsView`).
- `HelpModal` as a screen overlay triggered by `?`.
- Keyboard navigation: `1`–`6` for views, `q` for quit, `?` for help.
- App pushes `ShellScreen` instead of `WelcomeScreen` after load.
- `WelcomeScreen` removed; `BoardView` replaces it as the default view.
- Error handling via `notify()` + `ErrorModal` for critical errors.

**Non-Goals:**
- Actual view content — all 6 views are empty placeholders (just a title label).
- Vim-style keyboard navigation (`h/j/k/l`) — deferred to `add-keyboard-navigation`.
- Search (`/`), command palette (`Ctrl+P`) — deferred.
- Mouse support — Textual handles this by default; no custom mouse logic.
- Markdown rendering — deferred to `add-markdown-preview`.
- Narrow-terminal adaptation — deferred.

## Decisions

### D1: Content-swap over screen-per-view
**Choice:** Single `ShellScreen` with a `Viewport`-style container that mounts/dismounts view widgets. The shell chrome (header, tabs, footer) stays mounted across navigations.
**Why:** Avoids re-mounting chrome on every view switch. Textual's `mount`/`remove` is fast for widgets. Screen-per-view would rebuild the entire DOM each time.
**Alternatives:** Separate `Screen` per view — rejected because chrome would flicker on every navigation.

### D2: Custom header over Textual built-in `Header`
**Choice:** `OpsxHeader` widget extending `Widget`, composed of horizontal containers with app name left, project path center (truncated), active view right.
**Why:** Need project path display (truncated for long paths), active view indicator, and app-specific styling. Textual's `Header` doesn't support custom content without overriding.
**Alternatives:** Textual `Header` with `sub_title` — rejected because it can't show project path cleanly.

### D3: Tab bar from `TabbedContent` widget
**Choice:** Use Textual's built-in `TabbedContent` with `TabPane` per view. `TabbedContent` natively handles tab switching, focus, and keyboard navigation.
**Why:** Zero-effort tab bar — Textual already implements click-to-switch, keyboard navigation (`Ctrl+Tab`), and accessibility. Saves implementing a custom tab widget.
**Alternatives:** Custom tab bar via `Button` widgets — rejected because it duplicates existing framework capability.

### D4: Views as `Widget` subclasses inside `TabPane`
**Choice:** Each view is a `Widget` subclass (e.g., `class BoardView(Widget)`) composed inside a `TabPane` within `TabbedContent`. Views receive `OpenSpecProject` reference for data access.
**Why:** `TabbedContent` expects `TabPane` children, which wraps any widget. Views are simple trees of Textual widgets; no screen lifecycle needed.
**Alternatives:** Views as `Screen` subclasses — rejected per D1. Views as standalone callables — rejected as not testable.

### D5: `HelpModal` as a `Screen` pushed on top
**Choice:** `HelpModal(Screen)` with keyboard bindings table, dismissable by pressing any key (via `key` method that pops the screen). Push via `app.push_screen()` when `?` is pressed.
**Why:** A pushed screen naturally overlays the current content. Textual handles the overlay rendering. Dismiss-on-any-key is simple: override `on_key` to `self.dismiss()`.
**Alternatives:** Inline overlay widget — rejected because screen push/pop is the Textual-idiomatic modal pattern.

### D6: `ErrorModal` for critical errors, `notify()` for transient
**Choice:** Critical errors (workspace load failure after initial load, watcher crash) use `ErrorModal(Screen)` with error message and a continue/exit choice. Transient errors use Textual's `self.notify()`.
**Why:** `notify()` is right for toast-style info (file not found, brief warnings). `ErrorModal` is right for blocking errors that need user attention.
**Alternatives:** Only `notify()` — rejected because some errors (workspace vanished) need more than a toast.

### D7: ShellScreen receives `OpenSpecProject` via constructor
**Choice:** `ShellScreen.__init__(self, opsx_project: OpenSpecProject)` stores the reference and passes it to each view on mount.
**Why:** Clean dependency injection — no globals, no app-level state coupling. Follows the existing pattern of passing data through constructors.
**Alternatives:** Store on `app` and access via `self.app.opsx_project` — rejected as implicit coupling.

### D8: Views directory layout
**Choice:** `presentation/views/` for view widgets, `presentation/widgets/` for shell chrome widgets (header, footer).
**Why:** Separate concerns — views are content, widgets are chrome. Avoids a flat `presentation/` directory with 10+ files.
**Alternatives:** All in `presentation/` — rejected as cluttered. Views in `presentation/screens/` — rejected because views aren't screens.

## Risks / Trade-offs

- **[Risk] `TabbedContent` styling** → May look different from the envisioned "tab bar below header" design. Textual's `TabbedContent` places tabs at the top inside a border. Acceptable for MVP; custom TCSS can adjust appearance.
- **[Risk] View memory** → 6 widgets mounted simultaneously inside `TabbedContent` consume memory even when not visible. Acceptable for 6 lightweight placeholder views; revisit if views become heavy.
- **[Trade-off] Tab switching via `TabbedContent`'s built-in navigation** → By using `TabbedContent`, we get tab switching for free but lose custom key bindings like `1`–`6`. Bindings can be added on the shell screen to call `self.query_one(TabbedContent).active = "board"` etc. This works.
- **[Trade-off] Dismiss-on-any-key for help** → Simple but may surprise users who press `?` again expecting toggle. Acceptable.
- **[Risk] TCSS complexity** → The shell layout (header + tabs + content + footer) needs TCSS that works across terminal sizes. Textual's CSS is powerful but can be tricky. Pinning Textual version reduces risk.