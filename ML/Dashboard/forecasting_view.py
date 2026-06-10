from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def actual_vs_forecast(
    actual,
    forecast
):

    fig = go.Figure()

    fig.add_scatter(
        y=actual,
        mode="lines",
        name="Actual"
    )

    fig.add_scatter(
        y=forecast,
        mode="lines",
        name="Forecast"
    )

    return fig


def forecast_error_distribution(
    actual,
    forecast
):

    errors = (
        actual
        - forecast
    )

    fig = px.histogram(
        errors,
        title="Forecast Errors"
    )

    return fig