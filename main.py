'''
OLTP [1]
 ↓
ETL [1]
 ↓
Data Warehouse [1]
 ↓
Data Mart [1]
 ↓
OLAP Cube [0]
 ↓
Aggregation Leveling [0]
(Daily / Weekly / Monthly)
 ↓
Feature Engineering [1]
 ↓
Scaling [0]
 ↓
Hyperparameter Search [0]
 ↓
Clustering [0]
 ↓
Cluster Evaluation [0]
 ↓
Cluster Stability Analysis [0]
 ↓
Forecasting [0]
 ↓
Forecast Evaluation [0]
 ↓
Aggregation Comparison [0]
 ↓
Knowledge Discovery [0]
 ↓
Decision Support [0]
'''

from .ML.Clustering.graphing.viz import (
    scatter_clusters, cluster_distribution, centroid_heatmap, metric_comparison,
    noise_ratio_plot, optics_reachability_plot, cluster_persistence_plot, dendrogram_plot
    )
from .ML.Clustering.evals import (
    silhouette, davies_bouldin, calinski_harabasz, ari, nmi, ami, noise_ratio, clustering_report
    )
from .ML.Clustering.models import (
    BaseCentroidCluster, KMeans, KMedoids, KModes, BaseDensityCluster, DBSCANCluster, OPTICSCluster,
    HDBSCANCluster, BaseHierarchicalCluster, AgglomerativeCluster, BisectingKMeansCluster,
    BaseDistributionCluster, GaussianMixtureCluster, BayesianGaussianMixtureCluster
    )
from .ML.Forecast import ARIMA, SARIMA, ARIMAX, SARIMAX, VAR
from .ML.Forecast.evals import (
    is_stationary, difference, inverse_difference, define_pipeline, 
    evaluate_forecast, mae, mse, rmse, mape, smape, r2
    )
from .ML.hyperparameter_tuner import ClusteringGridSearch, ForecastGridSearch, OLAPAggregationSearch
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.title("Impact of OLAP Aggregation Levels towards Clustering Accuracy and Forecasting Performance in Data Warehouse-driven Analytics")
st.markdown("""This project explores how different OLAP aggregation levels (Daily, Weekly, Monthly) affect the performance of clustering algorithms and forecasting models in a data warehouse context. We evaluate clustering stability and forecast accuracy across these aggregation levels to provide insights for optimal data warehousing strategies.""")


