# ML/Forecast/arima.py

from typing import Optional
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA as StatsARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.statespace.sarimax import SARIMAX as StatsSARIMAX
import pickle
class BaseARIMA:

    def __init__(self):

        self.model = None
        self.fitted_model = None

    def summary(self):

        if self.fitted_model is None:
            raise ValueError(
                "Model has not been fitted."
            )

        return self.fitted_model.summary()

    def predict(
        self,
        start=None,
        end=None,
        **kwargs
    ):

        if self.fitted_model is None:
            raise ValueError(
                "Model has not been fitted."
            )

        return self.fitted_model.predict(
            start=start,
            end=end,
            **kwargs
        )

    def save(self, path):

        with open(path, "wb") as f:
            pickle.dump(
                self.fitted_model,
                f
            )

    def load(self, path):

        with open(path, "rb") as f:
            self.fitted_model = pickle.load(f)

        return self

    @property
    def aic(self):

        return (
            None
            if self.fitted_model is None
            else self.fitted_model.aic
        )

    @property
    def bic(self):

        return (
            None
            if self.fitted_model is None
            else self.fitted_model.bic
        )

    @property
    def hqic(self):

        return (
            None
            if self.fitted_model is None
            else self.fitted_model.hqic
        )

class ARIMA(BaseARIMA):

    def __init__(
        self,
        p=1,
        d=1,
        q=1
    ):

        super().__init__()

        self.p = p
        self.d = d
        self.q = q

    @property
    def order(self):

        return (
            self.p,
            self.d,
            self.q
        )

    def fit(self, y):

        self.model = StatsARIMA(
            y,
            order=self.order
        )

        self.fitted_model = self.model.fit()

        return self

    def forecast(self, steps):

        return self.fitted_model.forecast(
            steps=steps
        )
    
class SARIMA(ARIMA):

    def __init__(
        self,
        p=1,
        d=1,
        q=1,
        P=1,
        D=1,
        Q=1,
        s=12
    ):

        super().__init__(
            p,
            d,
            q
        )

        self.P = P
        self.D = D
        self.Q = Q
        self.s = s

    @property
    def seasonal_order(self):

        return (
            self.P,
            self.D,
            self.Q,
            self.s
        )

    def fit(self, y):

        self.model = StatsSARIMAX(
            y,
            order=self.order,
            seasonal_order=self.seasonal_order
        )

        self.fitted_model = self.model.fit(
            disp=False
        )

        return self
    
class ARIMAX(ARIMA):

    def fit(
        self,
        y,
        exog
    ):

        self.model = StatsSARIMAX(
            y,
            exog=exog,
            order=self.order
        )

        self.fitted_model = self.model.fit(
            disp=False
        )

        return self

    def forecast(
        self,
        steps,
        exog_future
    ):

        return self.fitted_model.forecast(
            steps=steps,
            exog=exog_future
        )
    
class SARIMAX(SARIMA):

    def fit(
        self,
        y,
        exog
    ):

        self.model = StatsSARIMAX(
            y,
            exog=exog,
            order=self.order,
            seasonal_order=self.seasonal_order
        )

        self.fitted_model = self.model.fit(
            disp=False
        )

        return self

    def forecast(
        self,
        steps,
        exog_future
    ):

        return self.fitted_model.forecast(
            steps=steps,
            exog=exog_future
        )
    
__all__ = [
    "ARIMA",
    "SARIMA",
    "ARIMAX",
    "SARIMAX"
]