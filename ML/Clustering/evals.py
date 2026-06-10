from __future__ import annotations

import numpy as np

from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,

    adjusted_rand_score,
    normalized_mutual_info_score,
    adjusted_mutual_info_score
)


# =====================================================
# INTERNAL METRICS
# =====================================================

def silhouette(
    X,
    labels
) -> float:
    """
    Higher is better.
    Range:
    -1 to 1
    """

    return silhouette_score(
        X,
        labels
    )


def davies_bouldin(
    X,
    labels
) -> float:
    """
    Lower is better.
    """

    return davies_bouldin_score(
        X,
        labels
    )


def calinski_harabasz(
    X,
    labels
) -> float:
    """
    Higher is better.
    """

    return calinski_harabasz_score(
        X,
        labels
    )


# =====================================================
# STABILITY METRICS
# =====================================================

def ari(
    labels_a,
    labels_b
) -> float:
    """
    Adjusted Rand Index.

    Range:
    -1 to 1

    Higher is better.
    """

    return adjusted_rand_score(
        labels_a,
        labels_b
    )


def nmi(
    labels_a,
    labels_b
) -> float:
    """
    Normalized Mutual Information.

    Range:
    0 to 1
    """

    return normalized_mutual_info_score(
        labels_a,
        labels_b
    )


def ami(
    labels_a,
    labels_b
) -> float:
    """
    Adjusted Mutual Information.

    Range:
    0 to 1
    """

    return adjusted_mutual_info_score(
        labels_a,
        labels_b
    )


# =====================================================
# DENSITY METRICS
# =====================================================

def noise_ratio(
    labels
) -> float:
    """
    Percentage of noise observations.

    DBSCAN/HDBSCAN only.
    """

    labels = np.asarray(
        labels
    )

    return np.mean(
        labels == -1
    )


# =====================================================
# SUMMARY
# =====================================================

def clustering_report(
    X,
    labels
):

    return {
        "silhouette":
            silhouette(
                X,
                labels
            ),

        "davies_bouldin":
            davies_bouldin(
                X,
                labels
            ),

        "calinski_harabasz":
            calinski_harabasz(
                X,
                labels
            )
    }

def evaluate_clustering(
    X,
    labels
):

    return clustering_report(
        X,
        labels
    )

__all__ = [
    "silhouette",
    "davies_bouldin",
    "calinski_harabasz",
    "ari",
    "nmi",
    "ami",
    "noise_ratio",
    "clustering_report",
    "evaluate_clustering"
]