"""Optional system-tray launcher for the desktop build.

Wraps the CLI in a pystray icon so the tool can run headless in the
background while watching a brief folder.
"""

from __future__ import annotations

import threading
from pathlib import Path

from bootstrap.cli import main as cli_main
from utils.logging import get_logger

log = get_logger(__name__)


class TrayLauncher:
    """Owns a background thread running the pipeline and a tray icon."""

    def __init__(self, brief_dir: Path, workers: int = 2) -> None:
        self._brief_dir = brief_dir
        self._workers = workers
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(
            target=cli_main,
            args=([str(self._brief_dir), "--watch", "--workers", str(self._workers)],),
            daemon=True,
            name="acs-pipeline",
        )
        self._thread.start()
        log.info("tray launcher started for %s", self._brief_dir)

    def stop(self) -> None:
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        log.info("tray launcher stopped")