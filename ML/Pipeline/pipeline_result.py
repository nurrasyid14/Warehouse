from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PipelineResult:

    pipeline_name: str

    model_name: str

    parameters: dict

    metrics: dict

    artifact: Any = None

    predictions: Any = None

    labels: Any = None

    figure: Any = None

    duration: float | None = None

    success: bool = True

    error: str | None = None