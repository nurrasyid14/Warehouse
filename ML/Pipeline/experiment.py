from __future__ import annotations

from datetime import datetime


class PipelineExperiment:

    def __init__(
        self,
        name: str,
        cube_name: str
    ):

        self.name = name

        self.cube_name = cube_name

        self.created_at = (
            datetime.now()
        )

        self.results = []

    def add_result(
        self,
        result
    ):

        self.results.append(
            result
        )

    def best_result(
        self,
        metric: str
    ):

        if not self.results:
            return None

        valid = [

            r for r in self.results

            if metric in r.metrics

        ]

        if not valid:
            return None

        return max(
            valid,
            key=lambda r:
            r.metrics[metric]
        )

    def __len__(self):

        return len(
            self.results
        )


Experiment = PipelineExperiment