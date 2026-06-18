from __future__ import annotations

import pandas as pd
from .result import BenchmarkResult

class AggregationBenchmark:
    """
    Aggregation level benchmark container.
    Collects multiple BenchmarkResult objects and evaluates them.
    """

    def __init__(self):
        self.results: list[BenchmarkResult] = []

    def add_result(self, result: BenchmarkResult) -> None:
        """Add a benchmark result to the collection."""
        self.results.append(result)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert all stored benchmark results to a single combined DataFrame."""
        if not self.results:
            return pd.DataFrame()
        
        dfs = [res.to_dataframe() for res in self.results]
        return pd.concat(dfs, ignore_index=True)