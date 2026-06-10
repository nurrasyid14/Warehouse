from __future__ import annotations

import plotly.express as px
import pandas as pd


def silhouette_comparison(
    df: pd.DataFrame
):

    fig = px.bar(
        df,
        x="cube_name",
        y="silhouette",
        color="model_name",
        title="Silhouette Score"
    )

    return fig


def cluster_size_plot(
    labels
):

    counts = (
        pd.Series(labels)
        .value_counts()
        .reset_index()
    )

    counts.columns = [
        "cluster",
        "count"
    ]

    fig = px.pie(
        counts,
        names="cluster",
        values="count"
    )

    return fig