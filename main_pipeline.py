"""
Main Analytical Pipeline for Warehouse DW / OLAP
=================================================
This module contains analytical pipeline functions that prepare data, run
clustering (all families), perform time series forecasting (ARIMA), execute
decompositions, correlation, and sensitivity studies.

It is exposed through the ML package so that main.py can easily render the dashboard.
"""

import os
import sys
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.seasonal import seasonal_decompose

# Import models & metrics directly to avoid circular dependency
from ML.Clustering.models import (
    KMeans, KMedoids,
    DBSCANCluster, OPTICSCluster, HDBSCANCluster,
    AgglomerativeCluster, BisectingKMeansCluster,
    GaussianMixtureCluster, BayesianGaussianMixtureCluster
)
from ML.Clustering.evals import ari, nmi, ami, silhouette, davies_bouldin, calinski_harabasz
from ML.Forecast.arima import ARIMA, SARIMA
from ML.Forecast.var import VAR
from ML.Forecast.evals import mae, rmse, mape
from Workshop import tables

# Global cache to share state/results between functions if needed
_cache_store = {}

# =====================================================================
# Helper: Dynamic, Contextual Cluster Naming
# =====================================================================
def _name_clusters(df: pd.DataFrame, labels: np.ndarray) -> tuple[list[str], dict[int, str]]:
    """
    Dynamically assigns contextual names to clusters based on their centroids/means.
    Handles both raw facts and aggregated employee metrics.
    """
    df_temp = df.copy()
    df_temp["__cluster_label"] = labels
    
    # Filter out noise/outliers (-1) from centroid calculation
    valid_labels = labels[labels != -1]
    if len(valid_labels) == 0:
        return ["Noise / Outliers"] * len(labels), {-1: "Noise / Outliers"}
        
    cluster_means = df_temp.groupby("__cluster_label").mean(numeric_only=True)
    
    # Identify key columns for naming
    # Raw features vs Aggregated features
    prod_col = "productivity_index" if "productivity_index" in cluster_means.columns else "avg_productivity"
    defect_col = "defect_rate" if "defect_rate" in cluster_means.columns else "avg_defect_rate"
    
    # Rank clusters by productivity
    sorted_by_prod = cluster_means[prod_col].sort_values(ascending=False).index.tolist()
    # Find cluster with highest defect rate
    highest_defect_cluster = cluster_means[defect_col].idxmax()
    defect_threshold = cluster_means[defect_col].mean()
    
    names = {}
    for cid in cluster_means.index:
        if cid == -1:
            names[cid] = "Noise / Outliers"
        elif cid == highest_defect_cluster and cluster_means.loc[cid, defect_col] > defect_threshold:
            names[cid] = "High-Defect Risk Production"
        elif cid == sorted_by_prod[0]:
            names[cid] = "High-Efficiency Production"
        elif cid == sorted_by_prod[-1] and len(sorted_by_prod) > 2:
            names[cid] = "Underperforming / Low-Efficiency"
        else:
            names[cid] = "Standard Performance"
            
    # Assign named labels to output list
    named_labels = [names.get(l, f"Cluster {l}") for l in labels]
    return named_labels, names


