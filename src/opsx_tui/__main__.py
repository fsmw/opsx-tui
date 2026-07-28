import argparse
import asyncio
import sys
from pathlib import Path

from opsx_tui.application.container import Container
from opsx_tui.presentation.app import OpsxTuiApp


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="opsx-tui",
        description="OPSX TUI - OpenSpec terminal UI",
    )
    parser.add_argument(
        "--project",
        type=Path,
        default=None,
        help="Path to an OpenSpec project root",
    )
    return parser.parse_args(argv)


def main() -> None:
    args = _parse_args()
    container = Container()
    app = OpsxTuiApp(container=container, project_arg=args.project)
    try:
        asyncio.run(app.run_async())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
