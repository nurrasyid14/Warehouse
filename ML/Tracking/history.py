from __future__ import annotations

import pandas as pd


class ExperimentHistory:

    def __init__(
        self,
        registry
    ):

        self.registry = registry

    def dataframe(self):

        return (

            self.registry
            .dataframe()

            .sort_values(
                "timestamp"
            )

        )

    def latest(
        self,
        n=10
    ):

        df = self.dataframe()

        return df.tail(
            n
        )