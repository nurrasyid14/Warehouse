from __future__ import annotations

import pandas as pd

from .experiment import (
    ExperimentRecord
)


class ExperimentRegistry:

    def __init__(self):

        self.records = []

    def add(
        self,
        record: ExperimentRecord
    ):

        self.records.append(
            record
        )

    def clear(self):

        self.records.clear()

    def dataframe(self):

        rows = []

        for r in self.records:

            row = {

                "experiment":
                    r.experiment_name,

                "pipeline":
                    r.pipeline_name,

                "model":
                    r.model_name,

                "cube":
                    r.cube_name,

                "timestamp":
                    r.timestamp,

                "duration":
                    r.duration
            }

            row.update(
                r.metrics
            )

            rows.append(
                row
            )

        return pd.DataFrame(
            rows
        )

    def __len__(self):

        return len(
            self.records
        )