# Contributing to ai-copywriting-studio

Thanks for wanting to help build the pipeline. This repo is a Windows desktop
tool that turns raw briefs into finished copy through a staged worker
pipeline: **ingest → process → output**.

## Ground rules

- Python 3.11+ on Windows 10/11. Tests run on Linux CI too, so keep paths
  `pathlib`-based.
- One handler per brief source. One processor per copy stage. One driver per
  output target. Don't cross the streams.
- Every new stage ships with a unit test under `tests/pipeline/`.
- Type hints on all public functions. `mypy --strict` is enforced on `core/`.

## Layout

```
bootstrap/       app entry, CLI, tray launcher
ingest/          brief sources (file drop, clipboard, RSS, prompt file)
processors/      copy stages (outline, draft, rewrite, seo, tone, factcheck)
drivers/         output targets (clipboard, markdown, docx, wordpress, csv)
queue/           job queue, worker pool, retry policy
models/          LLM client wrappers + prompt templates
config/          settings loader, schema, defaults
utils/           logging, text helpers, token counting, rate limit
docs/            architecture notes
tests/           pytest suites
```

## Adding a processor

1. Subclass `processors.base.CopyProcessor`.
2. Implement `process(brief: Brief, ctx: PipelineContext) -> Draft`.
3. Register it in `processors/registry.py` with a stable `stage_id`.
4. Add fixtures under `tests/fixtures/` and a test.

## Adding a driver

Drivers receive a `Draft` and a `DriverConfig`. They must be idempotent and
must not mutate the incoming draft. Return a `DriverResult` with a status
and any side-effect metadata (path written, bytes emitted).

## Style

- `ruff` for lint, `black` for format, line length 100.
- No bare `except:`. Catch specific exceptions; log with `utils.logging`.
- No secrets in code. Use `config/local.toml` (gitignored).

## PR checklist

- [ ] Tests pass locally (`pytest -q`).
- [ ] `ruff check .` clean.
- [ ] `mypy core/ processors/` clean.
- [ ] Docs updated if a stage or driver was added.