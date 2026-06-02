# ML/Forecast/__init__.py

from __future__ import annotations

import pandas as pd

from statsmodels.tsa.stattools import adfuller

from .arima import (
    ARIMA,
    SARIMA,
    ARIMAX,
    SARIMAX
)

from .var import VAR

from .evals import (
    mae,
    mse,
    rmse,
    mape,
    smape,
    r2,
    evaluate_forecast
)


# =====================================================
# STATIONARITY
# =====================================================

def is_stationary(
    series: pd.Series,
    alpha: float = 0.05
) -> bool:
    """
    Augmented Dickey-Fuller Test.

    Returns
    -------
    bool
        True if stationary.
    """

    result = adfuller(
        series.dropna()
    )

    p_value = result[1]

    return p_value < alpha


# =====================================================
# DIFFERENCING
# =====================================================

def difference(
    series: pd.Series,
    order: int = 1
) -> pd.Series:
    """
    Apply differencing.
    """

    result = series.copy()

    for _ in range(order):
        result = result.diff()

    return result.dropna()


def inverse_difference(
    original_series: pd.Series,
    forecast_values
):
    """
    Reverse first-order differencing.

    Notes
    -----
    Works for d=1.
    """

    last_value = original_series.iloc[-1]

    restored = []

    current = last_value

    for value in forecast_values:

        current += value

        restored.append(current)

    return restored


# =====================================================
# AUTO FORECAST PIPELINE
# =====================================================

def define_pipeline(
    data,
    steps: int = 6,
    auto_difference: bool = True
):

    if isinstance(data, pd.Series):

        working_data = data.copy()

        if auto_difference:

            if not is_stationary(
                working_data
            ):
                working_data = difference(
                    working_data
                )

        model = ARIMA(
            p=1,
            d=0,
            q=1
        )

        model.fit(
            working_data
        )

        forecast = model.forecast(
            steps=steps
        )

        return {
            "model_type": "ARIMA",
            "model": model,
            "forecast": forecast
        }

    elif isinstance(data, pd.DataFrame):

        working_data = data.copy()

        if auto_difference:

            for col in working_data.columns:

                if not is_stationary(
                    working_data[col]
                ):
                    working_data[col] = difference(
                        working_data[col]
                    )

            working_data = working_data.dropna()

        selector = VAR()

        lag_info = selector.select_order(
            working_data,
            maxlags=12
        )

        optimal_lag = lag_info.aic

        model = VAR(
            p=optimal_lag
        )

        model.fit(
            working_data
        )

        forecast = model.forecast(
            steps=steps
        )

        return {
            "model_type": "VAR",
            "model": model,
            "forecast": forecast,
            "lag": optimal_lag
        }

    raise TypeError(
        "Input must be pandas Series or DataFrame."
    )


__all__ = [
    # Models
    "ARIMA",
    "SARIMA",
    "ARIMAX",
    "SARIMAX",
    "VAR",

    # Utilities
    "is_stationary",
    "difference",
    "inverse_difference",
    "define_pipeline",
    "evaluate_forecast",
    # Evaluation Metrics
    "mae",
    "mse",
    "rmse",
    "mape",
    "smape",
    "r2",
]