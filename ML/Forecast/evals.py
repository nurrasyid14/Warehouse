# ML/Forecast/evals.py

from __future__ import annotations

import numpy as np

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


def mae(
    y_true,
    y_pred
) -> float:
    """
    Mean Absolute Error
    """

    return float(
        mean_absolute_error(
            y_true,
            y_pred
        )
    )


def mse(
    y_true,
    y_pred
) -> float:
    """
    Mean Squared Error
    """

    return float(
        mean_squared_error(
            y_true,
            y_pred
        )
    )


def rmse(
    y_true,
    y_pred
) -> float:
    """
    Root Mean Squared Error
    """

    return float(
        np.sqrt(
            mean_squared_error(
                y_true,
                y_pred
            )
        )
    )


def mape(
    y_true,
    y_pred
) -> float:
    """
    Mean Absolute Percentage Error
    """

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    mask = y_true != 0

    return float(
        np.mean(
            np.abs(
                (
                    y_true[mask]
                    - y_pred[mask]
                )
                / y_true[mask]
            )
        )
        * 100
    )


def smape(
    y_true,
    y_pred
) -> float:
    """
    Symmetric MAPE
    """

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    denominator = (
        np.abs(y_true)
        + np.abs(y_pred)
    )

    mask = denominator != 0

    return float(
        np.mean(
            (
                2
                * np.abs(
                    y_pred[mask]
                    - y_true[mask]
                )
            )
            / denominator[mask]
        )
        * 100
    )


def r2(
    y_true,
    y_pred
) -> float:
    """
    R² Score
    """

    return float(
        r2_score(
            y_true,
            y_pred
        )
    )


def evaluate_forecast(
    y_true,
    y_pred
) -> dict:
    """
    Full forecasting evaluation.
    """

    return {
        "MAE": mae(
            y_true,
            y_pred
        ),
        "MSE": mse(
            y_true,
            y_pred
        ),
        "RMSE": rmse(
            y_true,
            y_pred
        ),
        "MAPE": mape(
            y_true,
            y_pred
        ),
        "SMAPE": smape(
            y_true,
            y_pred
        ),
        "R2": r2(
            y_true,
            y_pred
        )
    }


__all__ = [
    "mae",
    "mse",
    "rmse",
    "mape",
    "smape",
    "r2",
    "evaluate_forecast"
]