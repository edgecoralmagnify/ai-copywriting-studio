"""Domain types shared across the pipeline.

A Brief flows through stages and accumulates Draft revisions. Drivers
consume the final Draft and emit to a target.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class Stage(str, Enum):
    OUTLINE = "outline"
    DRAFT = "draft"
    REWRITE = "rewrite"
    TONE = "tone"
    SEO = "seo"
    FACTCHECK = "factcheck"


class Brief(BaseModel):
    """Raw input. Everything downstream is derived from this."""

    source: str
    title: str
    body: str
    audience: str | None = None
    tone: str | None = None
    keywords: list[str] = Field(default_factory=list)
    word_target: int = 800
    metadata: dict[str, str] = Field(default_factory=dict)


class Draft(BaseModel):
    """A revision of copy produced by a processor."""

    brief_id: str
    stage: Stage
    text: str
    model: str
    tokens_in: int = 0
    tokens_out: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def char_count(self) -> int:
        return len(self.text)


class PipelineContext(BaseModel):
    """Mutable context threaded through the stage chain."""

    brief: Brief
    drafts: list[Draft] = Field(default_factory=list)
    export_dir: Path
    stops: set[Stage] = Field(default_factory=set)

    def latest(self) -> Draft | None:
        return self.drafts[-1] if self.drafts else None

    def append(self, draft: Draft) -> None:
        self.drafts.append(draft)