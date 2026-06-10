from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExperimentRecord:

    experiment_name: str

    pipeline_name: str

    model_name: str

    cube_name: str

    timestamp: datetime

    parameters: dict

    metrics: dict

    duration: float | None = None

    notes: str = ""