from __future__ import annotations

from itertools import product

import numpy as np
import pandas as pd

from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
    mean_absolute_error,
    mean_squared_error
)


# =====================================================
# SCORERS
# =====================================================

def silhouette_scorer(
    model,
    X
) -> float:

    labels = model.labels_

    unique = np.unique(labels)

    if len(unique) < 2:
        return -1.0

    return silhouette_score(
        X,
        labels
    )


def calinski_harabasz_scorer(
    model,
    X
) -> float:

    labels = model.labels_

    unique = np.unique(labels)

    if len(unique) < 2:
        return -1.0

    return calinski_harabasz_score(
        X,
        labels
    )


def davies_bouldin_scorer(
    model,
    X
) -> float:

    labels = model.labels_

    unique = np.unique(labels)

    if len(unique) < 2:
        return -np.inf

    score = davies_bouldin_score(
        X,
        labels
    )

    return -score


# =====================================================
# FORECASTING METRICS
# =====================================================

def mae(
    y_true,
    y_pred
):

    return mean_absolute_error(
        y_true,
        y_pred
    )


def rmse(
    y_true,
    y_pred
):

    return np.sqrt(
        mean_squared_error(
            y_true,
            y_pred
        )
    )


def mape(
    y_true,
    y_pred
):

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    mask = y_true != 0

    return (
        np.mean(
            np.abs(
                (y_true[mask] - y_pred[mask])
                / y_true[mask]
            )
        )
        * 100
    )


# =====================================================
# BASE GRID SEARCH
# =====================================================

class BaseGridSearch:

    def __init__(
        self,
        model_class,
        param_grid: dict
    ):

        self.model_class = model_class

        self.param_grid = param_grid

        self.best_model_ = None

        self.best_params_ = None

        self.best_score_ = None

        self.results_ = []

    def _generate_params(self):

        keys = list(
            self.param_grid.keys()
        )

        values = list(
            self.param_grid.values()
        )

        for combination in product(*values):

            yield dict(
                zip(
                    keys,
                    combination
                )
            )

    @property
    def results_df(self):

        return pd.DataFrame(
            self.results_
        )


# =====================================================
# CLUSTERING GRID SEARCH
# =====================================================

class ClusteringGridSearch(
    BaseGridSearch
):

    def __init__(
        self,
        model_class,
        param_grid: dict,
        scorer=silhouette_scorer
    ):

        super().__init__(
            model_class,
            param_grid
        )

        self.scorer = scorer

    def fit(
        self,
        X
    ):

        best_score = -np.inf

        for params in self._generate_params():

            try:

                model = self.model_class(
                    **params
                )

                model.fit(X)

                score = self.scorer(
                    model,
                    X
                )

                self.results_.append(
                    {
                        "params": params,
                        "score": score
                    }
                )

                if score > best_score:

                    best_score = score

                    self.best_model_ = model

                    self.best_params_ = params

                    self.best_score_ = score

            except Exception as e:

                self.results_.append(
                    {
                        "params": params,
                        "score": np.nan,
                        "error": str(e)
                    }
                )

        return self


# =====================================================
# FORECAST GRID SEARCH
# =====================================================

class ForecastGridSearch(
    BaseGridSearch
):

    def __init__(
        self,
        model_class,
        param_grid: dict,
        metric=rmse
    ):

        super().__init__(
            model_class,
            param_grid
        )

        self.metric = metric

    def fit(
        self,
        train,
        test
    ):

        best_score = np.inf

        for params in self._generate_params():

            try:

                model = self.model_class(
                    **params
                )

                model.fit(
                    train
                )

                predictions = model.forecast(
                    len(test)
                )

                score = self.metric(
                    test,
                    predictions
                )

                self.results_.append(
                    {
                        "params": params,
                        "score": score
                    }
                )

                if score < best_score:

                    best_score = score

                    self.best_model_ = model

                    self.best_params_ = params

                    self.best_score_ = score

            except Exception as e:

                self.results_.append(
                    {
                        "params": params,
                        "score": np.nan,
                        "error": str(e)
                    }
                )

        return self


# =====================================================
# OLAP AGGREGATION EXPERIMENT
# =====================================================

class OLAPAggregationSearch:

    def __init__(
        self,
        model_class,
        param_grid,
        scorer=silhouette_scorer
    ):

        self.model_class = model_class

        self.param_grid = param_grid

        self.scorer = scorer

        self.results_ = []

    def fit(
        self,
        datasets: dict
    ):
        """
        Example
        -------
        {
            "daily": X_daily,
            "weekly": X_weekly,
            "monthly": X_monthly
        }
        """

        for level, X in datasets.items():

            search = ClusteringGridSearch(
                self.model_class,
                self.param_grid,
                self.scorer
            )

            search.fit(X)

            self.results_.append(
                {
                    "aggregation": level,
                    "best_score": search.best_score_,
                    "best_params": search.best_params_
                }
            )

        return self

    @property
    def results_df(self):

        return pd.DataFrame(
            self.results_
        )


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    # Clustering Metrics
    "silhouette_scorer",
    "calinski_harabasz_scorer",
    "davies_bouldin_scorer",

    # Forecast Metrics
    "mae",
    "rmse",
    "mape",

    # Search Classes
    "ClusteringGridSearch",
    "ForecastGridSearch",
    "OLAPAggregationSearch"
]