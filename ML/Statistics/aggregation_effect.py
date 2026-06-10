from __future__ import annotations

import pandas as pd


def aggregation_improvement(
    df: pd.DataFrame,
    metric: str,
    baseline: str,
    target: str
):

    base_score = (
        df.loc[
            df["cube_name"] == baseline,
            metric
        ]
        .mean()
    )

    target_score = (
        df.loc[
            df["cube_name"] == target,
            metric
        ]
        .mean()
    )

    return (
        (
            target_score
            - base_score
        )
        / abs(base_score)
    ) * 100