# ML/Forecast/var.py

from __future__ import annotations

from typing import Optional

import pickle
import pandas as pd

from statsmodels.tsa.vector_ar.var_model import (
    VAR as StatsVAR
)


class VAR:
    """
    Vector Autoregression VAR(p)

    Parameters
    ----------
    p : int
        Lag order.
    """

    def __init__(
        self,
        p: int = 1
    ):

        self.p = p

        self.columns = None

        self.model = None
        self.fitted_model = None

    # =====================================================
    # FITTING
    # =====================================================

    def fit(
        self,
        df: pd.DataFrame
    ) -> "VAR":

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "VAR requires a pandas DataFrame."
            )

        self.columns = list(df.columns)

        self.model = StatsVAR(df)

        self.fitted_model = self.model.fit(
            maxlags=self.p
        )

        return self

    # =====================================================
    # FORECASTING
    # =====================================================

    def forecast(
        self,
        steps: int
    ) -> pd.DataFrame:

        self._check_fitted()

        lag_order = self.fitted_model.k_ar

        values = self.fitted_model.forecast(
            y=self.fitted_model.endog[-lag_order:],
            steps=steps
        )

        return pd.DataFrame(
            values,
            columns=self.columns
        )

    # =====================================================
    # LAG SELECTION
    # =====================================================

    def select_order(
        self,
        df: pd.DataFrame,
        maxlags: int = 12
    ):

        model = StatsVAR(df)

        return model.select_order(
            maxlags=maxlags
        )

    # =====================================================
    # CAUSALITY
    # =====================================================

    def granger_causality(
        self,
        caused,
        causing
    ):

        self._check_fitted()

        return self.fitted_model.test_causality(
            caused=caused,
            causing=causing,
            kind="f"
        )

    # =====================================================
    # IMPULSE RESPONSE
    # =====================================================

    def impulse_response(
        self,
        periods: int = 12
    ):

        self._check_fitted()

        return self.fitted_model.irf(
            periods
        )

    # =====================================================
    # FEVD
    # =====================================================

    def fevd(
        self,
        periods: int = 12
    ):

        self._check_fitted()

        return self.fitted_model.fevd(
            periods
        )

    # =====================================================
    # MODEL INFO
    # =====================================================

    def summary(self):

        self._check_fitted()

        return self.fitted_model.summary()

    @property
    def aic(self):

        if self.fitted_model is None:
            return None

        return self.fitted_model.aic

    @property
    def bic(self):

        if self.fitted_model is None:
            return None

        return self.fitted_model.bic

    @property
    def hqic(self):

        if self.fitted_model is None:
            return None

        return self.fitted_model.hqic

    @property
    def fpe(self):

        if self.fitted_model is None:
            return None

        return self.fitted_model.fpe

    @property
    def lag_order(self):

        if self.fitted_model is None:
            return None

        return self.fitted_model.k_ar

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def save(
        self,
        path: str
    ):

        self._check_fitted()

        with open(path, "wb") as f:
            pickle.dump(
                self.fitted_model,
                f
            )

    def load(
        self,
        path: str
    ) -> "VAR":

        with open(path, "rb") as f:
            self.fitted_model = pickle.load(f)

        return self

    # =====================================================
    # INTERNAL
    # =====================================================

    def _check_fitted(self):

        if self.fitted_model is None:
            raise ValueError(
                "Model has not been fitted."
            )


__all__ = ["VAR"]