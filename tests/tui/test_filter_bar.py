from __future__ import annotations

from textual.app import App
from textual.widgets import Button, Checkbox, Input, Static

from opsx_tui.domain.filtering import ChangeFilter
from opsx_tui.domain.status import ChangeStatus
from opsx_tui.presentation.widgets.filter_bar import FilterBar, FiltersChanged


class _Harness(App[None]):
    """App that records FiltersChanged messages bubbled from the FilterBar."""

    def __init__(self) -> None:
        super().__init__()
        self.messages: list[FiltersChanged] = []

    def on_filters_changed(self, event: FiltersChanged) -> None:
        self.messages.append(event)


async def test_filter_bar_composes() -> None:
    app = _Harness()
    async with app.run_test(size=(120, 24)):
        bar = FilterBar()
        await app.mount(bar)
        assert bar.query_one("#filter-text", Input)
        assert bar.query_one("#filter-tags", Input)
        assert bar.query_one("#filter-archived", Checkbox)
        assert bar.query_one("#filter-indicator", Static)
        assert bar.query_one("#filter-clear", Button)


async def test_text_input_posts_filters_changed() -> None:
    app = _Harness()
    async with app.run_test(size=(120, 24)) as pilot:
        bar = FilterBar()
        await app.mount(bar)
        text = bar.query_one("#filter-text", Input)
        bar.on_input_changed(Input.Changed(input=text, value="bug"))
        await pilot.pause()
        assert app.messages and app.messages[-1].filt.text == "bug"


async def test_tags_parse_comma_separated() -> None:
    app = _Harness()
    async with app.run_test(size=(120, 24)) as pilot:
        bar = FilterBar()
        await app.mount(bar)
        tags = bar.query_one("#filter-tags", Input)
        bar.on_input_changed(Input.Changed(input=tags, value="ui, core "))
        await pilot.pause()
        assert app.messages and app.messages[-1].filt.tags == ("ui", "core")


async def test_archive_checkbox_sets_include_archived() -> None:
    app = _Harness()
    async with app.run_test(size=(120, 24)) as pilot:
        bar = FilterBar()
        await app.mount(bar)
        archived = bar.query_one("#filter-archived", Checkbox)
        bar.on_checkbox_changed(Checkbox.Changed(archived, True))
        await pilot.pause()
        assert app.messages and app.messages[-1].filt.include_archived is True


async def test_state_checkbox_sets_states() -> None:
    app = _Harness()
    async with app.run_test(size=(120, 24)) as pilot:
        bar = FilterBar()
        await app.mount(bar)
        draft = bar.query_one("#filter-state-draft", Checkbox)
        bar.on_checkbox_changed(Checkbox.Changed(draft, True))
        await pilot.pause()
        assert app.messages and app.messages[-1].filt.states == frozenset(
            {ChangeStatus.DRAFT}
        )


async def test_clear_resets_filter_and_posts() -> None:
    app = _Harness()
    async with app.run_test(size=(120, 24)) as pilot:
        bar = FilterBar()
        await app.mount(bar)
        bar._filter = ChangeFilter(text="x", include_archived=True)
        bar.query_one("#filter-clear", Button).press()
        await pilot.pause()
        assert bar._filter == ChangeFilter()
        assert app.messages and app.messages[-1].filt == ChangeFilter()


async def test_indicator_shows_active_count() -> None:
    app = _Harness()
    async with app.run_test(size=(120, 24)):
        bar = FilterBar()
        await app.mount(bar)
        indicator = bar.query_one("#filter-indicator", Static)
        assert "no filters" in str(indicator.render())
        bar._filter = ChangeFilter(text="x", include_archived=True)
        bar._post_filters_changed()
        assert "2 filter" in str(indicator.render())


async def test_clear_resets_widget_values() -> None:
    app = _Harness()
    async with app.run_test(size=(120, 24)) as pilot:
        bar = FilterBar()
        await app.mount(bar)
        bar.query_one("#filter-text", Input).value = "query"
        bar.query_one("#filter-archived", Checkbox).value = True
        bar.query_one("#filter-clear", Button).press()
        await pilot.pause()
        assert bar.query_one("#filter-text", Input).value == ""
        assert bar.query_one("#filter-archived", Checkbox).value is False
