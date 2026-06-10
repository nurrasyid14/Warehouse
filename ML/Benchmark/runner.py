from __future__ import annotations

from .aggregation_benchmark import (
    AggregationBenchmark
)


class BenchmarkRunner:

    def __init__(self):

        self.benchmark = (
            AggregationBenchmark()
        )

    def run_suite(
        self,
        benchmark_objects
    ):

        for obj in benchmark_objects:

            result = obj.run()

            self.benchmark.add_result(
                result
            )

        return self.benchmark

    def dataframe(self):

        return self.benchmark.to_dataframe()