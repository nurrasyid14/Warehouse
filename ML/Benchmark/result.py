from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd


@dataclass
class BenchmarkResult:

    experiment_name: str

    cube_name: str

    model_name: str

    metrics: dict

    elapsed_seconds: float

    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )

    def to_dict(self) -> dict:

        row = {
            "experiment_name": self.experiment_name,
            "cube_name": self.cube_name,
            "model_name": self.model_name,
            "elapsed_seconds": self.elapsed_seconds,
            "timestamp": self.timestamp,
        }

        row.update(self.metrics)

        return row

    def to_dataframe(self) -> pd.DataFrame:

        return pd.DataFrame(
            [self.to_dict()]
        )