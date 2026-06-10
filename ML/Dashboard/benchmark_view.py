from __future__ import annotations

import pandas as pd
import plotly.express as px


def benchmark_table(
    df: pd.DataFrame
):

    return df.sort_values(
        by=df.columns[-1],
        ascending=False
    )


def benchmark_barplot(
    df: pd.DataFrame,
    metric: str
):

    fig = px.bar(
        df,
        x="cube_name",
        y=metric,
        color="model_name",
        barmode="group",
        title=f"{metric} Comparison"
    )

    return fig


def leaderboard(
    df: pd.DataFrame,
    metric: str
):

    return (
        df
        .sort_values(
            metric,
            ascending=False
        )
        .reset_index(drop=True)
    )