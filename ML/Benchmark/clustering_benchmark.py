from __future__ import annotations

import time
import pandas as pd

from .result import BenchmarkResult


class ClusteringBenchmark:

    def __init__(
        self,
        cube,
        model,
        evaluator
    ):

        self.cube = cube
        self.model = model
        self.evaluator = evaluator

        self.result = None

    def run(self):

        start = time.perf_counter()

        labels = self.model.fit_predict(
            self.cube.data
        )

        metrics = self.evaluator(
            self.cube.data,
            labels
        )

        elapsed = (
            time.perf_counter()
            - start
        )

        self.result = BenchmarkResult(
            experiment_name="clustering",
            cube_name=self.cube.name,
            model_name=self.model.__class__.__name__,
            metrics=metrics,
            elapsed_seconds=elapsed,
        )

        return self.result

    def to_dataframe(self):

        if self.result is None:
            return pd.DataFrame()

        return self.result.to_dataframe()