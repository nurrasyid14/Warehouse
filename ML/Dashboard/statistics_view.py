from __future__ import annotations

import plotly.express as px
import pandas as pd


def aggregation_effect_plot(
    df: pd.DataFrame,
    metric: str
):

    fig = px.line(
        df,
        x="cube_name",
        y=metric,
        color="model_name",
        markers=True,
        title=f"Aggregation Effect on {metric}"
    )

    return fig


def correlation_heatmap(
    corr_matrix
):

    fig = px.imshow(
        corr_matrix,
        text_auto=True
    )

    return fig