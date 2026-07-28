## 1. Change list view

- [ ] 1.1 Implement `ChangesView` with split-panel layout: `Input` search top, `ListView` left (40%), `ScrollableContainer` right (60%)
- [ ] 1.2 Display active changes first, then archived changes with a divider label between them
- [ ] 1.3 Each `ListItem` shows: change name, state badge, progress string, artifact indicator icons
- [ ] 1.4 Handle empty state: show "No changes" label

## 2. Search filter

- [ ] 2.1 Wire `Input.Changed` handler to rebuild `ListView` items based on name substring match
- [ ] 2.2 Reset filter on empty input — show all changes
- [ ] 2.3 Bind `/` to focus the search `Input`

## 3. Detail panel content

- [ ] 3.1 Create `ChangeDetailContent` static builder with `for_change(change)` returning formatted text
- [ ] 3.2 Include Proposal section (Why, What Changes, Capabilities, Impact) when `parsed_proposal` exists
- [ ] 3.3 Include Design Decisions section (list decision titles and bodies) when `parsed_design` exists
- [ ] 3.4 Include Delta Specs section listing each delta spec's title when `delta_specs` non-empty
- [ ] 3.5 Include Tasks section with progress bar + task list when `parsed_tasks` exists
- [ ] 3.6 Include Diagnostics section when `artifact_diagnostics` non-empty
- [ ] 3.7 Include Unknown files section listing non-recognized files in the change directory
- [ ] 3.8 Only show a section if its corresponding `parsed_*` field is non-None or data is non-empty

## 4. ListView selection to detail

- [ ] 4.1 Wire `ListView.Selected` handler to update detail content from selected change
- [ ] 4.2 Ensure detail updates when Enter is pressed (same as click)
- [ ] 4.3 Store `(change, ChangeDetailContent.for_change(change))` pair per list item

## 5. Keyboard navigation

- [ ] 5.1 Up/down arrows move selection natively via `ListView`
- [ ] 5.2 `/` key focuses search `Input`
- [ ] 5.3 Escape from search returns focus to change list

## 6. Reactive refresh

- [ ] 6.1 Rebuild change list in `on_mount` from `opsx_project.workspace`
- [ ] 6.2 Support `refresh()` through shell screen's workspace update path

## 7. Tests

- [ ] 7.1 Test change list shows active before archived
- [ ] 7.2 Test list items show state badge and progress
- [ ] 7.3 Test empty changes list shows message
- [ ] 7.4 Test detail panel shows all sections for complete change
- [ ] 7.5 Test detail panel omits sections for missing artifacts
- [ ] 7.6 Test detail shows diagnostics
- [ ] 7.7 Test detail shows unknown files
- [ ] 7.8 Test search filter matches by name
- [ ] 7.9 Test empty search shows all
- [ ] 7.10 Test search `/` key focuses input
- [ ] 7.11 Test arrow keys navigate list
- [x] 7.12 Test all existing tests still pass

## 8. Quality verification

- [x] 8.1 Run `ruff check .` and fix issues
- [x] 8.2 Run `mypy src` and fix issues
- [x] 8.3 Verify all existing tests still pass