# =====================================================================
# Pipeline 1: Data Preparation
# =====================================================================
def data_preparation(use_aggregate: bool) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Preprocesses, scales features, and builds time series.
    
    Parameters
    ----------
    use_aggregate : bool
        If True, loads aggregated Monthly Cubes.
        If False, loads raw OLTP facts.
        
    Returns
    -------
    df_features : pd.DataFrame
        Scaled numerical features for clustering, including mapping keys.
    ts_df : pd.DataFrame
        Sorted time series dataframe for forecasting.
    """
    if not use_aggregate:
        # Load Raw OLTP facts
        df_raw = tables.fact_production.copy()
        
        # Columns for clustering
        feature_cols = [
            "planned_quantity", 
            "actual_quantity", 
            "defects", 
            "production_minutes", 
            "defect_rate", 
            "productivity_index"
        ]
        df_clean = df_raw.dropna(subset=["employee_id", "production_date"]).copy()
        
        # Add a helper month column for alignment
        df_clean["month"] = pd.to_datetime(df_clean["production_date"]).dt.month
        
        # Fill missing numeric values
        df_clean[feature_cols] = df_clean[feature_cols].fillna(0)
        
        # Preprocessing & Scaling
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(df_clean[feature_cols])
        
        df_scaled = pd.DataFrame(scaled_features, columns=feature_cols, index=df_clean.index)
        
        # Keep keys for grouping/stability alignment
        df_features = df_clean[["employee_id", "month"] + feature_cols].copy()
        for col in feature_cols:
            df_features[f"scaled_{col}"] = df_scaled[col]
            
        # Time Series Prep (Daily output and defects for VAR)
        ts_df = df_clean.groupby("production_date")[["actual_quantity", "defects"]].sum().reset_index()
        ts_df.rename(columns={"production_date": "date", "actual_quantity": "output"}, inplace=True)
        ts_df["date"] = pd.to_datetime(ts_df["date"])
        ts_df.sort_values("date", inplace=True)
        ts_df.set_index("date", inplace=True)
        
    else:
        # Load OLAP Aggregated Cubes
        df_cube = tables.cube_employee_monthly.copy()
        
        feature_cols = [
            "total_runs", 
            "total_output", 
            "total_defects", 
            "avg_defect_rate", 
            "avg_productivity", 
            "good_output"
        ]
        df_clean = df_cube.dropna(subset=["employee_id", "month"]).copy()
        df_clean[feature_cols] = df_clean[feature_cols].fillna(0)
        
        # Preprocessing & Scaling
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(df_clean[feature_cols])
        
        df_scaled = pd.DataFrame(scaled_features, columns=feature_cols, index=df_clean.index)
        
        df_features = df_clean[["employee_id", "month"] + feature_cols].copy()
        for col in feature_cols:
            df_features[f"scaled_{col}"] = df_scaled[col]
            
        # Time Series Prep (Monthly output and defects from cube_forecast_monthly for VAR)
        df_ts_monthly = tables.cube_forecast_monthly.copy()
        # Construct date index
        df_ts_monthly["date"] = pd.to_datetime(
            df_ts_monthly["year"].astype(str) + "-" + df_ts_monthly["month"].astype(str) + "-01"
        )
        ts_df = df_ts_monthly.groupby("date")[["total_output", "total_defects"]].sum().reset_index()
        ts_df.rename(columns={"total_output": "output", "total_defects": "defects"}, inplace=True)
        ts_df.sort_values("date", inplace=True)
        ts_df.set_index("date", inplace=True)
        
    return df_features, ts_df


# =====================================================================
# Pipeline 2: Correlation Analysis
# =====================================================================
def correlation_analysis(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Computes Pearson and Spearman correlation matrices for the fact columns.
    """
    # Select feature columns (non-scaled, numeric columns)
    num_cols = [c for c in df.columns if not c.startswith("scaled_") and c not in ["employee_id", "month"]]
    df_num = df[num_cols].copy()
    
    pearson_corr = df_num.corr(method="pearson")
    spearman_corr = df_num.corr(method="spearman")
    
    return pearson_corr, spearman_corr


