# ML/Clustering/models/centroids.py

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
import pickle
import pandas as pd


class BaseCentroidCluster(ABC):
    """
    Base class for centroid-based clustering algorithms.

    Supported descendants:
    ----------------------
    - KMeans
    - KMeans++
    - KMedoids
    - KModes
    - Fuzzy C-Means
    """

    def __init__(
        self,
        n_clusters: int = 3,
        random_state: int = 42
    ):

        self.n_clusters = n_clusters
        self.random_state = random_state

        self.model = None

        self.labels_ = None

    # =====================================================
    # ABSTRACT METHODS
    # =====================================================

    @abstractmethod
    def fit(
        self,
        X
    ):
        """
        Train clustering model.
        """
        pass

    # =====================================================
    # COMMON METHODS
    # =====================================================

    def fit_predict(
        self,
        X
    ):
        """
        Fit model and return labels.
        """

        self.fit(X)

        return self.labels_

    def predict(
        self,
        X
    ):
        """
        Predict cluster membership.
        """

        self._check_fitted()

        if not hasattr(
            self.model,
            "predict"
        ):
            raise NotImplementedError(
                f"{self.__class__.__name__} "
                "does not support predict()."
            )

        return self.model.predict(X)

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def centroids(self):
        """
        Return cluster centers if available.
        """

        if self.model is None:
            return None

        return getattr(
            self.model,
            "cluster_centers_",
            None
        )

    @property
    def inertia(self):
        """
        Return inertia if supported.
        """

        if self.model is None:
            return None

        return getattr(
            self.model,
            "inertia_",
            None
        )

    @property
    def n_samples(self) -> Optional[int]:

        if self.labels_ is None:
            return None

        return len(self.labels_)

    # =====================================================
    # ANALYSIS
    # =====================================================

    def cluster_distribution(
        self
    ) -> pd.Series:
        """
        Number of observations per cluster.
        """

        self._check_labels()

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
    ) -> dict:
        """
        Basic model summary.
        """

        self._check_labels()

        return {
            "algorithm":
                self.__class__.__name__,

            "n_clusters":
                self.n_clusters,

            "n_samples":
                self.n_samples,

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
        """
        Save fitted model.
        """

        self._check_fitted()

        with open(path, "wb") as f:

            pickle.dump(
                self,
                f
            )

    @classmethod
    def load(
        cls,
        path: str
    ):
        """
        Load saved clustering object.
        """

        with open(path, "rb") as f:

            obj = pickle.load(f)

        return obj

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

    def _check_labels(
        self
    ):

        if self.labels_ is None:
            raise ValueError(
                "Cluster labels are unavailable. "
                "Fit the model first."
            )


__all__ = [
    "BaseCentroidCluster"
]