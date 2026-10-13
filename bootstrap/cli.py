"""Entry point for the ai-copywriting-studio desktop tool.

Parses args, loads config, spins up the worker pool, and runs the pipeline
for a single brief or a watched folder.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from config.settings import load_settings
from queue.pool import WorkerPool
from queue.job_store import JobStore
from utils.logging import configure_logging, get_logger

log = get_logger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ai-copywriting-studio")
    p.add_argument("brief", nargs="?", type=Path, help="Brief file or folder to process.")
    p.add_argument("--config", type=Path, default=None, help="Path to settings TOML.")
    p.add_argument("--watch", action="store_true", help="Watch the brief folder for new jobs.")
    p.add_argument("--workers", type=int, default=None, help="Override worker count.")
    p.add_argument("--version", action="store_true")
    return p


async def _run(args: argparse.Namespace) -> int:
    settings = load_settings(args.config)
    if args.workers:
        settings.queue.workers = args.workers

    store = JobStore(settings.queue.state_dir)
    pool = WorkerPool(settings, store)
    await pool.start()

    try:
        if args.brief and args.brief.is_file():
            await pool.submit_path(args.brief)
        elif args.brief and args.brief.is_dir():
            await pool.submit_folder(args.brief, watch=args.watch)
        else:
            log.warning("no brief provided; worker pool idling")
        await pool.drain()
    finally:
        await pool.stop()
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.version:
        from bootstrap import __version__

        print(f"ai-copywriting-studio {__version__}")
        return 0
    configure_logging()
    try:
        return asyncio.run(_run(args))
    except KeyboardInterrupt:
        log.info("interrupted; shutting down")
        return 130


if __name__ == "__main__":
    sys.exit(main())