# =====================================================================
# Pipeline 3: Clustering Analysis
# =====================================================================
def clustering_analysis(df_features: pd.DataFrame, use_aggregate: bool) -> dict:
    """
    Fits models from each of the clustering families and computes metrics + stability.
    """
    # Get scaled columns for training
    scaled_cols = [c for c in df_features.columns if c.startswith("scaled_")]
    X = df_features[scaled_cols].values
    
    # Instantiate all 9 clustering models
    models_dict = {
        "KMeans": KMeans(n_clusters=3, random_state=42),
        "KMedoids": KMedoids(n_clusters=3, random_state=42),
        "DBSCAN": DBSCANCluster(eps=0.5, min_samples=5),
        "OPTICS": OPTICSCluster(min_samples=5),
        "HDBSCAN": HDBSCANCluster(min_cluster_size=5),
        "Agglomerative": AgglomerativeCluster(n_clusters=3),
        "BisectingKMeans": BisectingKMeansCluster(n_clusters=3, random_state=42),
        "GaussianMixture": GaussianMixtureCluster(n_clusters=3, random_state=42),
        "BayesianGaussianMixture": BayesianGaussianMixtureCluster(n_clusters=3, random_state=42)
    }
    
    def _fit_model(model_obj, X_data, model_name):
        if model_name in ["GaussianMixture", "BayesianGaussianMixture"]:
            return model_obj.fit_predict(X_data)
        model_obj.fit(X_data)
        return model_obj.labels_

    results = {}
    cached_labels = {}
    
    for name, model in models_dict.items():
        try:
            labels = _fit_model(model, X, name)
        except Exception:
            # Fallback if any model errors out
            labels = np.zeros(len(X), dtype=int)
            
        cached_labels[name] = labels
        
        # Calculate silhouette, DB, and CH scores safely
        # Filter out noise label (-1) for score calculation
        mask = labels != -1
        unique_lbls = np.unique(labels[mask])
        
        if len(unique_lbls) >= 2:
            sil = silhouette(X[mask], labels[mask])
            db_val = davies_bouldin(X[mask], labels[mask])
            ch = calinski_harabasz(X[mask], labels[mask])
        else:
            sil, db_val, ch = -1.0, 99.0, 0.0
            
        # Get contextual names
        named_labels, name_map = _name_clusters(df_features, labels)
        
        results[name] = {
            "labels": labels,
            "named_labels": named_labels,
            "name_mapping": name_map,
            "metrics": {
                "silhouette": sil,
                "davies_bouldin": db_val,
                "calinski_harabasz": ch
            }
        }
        
    # Store in cache for stability calculation
    key = "agg" if use_aggregate else "raw"
    _cache_store[f"cluster_{key}"] = {
        "df": df_features,
        "labels": cached_labels
    }
    
    return results


# =====================================================================
# Pipeline 4: Stability Calculation (Raw vs Aggregated alignment)
# =====================================================================
def calculate_stability() -> dict:
    """
    Computes ARI, NMI, and AMI between raw and aggregated labels
    for all clustering families by aligning production runs to
    employee-months using mode aggregation.
    """
    raw_data = _cache_store.get("cluster_raw")
    agg_data = _cache_store.get("cluster_agg")
    
    if not raw_data or not agg_data:
        # Fallback if both pipelines haven't run yet
        # Run them dynamically
        raw_df, _ = data_preparation(False)
        clustering_analysis(raw_df, False)
        
        agg_df, _ = data_preparation(True)
        clustering_analysis(agg_df, True)
        
        raw_data = _cache_store["cluster_raw"]
        agg_data = _cache_store["cluster_agg"]
        
    df_raw = raw_data["df"].copy()
    df_agg = agg_data["df"].copy()
    
    raw_labels_dict = raw_data["labels"]
    agg_labels_dict = agg_data["labels"]
    
    stability_results = {}
    families = [
        "KMeans", "KMedoids", "DBSCAN", "OPTICS", "HDBSCAN", 
        "Agglomerative", "BisectingKMeans", "GaussianMixture", "BayesianGaussianMixture"
    ]
    
    for family in families:
        if family not in raw_labels_dict or family not in agg_labels_dict:
            stability_results[family] = {"ari": 0.0, "nmi": 0.0, "ami": 0.0}
            continue
            
        lbls_raw = raw_labels_dict[family]
        lbls_agg = agg_labels_dict[family]
        
        df_raw_temp = df_raw.copy()
        df_raw_temp["label"] = lbls_raw
        
        df_agg_temp = df_agg.copy()
        df_agg_temp["agg_label"] = lbls_agg
        
        # Aggregate raw labels by employee_id and month (using majority vote / mode)
        # This aligns the grain to employee-month
        raw_modes = (
            df_raw_temp.groupby(["employee_id", "month"])["label"]
            .agg(lambda x: x.mode().iloc[0] if not x.empty else -1)
            .reset_index()
        )
        
        # Merge mode labels with cube labels
        aligned = pd.merge(
            raw_modes, 
            df_agg_temp[["employee_id", "month", "agg_label"]], 
            on=["employee_id", "month"], 
            how="inner"
        )
        
        if len(aligned) == 0:
            stability_results[family] = {"ari": 0.0, "nmi": 0.0, "ami": 0.0}
        else:
            stability_results[family] = {
                "ari": ari(aligned["label"], aligned["agg_label"]),
                "nmi": nmi(aligned["label"], aligned["agg_label"]),
                "ami": ami(aligned["label"], aligned["agg_label"])
            }
            
    return stability_results


