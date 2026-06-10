from __future__ import annotations

import pandas as pd


class TrackingPersistence:

    @staticmethod
    def save_csv(
        registry,
        path
    ):

        registry.dataframe().to_csv(
            path,
            index=False
        )

    @staticmethod
    def load_csv(
        path
    ):

        return pd.read_csv(
            path
        )