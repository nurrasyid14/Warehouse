from __future__ import annotations

import pandas as pd

from .cube import Cube


class ForecastFeeder:

    def __init__(
        self,
        cube: Cube
    ):

        self.cube = cube

    def univariate(
        self,
        target: str,
        time_col: str = "full_date"
    ) -> pd.DataFrame:

        df = (
            self.cube.data[
                [time_col, target]
            ]
            .sort_values(time_col)
            .copy()
        )

        return df

    def multivariate(
        self,
        targets,
        time_col: str = "full_date"
    ) -> pd.DataFrame:

        cols = [time_col]

        cols.extend(targets)

        df = (
            self.cube.data[cols]
            .sort_values(time_col)
            .copy()
        )

        return df

    def arima(
        self,
        target: str,
        time_col: str = "full_date"
    ):

        df = self.univariate(
            target,
            time_col
        )

        return (
            df
            .set_index(time_col)[target]
        )

    def var(
        self,
        targets,
        time_col: str = "full_date"
    ):

        df = self.multivariate(
            targets,
            time_col
        )

        return (
            df
            .set_index(time_col)
        )