# =====================================================================
# Pipeline 5: Forecasting Analysis
# =====================================================================
def forecasting_analysis(ts_df: pd.DataFrame, use_aggregate: bool) -> dict:
    """
    Fits ARIMA, SARIMA, and VAR models, and computes metrics for each.
    """
    if not use_aggregate:
        # Daily: Split train (all except last 30 days) and test (last 30 days)
        test_size = 30
    else:
        # Monthly: Split train (first 9 months) and test (last 3 months)
        test_size = 3
        
    train_df = ts_df.iloc[:-test_size]
    test_df = ts_df.iloc[-test_size:]
    
    y_train = train_df["output"]
    y_test = test_df["output"]
    
    results = {}
    
    # 1. ARIMA
    try:
        arima_model = ARIMA(p=1, d=1, q=1)
        arima_model.fit(y_train.values)
        arima_fc = arima_model.forecast(steps=test_size)
        results["ARIMA"] = {
            "forecast": pd.Series(arima_fc, index=y_test.index),
            "metrics": {
                "mae": mae(y_test.values, arima_fc),
                "rmse": rmse(y_test.values, arima_fc),
                "mape": mape(y_test.values, arima_fc)
            }
        }
    except Exception as e:
        results["ARIMA"] = {"error": str(e)}
        
    # 2. SARIMA
    try:
        s = 3 if use_aggregate else 7
        sarima_model = SARIMA(p=1, d=1, q=1, P=1, D=1, Q=1, s=s)
        sarima_model.fit(y_train.values)
        sarima_fc = sarima_model.forecast(steps=test_size)
        results["SARIMA"] = {
            "forecast": pd.Series(sarima_fc, index=y_test.index),
            "metrics": {
                "mae": mae(y_test.values, sarima_fc),
                "rmse": rmse(y_test.values, sarima_fc),
                "mape": mape(y_test.values, sarima_fc)
            }
        }
    except Exception as e:
        results["SARIMA"] = {"error": str(e)}
        
    # 3. VAR
    try:
        var_model = VAR(p=1)
        var_model.fit(train_df[["output", "defects"]])
        var_fc_df = var_model.forecast(steps=test_size)
        var_fc = var_fc_df["output"].values
        results["VAR"] = {
            "forecast": pd.Series(var_fc, index=y_test.index),
            "metrics": {
                "mae": mae(y_test.values, var_fc),
                "rmse": rmse(y_test.values, var_fc),
                "mape": mape(y_test.values, var_fc)
            }
        }
    except Exception as e:
        results["VAR"] = {"error": str(e)}
        
    return {
        "train": y_train,
        "test": y_test,
        "results": results
    }


# =====================================================================
# Pipeline 6: Timeseries Decomposition
# =====================================================================
def timeseries_decomposition(ts_df: pd.DataFrame) -> dict:
    """
    Decomposes the output time series into Trend, Seasonal, and Residual.
    """
    series = ts_df["output"].copy()
    
    # Select appropriate period: 7 for daily, 3 for monthly due to short length
    period = 7 if len(series) > 30 else 3
    
    decomposition = seasonal_decompose(series, model="additive", period=period)
    
    return {
        "observed": series,
        "trend": decomposition.trend,
        "seasonal": decomposition.seasonal,
        "resid": decomposition.resid
    }


