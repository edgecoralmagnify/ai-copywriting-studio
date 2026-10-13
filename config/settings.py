"""Settings loader and schema for ai-copywriting-studio.

Layers, in order of precedence:
    defaults -> config/default.toml -> config/local.toml -> env overrides
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from pydantic import BaseModel, Field

CONFIG_DIR = Path(__file__).resolve().parent


class ModelSettings(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(1024, ge=64, le=8192)
    timeout_s: float = 60.0
    api_key_env: str = "ACS_API_KEY"


class QueueSettings(BaseModel):
    workers: int = Field(2, ge=1, le=16)
    max_retries: int = Field(3, ge=0, le=10)
    backoff_base_s: float = 1.5
    state_dir: Path = Path("data/jobs")


class OutputSettings(BaseModel):
    export_dir: Path = Path("data/exports")
    default_drivers: list[str] = Field(default_factory=lambda: ["markdown", "clipboard"])
    wordpress_url: str | None = None


class Settings(BaseModel):
    model: ModelSettings = Field(default_factory=ModelSettings)
    queue: QueueSettings = Field(default_factory=QueueSettings)
    output: OutputSettings = Field(default_factory=OutputSettings)
    stages: list[str] = Field(
        default_factory=lambda: ["outline", "draft", "tone", "seo", "factcheck"]
    )


def _merge(base: dict, overlay: dict) -> dict:
    out = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def _read_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("rb") as fh:
        return tomllib.load(fh)


def load_settings(explicit: Path | None = None) -> Settings:
    data: dict = _read_toml(CONFIG_DIR / "default.toml")
    if explicit is not None:
        data = _merge(data, _read_toml(explicit))
    else:
        data = _merge(data, _read_toml(CONFIG_DIR / "local.toml"))

    env_model = os.getenv("ACS_MODEL")
    if env_model:
        data.setdefault("model", {})["model"] = env_model

    return Settings.model_validate(data)