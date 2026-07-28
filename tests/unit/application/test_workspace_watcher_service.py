from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from opsx_tui.application.workspace_watcher_service import WorkspaceWatcherService
from opsx_tui.domain.logging import Logger
from opsx_tui.domain.ports import WorkspaceObserver
from opsx_tui.domain.workspace import WorkspaceSnapshot
from tests.fixtures.watcher import FakeWorkspaceObserver


def _make_snapshot(
    root: Path = Path("/test"),
    fingerprint: str = "fp1",
) -> WorkspaceSnapshot:
    return WorkspaceSnapshot(
        root=root,
        openspec_root=root / "openspec",
        config_yaml=True,
        specs=(),
        active_changes=(),
        archived_changes=(),
        diagnostics=(),
        fingerprint=fingerprint,
    )


def _make_service(
    observer: WorkspaceObserver | None = None,
    logger: Logger | None = None,
) -> tuple[WorkspaceWatcherService, FakeWorkspaceObserver, MagicMock]:
    fake_obs = observer if observer is not None else FakeWorkspaceObserver()
    log = logger if logger is not None else MagicMock(spec=Logger)
    ws_service = MagicMock()
    service = WorkspaceWatcherService(
        observer=fake_obs, logger=log, workspace_service=ws_service
    )
    return service, fake_obs, ws_service


class TestWorkspaceObserverContract:
    @pytest.mark.asyncio
    async def test_fake_observer_implements_protocol(self) -> None:
        observer: WorkspaceObserver = FakeWorkspaceObserver()
        assert isinstance(observer, FakeWorkspaceObserver)

    @pytest.mark.asyncio
    async def test_fake_observer_yields_notified_paths(self) -> None:
        observer = FakeWorkspaceObserver()
        paths = [Path("a.md"), Path("b.md")]

        async def consumer() -> None:
            async for batch in observer.watch(Path("/test")):
                assert batch == tuple(paths)
                break

        task = asyncio.create_task(consumer())
        await asyncio.sleep(0.02)
        await observer.notify(*paths)
        await asyncio.wait_for(task, timeout=2)

    @pytest.mark.asyncio
    async def test_fake_observer_cancellation(self) -> None:
        observer = FakeWorkspaceObserver()

        async def consumer() -> None:
            async for _ in observer.watch(Path("/test")):
                pass

        task = asyncio.create_task(consumer())
        await asyncio.sleep(0.02)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task


class TestDebounce:
    @pytest.mark.asyncio
    async def test_single_event_fires_callback_once(self) -> None:
        service, observer, ws_service = _make_service()
        sn = _make_snapshot(fingerprint="fp1")
        ws_service.read_snapshot.return_value = sn

        events: list[WorkspaceSnapshot] = []
        service.start(Path("/test"), events.append)

        await observer.notify(Path("a.md"))
        await asyncio.sleep(0.6)

        assert len(events) == 1
        assert events[0].fingerprint == "fp1"
        ws_service.read_snapshot.assert_called_once()
        await service.stop()

    @pytest.mark.asyncio
    async def test_rapid_events_fire_callback_once(self) -> None:
        service, observer, ws_service = _make_service()
        ws_service.read_snapshot.return_value = _make_snapshot(fingerprint="fp1")

        events: list[WorkspaceSnapshot] = []
        service.start(Path("/test"), events.append)

        await observer.notify(Path("a.md"))
        await asyncio.sleep(0.05)
        await observer.notify(Path("b.md"))
        await asyncio.sleep(0.05)
        await observer.notify(Path("c.md"))

        await asyncio.sleep(0.6)

        assert len(events) == 1
        ws_service.read_snapshot.assert_called_once()
        await service.stop()

    @pytest.mark.asyncio
    async def test_no_events_no_callback(self) -> None:
        service, observer, ws_service = _make_service()

        events: list[WorkspaceSnapshot] = []
        service.start(Path("/test"), events.append)

        await asyncio.sleep(0.6)

        assert len(events) == 0
        ws_service.read_snapshot.assert_not_called()
        await service.stop()