# =====================================================================
# Pipeline 7: Sensitivity Analysis
# =====================================================================
def sensitivity_analysis(df_features: pd.DataFrame) -> dict:
    """
    Varies hyperparameter (n_clusters) for KMeans to show sensitivity.
    """
    scaled_cols = [c for c in df_features.columns if c.startswith("scaled_")]
    X = df_features[scaled_cols].values
    
    k_range = [2, 3, 4, 5, 6]
    silhouette_scores = []
    
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42)
        labels = km.fit_predict(X)
        if len(np.unique(labels)) >= 2:
            silhouette_scores.append(silhouette(X, labels))
        else:
            silhouette_scores.append(-1.0)
            
    return {
        "k_values": k_range,
        "scores": silhouette_scores
    }


# =====================================================================
# Pipeline 8: Dashboard Generation (Plotly visual creators)
# =====================================================================
def dashboard_generation(use_aggregate: bool) -> dict:
    """
    Runs the entire pipeline for the given toggle state (aggregated vs raw)
    and returns a dictionary of plotly figures and metrics.
    """
    df_features, ts_df = data_preparation(use_aggregate)
    
    # 1. Correlation Heatmap
    p_corr, _ = correlation_analysis(df_features)
    fig_corr = px.imshow(
        p_corr, 
        text_auto=True, 
        aspect="auto", 
        color_continuous_scale="RdBu_r",
        title="Fact Variables Correlation Matrix (Pearson)"
    )
    fig_corr.update_layout(coloraxis_showscale=False)
    
    # 2. Clustering Analysis
    cluster_results = clustering_analysis(df_features, use_aggregate)
    
    # Gather metrics comparison across all 9 models
    models = list(cluster_results.keys())
    sils = [cluster_results[m]["metrics"]["silhouette"] for m in models]
    dbs = [cluster_results[m]["metrics"]["davies_bouldin"] for m in models]
    
    # Metric comparison figure
    fig_metrics = go.Figure(data=[
        go.Bar(name="Silhouette (Higher is Better)", x=models, y=sils, marker_color="#1f77b4"),
        go.Bar(name="Davies-Bouldin (Lower is Better)", x=models, y=dbs, marker_color="#aec7e8")
    ])
    fig_metrics.update_layout(
        barmode="group", 
        title="Clustering Quality Comparison across Model Families",
        yaxis_title="Metric Score"
    )
    
    # Cluster Scatter Plot (KMeans as baseline)
    km_res = cluster_results["KMeans"]
    x_axis = "actual_quantity" if "actual_quantity" in df_features.columns else "total_output"
    y_axis = "defects" if "defects" in df_features.columns else "total_defects"
    
    fig_scatter = px.scatter(
        df_features,
        x=x_axis,
        y=y_axis,
        color=km_res["named_labels"],
        labels={"color": "Manufacturing Profile"},
        title=f"KMeans Clustering Profile ({'Aggregated Cubes' if use_aggregate else 'Raw OLTP Facts'})"
    )
    fig_scatter.update_traces(marker=dict(size=8, opacity=0.8, line=dict(width=1, color="DarkSlateGrey")))
    
    # 3. Forecasting Analysis
    fc_results = forecasting_analysis(ts_df, use_aggregate)
    train_ser = fc_results["train"]
    test_ser = fc_results["test"]
    
    # Plot multi-model forecast
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(x=train_ser.index, y=train_ser.values, name="Training Data", line=dict(color="#1f77b4")))
    fig_forecast.add_trace(go.Scatter(x=test_ser.index, y=test_ser.values, name="Actual Output", line=dict(color="#2ca02c")))
    
    colors = {"ARIMA": "#d62728", "SARIMA": "#9467bd", "VAR": "#ff7f0e"}
    dashes = {"ARIMA": "dash", "SARIMA": "dot", "VAR": "longdash"}
    
    for model_name, model_data in fc_results["results"].items():
        if "error" not in model_data:
            fc_ser = model_data["forecast"]
            fig_forecast.add_trace(go.Scatter(
                x=fc_ser.index, 
                y=fc_ser.values, 
                name=f"{model_name} Forecast", 
                line=dict(color=colors.get(model_name, "#7f7f7f"), dash=dashes.get(model_name, "solid"))
            ))
            
    fig_forecast.update_layout(
        title="Production Output Forecasting Multi-Model Comparison",
        xaxis_title="Timeline",
        yaxis_title="Output Quantity"
    )
    
    # 4. Timeseries Decomposition Plot
    dec_results = timeseries_decomposition(ts_df)
    obs = dec_results["observed"]
    trend = dec_results["trend"]
    seasonal = dec_results["seasonal"]
    resid = dec_results["resid"]
    
    fig_decomp = make_subplots(rows=4, cols=1, shared_xaxes=True, subplot_titles=("Observed", "Trend", "Seasonal", "Residual"))
    fig_decomp.add_trace(go.Scatter(x=obs.index, y=obs.values, name="Observed", line=dict(color="#1f77b4")), row=1, col=1)
    fig_decomp.add_trace(go.Scatter(x=trend.index, y=trend.values, name="Trend", line=dict(color="#ff7f0e")), row=2, col=1)
    fig_decomp.add_trace(go.Scatter(x=seasonal.index, y=seasonal.values, name="Seasonal", line=dict(color="#2ca02c")), row=3, col=1)
    fig_decomp.add_trace(go.Scatter(x=resid.index, y=resid.values, name="Residual", line=dict(color="#7f7f7f")), row=4, col=1)
    fig_decomp.update_layout(height=600, title_text="Additive Seasonal Decomposition", showlegend=False)
    
    # 5. Sensitivity Analysis Plot
    sens_results = sensitivity_analysis(df_features)
    fig_sens = px.line(
        x=sens_results["k_values"],
        y=sens_results["scores"],
        markers=True,
        title="KMeans Silhouette Score Sensitivity Analysis (Varying clusters k)",
        labels={"x": "Number of Clusters (k)", "y": "Silhouette Score"}
    )
    
    # 6. Stability comparison (ARI, NMI, AMI)
    stability_metrics = calculate_stability()
    
    # Prepare data for multi-family plotting
    stability_data = []
    for family, metrics in stability_metrics.items():
        for index_name, val in metrics.items():
            stability_data.append({
                "Clustering Family": family,
                "Stability Index": {
                    "ari": "Adjusted Rand Index (ARI)",
                    "nmi": "Normalized Mutual Info (NMI)",
                    "ami": "Adjusted Mutual Info (AMI)"
                }.get(index_name, index_name),
                "Agreement Level": val
            })
    df_stab_plot = pd.DataFrame(stability_data)
    
    fig_stability = px.bar(
        df_stab_plot,
        x="Stability Index",
        y="Agreement Level",
        color="Clustering Family",
        barmode="group",
        title="Clustering Stability: Raw OLTP Facts vs. Monthly Cubes across Method Families",
        labels={"Agreement Level": "Agreement Level (0 to 1)", "Stability Index": "Stability Index"},
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig_stability.update_yaxes(range=[0, 1])
    
    return {
        "figs": {
            "correlation": fig_corr,
            "scatter": fig_scatter,
            "metrics_comparison": fig_metrics,
            "forecast": fig_forecast,
            "decomposition": fig_decomp,
            "sensitivity": fig_sens,
            "stability": fig_stability
        },
        "metrics": {
            "clustering": {m: cluster_results[m]["metrics"] for m in cluster_results},
            "forecasting": {m: fc_results["results"][m]["metrics"] for m in fc_results["results"] if "metrics" in fc_results["results"][m]},
            "stability": stability_metrics
        },
        "cluster_results": cluster_results,
        "df_features": df_features,
        "forecast_results": fc_results
    }

