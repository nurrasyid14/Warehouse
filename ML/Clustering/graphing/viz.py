from __future__ import annotations

import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

from scipy.cluster.hierarchy import dendrogram


# =====================================================
# CLUSTER SCATTER
# =====================================================

def scatter_clusters(
    X,
    labels,
    x_col=None,
    y_col=None,
    title="Cluster Scatter"
):

    df = pd.DataFrame(X)

    df["cluster"] = labels.astype(str)

    if x_col is None:
        x_col = df.columns[0]

    if y_col is None:
        y_col = df.columns[1]

    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color="cluster",
        title=title
    )

    return fig


# =====================================================
# CLUSTER DISTRIBUTION
# =====================================================

def cluster_distribution(
    labels,
    title="Cluster Distribution"
):

    counts = (
        pd.Series(labels)
        .value_counts()
        .sort_index()
    )

    fig = px.bar(
        x=counts.index.astype(str),
        y=counts.values,
        labels={
            "x": "Cluster",
            "y": "Count"
        },
        title=title
    )

    return fig


# =====================================================
# CENTROIDS
# =====================================================

def centroid_heatmap(
    centroids,
    title="Cluster Centroids"
):

    fig = px.imshow(
        centroids,
        aspect="auto",
        title=title
    )

    return fig


# =====================================================
# SILHOUETTE COMPARISON
# =====================================================

def metric_comparison(
    results_df,
    metric="silhouette",
    title="Model Comparison"
):

    fig = px.bar(
        results_df,
        x="model",
        y=metric,
        title=title
    )

    return fig


# =====================================================
# NOISE RATIO
# =====================================================

def noise_ratio_plot(
    labels,
    title="Noise vs Clustered"
):

    labels = np.asarray(labels)

    noise = np.sum(labels == -1)

    clustered = np.sum(labels != -1)

    fig = px.pie(
        names=["Clustered", "Noise"],
        values=[clustered, noise],
        title=title
    )

    return fig


# =====================================================
# OPTICS REACHABILITY
# =====================================================

def optics_reachability_plot(
    reachability,
    ordering,
    title="OPTICS Reachability Plot"
):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=np.arange(len(ordering)),
            y=reachability[ordering],
            mode="lines"
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Ordering",
        yaxis_title="Reachability Distance"
    )

    return fig


# =====================================================
# HDBSCAN PERSISTENCE
# =====================================================

def cluster_persistence_plot(
    persistence,
    title="Cluster Persistence"
):

    fig = px.bar(
        x=np.arange(len(persistence)),
        y=persistence,
        labels={
            "x": "Cluster",
            "y": "Persistence"
        },
        title=title
    )

    return fig


# =====================================================
# DENDROGRAM
# =====================================================

def dendrogram_plot(
    linkage_matrix,
    title="Dendrogram"
):

    dendro = dendrogram(
        linkage_matrix,
        no_plot=True
    )

    fig = go.Figure()

    for xs, ys in zip(
        dendro["icoord"],
        dendro["dcoord"]
    ):

        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="lines"
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Samples",
        yaxis_title="Distance"
    )

    return fig