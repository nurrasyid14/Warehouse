# ML/Forecast/exponential_smoothing.py

from typing import Optional
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import SimpleExpSmoothing as StatsSimpleExpSmoothing
from statsmodels.tsa.holtwinters import Holt as StatsHolt
from statsmodels.tsa.holtwinters import ExponentialSmoothing as StatsExponentialSmoothing
import pickle

class BaseExponentialSmoothing:
    def __init__(self):
        self.model = None
        self.fitted_model = None

    def summary(self):
        if self.fitted_model is None:
            raise ValueError("Model has not been fitted.")
        return self.fitted_model.summary()

    def predict(self, start=None, end=None, **kwargs):
        if self.fitted_model is None:
            raise ValueError("Model has not been fitted.")
        return self.fitted_model.predict(start=start, end=end, **kwargs)

    def save(self, path: str):
        if self.fitted_model is None:
            raise ValueError("Model has not been fitted.")
        with open(path, "wb") as f:
            pickle.dump(self.fitted_model, f)

    def load(self, path: str):
        with open(path, "rb") as f:
            self.fitted_model = pickle.load(f)
        return self

    @property
    def aic(self):
        return None if self.fitted_model is None else self.fitted_model.aic

    @property
    def bic(self):
        return None if self.fitted_model is None else self.fitted_model.bic

    @property
    def sse(self):
        return None if self.fitted_model is None else self.fitted_model.sse


class SimpleExponentialSmoothing(BaseExponentialSmoothing):
    """
    Simple Exponential Smoothing (SES)
    Suitable for data with no trend or seasonality.
    """
    def __init__(self):
        super().__init__()

    def fit(self, y):
        y_series = pd.Series(y) if not isinstance(y, pd.Series) else y
        self.model = StatsSimpleExpSmoothing(y_series)
        self.fitted_model = self.model.fit()
        return self

    def forecast(self, steps: int):
        if self.fitted_model is None:
            raise ValueError("Model has not been fitted.")
        return self.fitted_model.forecast(steps=steps)


class Holt(BaseExponentialSmoothing):
    """
    Holt's Exponential Smoothing (Double Exponential Smoothing)
    Suitable for data with a trend but no seasonality.
    """
    def __init__(self, exponential: bool = False, damped_trend: bool = False):
        super().__init__()
        self.exponential = exponential
        self.damped_trend = damped_trend

    def fit(self, y):
        y_series = pd.Series(y) if not isinstance(y, pd.Series) else y
        self.model = StatsHolt(
            y_series,
            exponential=self.exponential,
            damped_trend=self.damped_trend
        )
        self.fitted_model = self.model.fit()
        return self

    def forecast(self, steps: int):
        if self.fitted_model is None:
            raise ValueError("Model has not been fitted.")
        return self.fitted_model.forecast(steps=steps)


class ExponentialSmoothing(BaseExponentialSmoothing):
    """
    Holt-Winters Exponential Smoothing (Triple Exponential Smoothing)
    Suitable for data with trend and/or seasonality.
    """
    def __init__(
        self,
        trend: Optional[str] = "add",
        damped_trend: bool = False,
        seasonal: Optional[str] = "add",
        seasonal_periods: Optional[int] = None
    ):
        super().__init__()
        self.trend = trend
        self.damped_trend = damped_trend
        self.seasonal = seasonal
        self.seasonal_periods = seasonal_periods

    def fit(self, y):
        y_series = pd.Series(y) if not isinstance(y, pd.Series) else y
        self.model = StatsExponentialSmoothing(
            y_series,
            trend=self.trend,
            damped_trend=self.damped_trend,
            seasonal=self.seasonal,
            seasonal_periods=self.seasonal_periods
        )
        self.fitted_model = self.model.fit()
        return self

    def forecast(self, steps: int):
        if self.fitted_model is None:
            raise ValueError("Model has not been fitted.")
        return self.fitted_model.forecast(steps=steps)


__all__ = [
    "SimpleExponentialSmoothing",
    "Holt",
    "ExponentialSmoothing"
]
