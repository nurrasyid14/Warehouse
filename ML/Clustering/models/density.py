# ML/Clustering/models/density.py

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from typing import Optional

import pickle
import pandas as pd


class BaseDensityCluster(ABC):
    """
    Base class for density-based clustering algorithms.

    Supported descendants
    ---------------------
    - DBSCAN
    - HDBSCAN
    - OPTICS
    - MeanShift
    """

    def __init__(self):

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

        self.fit(X)

        return self.labels_

    def predict(
        self,
        X
    ):

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
    def n_clusters(self) -> Optional[int]:
        """
        Number of discovered clusters.

        Noise cluster (-1) excluded.
        """

        if self.labels_ is None:
            return None

        labels = set(self.labels_)

        if -1 in labels:
            labels.remove(-1)

        return len(labels)

    @property
    def n_noise(self) -> Optional[int]:
        """
        Number of noise observations.
        """

        if self.labels_ is None:
            return None

        return int(
            (self.labels_ == -1).sum()
        )

    @property
    def noise_ratio(self) -> Optional[float]:

        if self.labels_ is None:
            return None

        return self.n_noise / len(
            self.labels_
        )

    # =====================================================
    # ANALYSIS
    # =====================================================

    def cluster_distribution(
        self
    ) -> pd.Series:

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

        self._check_labels()

        return {
            "algorithm":
                self.__class__.__name__,

            "n_clusters":
                self.n_clusters,

            "n_noise":
                self.n_noise,

            "noise_ratio":
                round(
                    self.noise_ratio,
                    4
                ),

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
    "BaseDensityCluster"
]