class TestFingerprint:
    @pytest.mark.asyncio
    async def test_unchanged_fingerprint_skips_callback(self) -> None:
        service, observer, ws_service = _make_service()
        sn = _make_snapshot(fingerprint="fp1")
        ws_service.read_snapshot.return_value = sn

        events: list[WorkspaceSnapshot] = []
        service.start(Path("/test"), events.append)

        await observer.notify(Path("a.md"))
        await asyncio.sleep(0.6)
        assert len(events) == 1

        await observer.notify(Path("b.md"))
        await asyncio.sleep(0.6)
        assert len(events) == 1

        await service.stop()

    @pytest.mark.asyncio
    async def test_changed_fingerprint_triggers_callback(self) -> None:
        service, observer, ws_service = _make_service()
        sn1 = _make_snapshot(fingerprint="fp1")
        sn2 = _make_snapshot(fingerprint="fp2")
        ws_service.read_snapshot.side_effect = [sn1, sn2]

        events: list[WorkspaceSnapshot] = []
        service.start(Path("/test"), events.append)

        await observer.notify(Path("a.md"))
        await asyncio.sleep(0.6)
        assert len(events) == 1

        await observer.notify(Path("b.md"))
        await asyncio.sleep(0.6)
        assert len(events) == 2
        assert events[1].fingerprint == "fp2"

        await service.stop()


class TestLifecycle:
    @pytest.mark.asyncio
    async def test_stop_cancels_task(self) -> None:
        service, observer, ws_service = _make_service()

        service.start(Path("/test"), lambda _: None)
        assert service._task is not None
        assert not service._task.done()

        await service.stop()
        assert service._task is None

    @pytest.mark.asyncio
    async def test_stop_without_start_is_noop(self) -> None:
        service, _, _ = _make_service()
        assert service._task is None

        await service.stop()
        assert service._task is None

    @pytest.mark.asyncio
    async def test_stop_no_callback_fired(self) -> None:
        service, observer, ws_service = _make_service()

        events: list[WorkspaceSnapshot] = []
        service.start(Path("/test"), events.append)

        await observer.notify(Path("a.md"))
        await service.stop()

        await asyncio.sleep(0.6)
        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_restart_after_stop(self) -> None:
        service, observer, ws_service = _make_service()
        ws_service.read_snapshot.return_value = _make_snapshot(fingerprint="fp1")

        events: list[WorkspaceSnapshot] = []
        service.start(Path("/test"), events.append)
        await service.stop()

        service.start(Path("/test"), events.append)
        await observer.notify(Path("a.md"))
        await asyncio.sleep(0.6)
        assert len(events) == 1

        await service.stop()


class TestErrorResilience:
    @pytest.mark.asyncio
    async def test_callback_error_logged_and_continues(self) -> None:
        service, observer, ws_service = _make_service()
        ws_service.read_snapshot.return_value = _make_snapshot(fingerprint="fp1")
        logger = MagicMock(spec=Logger)
        service = WorkspaceWatcherService(
            observer=observer,
            logger=logger,
            workspace_service=ws_service,
        )

        call_count = 0

        def callback(_: WorkspaceSnapshot) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("callback error")

        service.start(Path("/test"), callback)
        await observer.notify(Path("a.md"))
        await asyncio.sleep(0.6)
        assert call_count == 1
        logger.error.assert_called()

        await service.stop()


class TestFingerprintSkipOnTempEvents:
    @pytest.mark.asyncio
    async def test_fingerprint_unchanged_after_first(self) -> None:
        service, observer, ws_service = _make_service()
        sn = _make_snapshot(fingerprint="fp1")
        ws_service.read_snapshot.return_value = sn

        events: list[WorkspaceSnapshot] = []
        service.start(Path("/test"), events.append)

        await observer.notify(Path("temp.md~"))
        await asyncio.sleep(0.6)
        assert len(events) == 1  # First event always fires (gets initial fingerprint)

        ws_service.read_snapshot.return_value = _make_snapshot(fingerprint="fp1")
        await observer.notify(Path("temp.md~"))
        await asyncio.sleep(0.6)
        assert len(events) == 1  # Same fingerprint → skipped

        await service.stop()


class TestContainerWiring:
    def test_service_requires_observer(self) -> None:
        observer = FakeWorkspaceObserver()
        logger = MagicMock(spec=Logger)
        ws_service = MagicMock()
        service = WorkspaceWatcherService(
            observer=observer,
            logger=logger,
            workspace_service=ws_service,
        )
        assert service._observer is observer
        assert service._logger is logger
        assert service._workspace_service is ws_service
