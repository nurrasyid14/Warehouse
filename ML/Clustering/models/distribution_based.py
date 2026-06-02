from __future__ import annotations

import pickle

import numpy as np
import pandas as pd

from sklearn.mixture import (
    GaussianMixture,
    BayesianGaussianMixture
)


# =====================================================
# BASE DISTRIBUTION CLUSTER
# =====================================================

class BaseDistributionCluster:

    def __init__(self):

        self.model = None

        self.labels_ = None

        self.n_features_ = None

    # =====================================================
    # FITTING
    # =====================================================

    def fit_predict(
        self,
        X
    ):

        self.fit(X)

        return self.labels_

    def predict(
        self,
        X
    ):

        self._check_fitted()

        return self.model.predict(X)

    def predict_proba(
        self,
        X
    ):

        self._check_fitted()

        return self.model.predict_proba(X)

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def n_clusters(self):

        if self.labels_ is None:
            return None

        return len(
            np.unique(
                self.labels_
            )
        )

    @property
    def weights(self):

        self._check_fitted()

        return self.model.weights_

    @property
    def means(self):

        self._check_fitted()

        return self.model.means_

    @property
    def covariances(self):

        self._check_fitted()

        return self.model.covariances_

    @property
    def converged(self):

        if self.model is None:
            return None

        return self.model.converged_

    @property
    def n_iter(self):

        if self.model is None:
            return None

        return self.model.n_iter_

    # =====================================================
    # ANALYSIS
    # =====================================================

    def cluster_distribution(
        self
    ):

        if self.labels_ is None:
            raise ValueError(
                "Model has not been fitted."
            )

        return (
            pd.Series(
                self.labels_,
                name="cluster"
            )
            .value_counts()
            .sort_index()
        )

    def summary(
        self
    ):

        return {
            "algorithm":
                self.__class__.__name__,

            "n_clusters":
                self.n_clusters,

            "n_features":
                self.n_features_,

            "converged":
                self.converged,

            "n_iter":
                self.n_iter,

            "cluster_distribution":
                self.cluster_distribution()
                .to_dict()
        }

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def save(
        self,
        path: str
    ):

        self._check_fitted()

        with open(
            path,
            "wb"
        ) as f:

            pickle.dump(
                self,
                f
            )

    @classmethod
    def load(
        cls,
        path: str
    ):

        with open(
            path,
            "rb"
        ) as f:

            return pickle.load(f)

    # =====================================================
    # INTERNAL
    # =====================================================

    def _check_fitted(
        self
    ):

        if self.model is None:
            raise ValueError(
                "Model has not been fitted."
            )


# =====================================================
# GAUSSIAN MIXTURE MODEL
# =====================================================

class GaussianMixtureCluster(
    BaseDistributionCluster
):
    """
    Classical Gaussian Mixture Model.
    """

    def __init__(
        self,
        n_clusters: int = 3,
        covariance_type: str = "full",
        random_state: int = 42
    ):

        super().__init__()

        if n_clusters < 1:
            raise ValueError(
                "n_clusters must be >= 1."
            )

        self.n_clusters_target = n_clusters

        self.covariance_type = covariance_type

        self.random_state = random_state

        self._aic = None
        self._bic = None

    def fit(
        self,
        X
    ):

        X = np.asarray(X)

        self.n_features_ = X.shape[1]

        self.model = GaussianMixture(
            n_components=self.n_clusters_target,
            covariance_type=self.covariance_type,
            random_state=self.random_state
        )

        self.model.fit(X)

        self.labels_ = self.model.predict(X)

        self._aic = self.model.aic(X)

        self._bic = self.model.bic(X)

        return self

    @property
    def aic(self):

        return self._aic

    @property
    def bic(self):

        return self._bic

    def summary(
        self
    ):

        result = super().summary()

        result.update(
            {
                "aic": self.aic,
                "bic": self.bic
            }
        )

        return result


# =====================================================
# BAYESIAN GMM
# =====================================================

class BayesianGaussianMixtureCluster(
    BaseDistributionCluster
):
    """
    Bayesian Gaussian Mixture Model.

    Automatically prunes
    unnecessary clusters.
    """

    def __init__(
        self,
        n_clusters: int = 10,
        covariance_type: str = "full",
        random_state: int = 42,
        weight_threshold: float = 0.01
    ):

        super().__init__()

        self.n_clusters_target = n_clusters

        self.covariance_type = covariance_type

        self.random_state = random_state

        self.weight_threshold = weight_threshold

    def fit(
        self,
        X
    ):

        X = np.asarray(X)

        self.n_features_ = X.shape[1]

        self.model = BayesianGaussianMixture(
            n_components=self.n_clusters_target,
            covariance_type=self.covariance_type,
            random_state=self.random_state
        )

        self.model.fit(X)

        self.labels_ = self.model.predict(X)

        return self

    @property
    def effective_clusters(self):

        if self.model is None:
            return None

        return int(
            np.sum(
                self.model.weights_
                > self.weight_threshold
            )
        )

    def summary(
        self
    ):

        result = super().summary()

        result.update(
            {
                "effective_clusters":
                    self.effective_clusters
            }
        )

        return result


# =====================================================
# EXPORTS
# =====================================================

__all__ = [
    "BaseDistributionCluster",
    "GaussianMixtureCluster",
    "BayesianGaussianMixtureCluster"
]