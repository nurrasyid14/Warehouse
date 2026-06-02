# ML/Clustering/models/hierarchical.py

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

import pickle
import pandas as pd


class BaseHierarchicalCluster(ABC):

    def __init__(self):

        self.model = None
        self.labels_ = None

    @abstractmethod
    def fit(self, X):
        pass

    def fit_predict(self, X):

        self.fit(X)

        return self.labels_

    @property
    def n_clusters(self):

        if self.labels_ is None:
            return None

        return len(set(self.labels_))

    def cluster_distribution(self):

        return (
            pd.Series(self.labels_)
            .value_counts()
            .sort_index()
        )

    def summary(self):

        return {
            "algorithm":
                self.__class__.__name__,

            "n_clusters":
                self.n_clusters,

            "cluster_distribution":
                self.cluster_distribution()
                .to_dict()
        }

    def save(
        self,
        path: str
    ):

        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(
        cls,
        path: str
    ):

        with open(path, "rb") as f:
            return pickle.load(f)


__all__ = [
    "BaseHierarchicalCluster"
]