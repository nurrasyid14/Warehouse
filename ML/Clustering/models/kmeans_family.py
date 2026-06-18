# ML/Clustering/models/kmeans_family.py

from __future__ import annotations
import numpy as np
from sklearn.cluster import KMeans as SKKMeans
import skfuzzy as fuzz
import kmedoids
from kmodes.kmodes import KModes
from .centroids import BaseCentroidCluster


# =====================================================
# K-MEANS
# =====================================================

class KMeansCluster(BaseCentroidCluster):

    def __init__(
        self,
        n_clusters: int = 3,
        random_state: int = 42,
        max_iter: int = 300,
        n_init: int = 10
    ):

        super().__init__(
            n_clusters=n_clusters,
            random_state=random_state
        )

        self.max_iter = max_iter
        self.n_init = n_init

    def fit(
        self,
        X
    ):

        self.model = SKKMeans(
            n_clusters=self.n_clusters,
            init="random",
            max_iter=self.max_iter,
            n_init=self.n_init,
            random_state=self.random_state
        )

        self.labels_ = self.model.fit_predict(X)

        return self


# =====================================================
# K-MEANS++
# =====================================================

class KMeansPlusPlus(BaseCentroidCluster):

    def __init__(
        self,
        n_clusters: int = 3,
        random_state: int = 42,
        max_iter: int = 300,
        n_init: int = 10
    ):

        super().__init__(
            n_clusters=n_clusters,
            random_state=random_state
        )

        self.max_iter = max_iter
        self.n_init = n_init

    def fit(
        self,
        X
    ):

        self.model = SKKMeans(
            n_clusters=self.n_clusters,
            init="k-means++",
            max_iter=self.max_iter,
            n_init=self.n_init,
            random_state=self.random_state
        )

        self.labels_ = self.model.fit_predict(X)

        return self


# =====================================================
# FUZZY C-MEANS
# =====================================================

class FuzzyCMeansCluster(BaseCentroidCluster):

    def __init__(
        self,
        n_clusters: int = 3,
        m: float = 2.0,
        error: float = 0.005,
        max_iter: int = 1000,
        random_state: int = 42
    ):

        super().__init__(
            n_clusters=n_clusters,
            random_state=random_state
        )

        self.m = m
        self.error = error
        self.max_iter = max_iter

        self.centers_ = None
        self.membership_ = None
        self.fpc_ = None

    def fit(
        self,
        X
    ):

        X = np.asarray(X)

        cntr, u, _, _, _, _, fpc = fuzz.cluster.cmeans(
            X.T,
            c=self.n_clusters,
            m=self.m,
            error=self.error,
            maxiter=self.max_iter,
            seed=self.random_state
        )

        self.centers_ = cntr
        self.membership_ = u

        self.labels_ = np.argmax(
            u,
            axis=0
        )

        self.fpc_ = fpc

        self.model = {
            "centers": cntr,
            "fpc": fpc
        }

        return self

    def predict(
        self,
        X
    ):

        if self.centers_ is None:
            raise ValueError(
                "Model has not been fitted."
            )

        X = np.asarray(X)

        u, _, _, _, _, _ = fuzz.cluster.cmeans_predict(
            X.T,
            self.centers_,
            m=self.m,
            error=self.error,
            maxiter=self.max_iter
        )

        return np.argmax(
            u,
            axis=0
        )

    @property
    def centroids(self):

        return self.centers_

    @property
    def membership_matrix(self):

        return self.membership_

    @property
    def fuzzy_partition_coefficient(self):

        return self.fpc_


# =====================================================
# K-MODES
# =====================================================

class KModesCluster(BaseCentroidCluster):

    def __init__(
        self,
        n_clusters: int = 3,
        init: str = "Huang",
        n_init: int = 10,
        random_state: int = 42
    ):

        super().__init__(
            n_clusters=n_clusters,
            random_state=random_state
        )

        self.init = init
        self.n_init = n_init

    def fit(
        self,
        X
    ):

        self.model = KModes(
            n_clusters=self.n_clusters,
            init=self.init,
            n_init=self.n_init,
            random_state=self.random_state
        )

        self.labels_ = self.model.fit_predict(X)

        return self

    @property
    def centroids(self):

        if self.model is None:
            return None

        return self.model.cluster_centroids_


# =====================================================
# K-MEDOIDS
# =====================================================

class KMedoidsCluster(BaseCentroidCluster):

    def __init__(
        self,
        n_clusters: int = 3,
        random_state: int = 42
    ):

        super().__init__(
            n_clusters=n_clusters,
            random_state=random_state
        )

        self.X_ = None
        self.medoid_indices_ = None

    def fit(
        self,
        X
    ):

        X = np.asarray(X)

        self.X_ = X

        rng = np.random.default_rng(
            self.random_state
        )

        medoid_indices = rng.choice(
            len(X),
            self.n_clusters,
            replace=False
        )

        from sklearn.metrics import pairwise_distances
        dist_matrix = pairwise_distances(X, metric="euclidean")
        result = kmedoids.fasterpam(
            dist_matrix,
            medoid_indices
        )

        self.medoid_indices_ = result.medoids

        self.labels_ = result.labels

        self.model = result

        return self

    @property
    def centroids(self):

        if self.medoid_indices_ is None:
            return None

        return self.X_[
            self.medoid_indices_
        ]

    @property
    def medoids(self):

        return self.medoid_indices_


# =====================================================
# EXPORTS
# =====================================================

# Aliases to match imports in ML.Clustering.models
KMeans = KMeansPlusPlus
KMedoids = KMedoidsCluster
KModes = KModesCluster

__all__ = [
    "KMeansCluster",
    "KMeansPlusPlus",
    "FuzzyCMeansCluster",
    "KModesCluster",
    "KMedoidsCluster",
    "KMeans",
    "KMedoids",
    "KModes"
]