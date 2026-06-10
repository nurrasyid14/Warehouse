from __future__ import annotations

import pandas as pd


def rank_by_metric(
    df: pd.DataFrame,
    metric: str,
    ascending: bool = False
):

    return (
        df.sort_values(
            metric,
            ascending=ascending
        )
        .reset_index(drop=True)
    )


def top_cube(
    df: pd.DataFrame,
    metric: str
):

    ranked = rank_by_metric(
        df,
        metric
    )

    return ranked.iloc[0]


def top_algorithm(
    df: pd.DataFrame,
    metric: str
):

    ranked = rank_by_metric(
        df,
        metric
    )

    return ranked.iloc[0]