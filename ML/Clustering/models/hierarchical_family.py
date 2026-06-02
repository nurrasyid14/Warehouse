from __future__ import annotations

import numpy as np

from sklearn.cluster import (
    AgglomerativeClustering,
    BisectingKMeans
)

from .hierarchical import BaseHierarchicalCluster


# =====================================================
# AGGLOMERATIVE CLUSTERING
# =====================================================

class AgglomerativeCluster(
    BaseHierarchicalCluster
):
    """
    Bottom-up hierarchical clustering.

    Linkages
    --------
    - ward
    - complete
    - average
    - single
    """

    def __init__(
        self,
        n_clusters: int = 3,
        linkage: str = "ward",
        metric: str = "euclidean"
    ):

        super().__init__()

        if n_clusters < 2:
            raise ValueError(
                "n_clusters must be >= 2."
            )

        self.n_clusters_target = n_clusters

        self.linkage = linkage
        self.metric = metric

        self.n_features_ = None

    def fit(
        self,
        X
    ):

        X = np.asarray(X)

        self.n_features_ = X.shape[1]

        kwargs = {
            "n_clusters":
                self.n_clusters_target,

            "linkage":
                self.linkage,

            "compute_distances":
                True
        }

        if self.linkage != "ward":
            kwargs["metric"] = self.metric

        self.model = AgglomerativeClustering(
            **kwargs
        )

        self.labels_ = self.model.fit_predict(
            X
        )

        return self

    @property
    def merge_distances(self):
        """
        Distance at each merge step.
        Useful for dendrogram analysis.
        """

        if self.model is None:
            return None

        return self.model.distances_

    @property
    def children(self):
        """
        Hierarchical merge structure.
        """

        if self.model is None:
            return None

        return self.model.children_


# =====================================================
# BISECTING K-MEANS
# =====================================================

class BisectingKMeansCluster(
    BaseHierarchicalCluster
):
    """
    Divisive hierarchical clustering
    based on recursive K-Means splitting.
    """

    def __init__(
        self,
        n_clusters: int = 3,
        random_state: int = 42,
        init: str = "k-means++"
    ):

        super().__init__()

        if n_clusters < 2:
            raise ValueError(
                "n_clusters must be >= 2."
            )

        self.n_clusters_target = n_clusters

        self.random_state = random_state
        self.init = init

        self.n_features_ = None

    def fit(
        self,
        X
    ):

        X = np.asarray(X)

        self.n_features_ = X.shape[1]

        self.model = BisectingKMeans(
            n_clusters=self.n_clusters_target,
            init=self.init,
            random_state=self.random_state
        )

        self.labels_ = self.model.fit_predict(
            X
        )

        return self

    @property
    def centroids(self):
        """
        Cluster centers.
        """

        if self.model is None:
            return None

        return self.model.cluster_centers_

    @property
    def inertia(self):
        """
        Sum of squared distances.
        """

        if self.model is None:
            return None

        return self.model.inertia_


# =====================================================
# EXPORTS
# =====================================================

__all__ = [
    "AgglomerativeCluster",
    "BisectingKMeansCluster"
]