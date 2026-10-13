"""Stage-chain orchestrator.

Runs registered processors in order, threading a PipelineContext through
each. A processor may declare it `stops` the chain (e.g. factcheck fails
hard when a claim can't be verified and the config says fail-closed).
"""

from __future__ import annotations

from core.types import Brief, PipelineContext, Stage
from processors.base import CopyProcessor
from processors.registry import build_chain
from utils.logging import get_logger

log = get_logger(__name__)


class Pipeline:
    def __init__(self, stages: list[str], export_dir) -> None:
        self._chain: list[CopyProcessor] = build_chain(stages)
        self._export_dir = export_dir

    async def run(self, brief: Brief) -> PipelineContext:
        ctx = PipelineContext(brief=brief, export_dir=self._export_dir)
        for processor in self._chain:
            log.info("stage=%s brief=%s", processor.stage_id, brief.title)
            draft = await processor.process(brief, ctx)
            ctx.append(draft)
            if draft.stage in ctx.stops:
                log.warning("chain stopped at %s", draft.stage)
                break
        return ctx
</｜｜DSML｜｜ parameter>