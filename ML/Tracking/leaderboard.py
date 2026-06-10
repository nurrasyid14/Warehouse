from __future__ import annotations


class Leaderboard:

    def __init__(
        self,
        registry
    ):

        self.registry = registry

    def rank(
        self,
        metric,
        ascending=False
    ):

        df = (
            self.registry
            .dataframe()
        )

        if metric not in df:

            raise ValueError(
                f"{metric} not found."
            )

        return (

            df

            .sort_values(
                metric,
                ascending=ascending
            )

            .reset_index(
                drop=True
            )

        )