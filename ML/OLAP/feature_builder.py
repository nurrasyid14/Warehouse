# ML/OLAP/feature_builder.py

from __future__ import annotations

import pandas as pd
import numpy as np

from .cube import Cube


class FeatureBuilder:

    def __init__(
        self,
        cube: Cube
    ):

        self.cube = cube

        self.df = cube.data.copy()

    # ==================================================
    # COLUMN SELECTION
    # ==================================================

    def select(
        self,
        columns: list[str]
    ):

        self.df = self.df[
            columns
        ].copy()

        return self

    # ==================================================
    # DROP COLUMNS
    # ==================================================

    def drop(
        self,
        columns: list[str]
    ):

        self.df = self.df.drop(
            columns=columns,
            errors="ignore"
        )

        return self

    # ==================================================
    # NUMERIC ONLY
    # ==================================================

    def numeric_only(self):

        self.df = self.df.select_dtypes(
            include=np.number
        )

        return self

    # ==================================================
    # CATEGORICAL ENCODING
    # ==================================================

    def one_hot_encode(
        self,
        columns=None
    ):

        self.df = pd.get_dummies(
            self.df,
            columns=columns,
            drop_first=False
        )

        return self

    # ==================================================
    # DATE FEATURES
    # ==================================================

    def datetime_features(
        self,
        column="full_date"
    ):

        if column not in self.df:

            return self

        dt = pd.to_datetime(
            self.df[column]
        )

        self.df[
            f"{column}_year"
        ] = dt.dt.year

        self.df[
            f"{column}_month"
        ] = dt.dt.month

        self.df[
            f"{column}_quarter"
        ] = dt.dt.quarter

        self.df[
            f"{column}_week"
        ] = dt.dt.isocalendar().week

        return self

    # ==================================================
    # LAG FEATURES
    # ==================================================

    def lag(
        self,
        column,
        periods=1
    ):

        self.df[
            f"{column}_lag_{periods}"
        ] = self.df[
            column
        ].shift(periods)

        return self

    # ==================================================
    # ROLLING FEATURES
    # ==================================================

    def rolling_mean(
        self,
        column,
        window=3
    ):

        self.df[
            f"{column}_rollmean_{window}"
        ] = (
            self.df[column]
            .rolling(window)
            .mean()
        )

        return self

    def rolling_std(
        self,
        column,
        window=3
    ):

        self.df[
            f"{column}_rollstd_{window}"
        ] = (
            self.df[column]
            .rolling(window)
            .std()
        )

        return self

    # ==================================================
    # RATIO FEATURES
    # ==================================================

    def ratio(
        self,
        numerator,
        denominator,
        new_name
    ):

        self.df[new_name] = (
            self.df[numerator]
            /
            self.df[denominator]
            .replace(0, np.nan)
        )

        return self

    # ==================================================
    # INTERACTION FEATURES
    # ==================================================

    def interaction(
        self,
        col1,
        col2,
        new_name=None
    ):

        if new_name is None:

            new_name = (
                f"{col1}_{col2}_interaction"
            )

        self.df[new_name] = (
            self.df[col1]
            *
            self.df[col2]
        )

        return self

    # ==================================================
    # LOG TRANSFORM
    # ==================================================

    def log_transform(
        self,
        column
    ):

        self.df[
            f"log_{column}"
        ] = np.log1p(
            self.df[column]
        )

        return self

    # ==================================================
    # FILL NULLS
    # ==================================================

    def fillna(
        self,
        value=0
    ):

        self.df = self.df.fillna(
            value
        )

        return self

    # ==================================================
    # BUILD
    # ==================================================

    def build(self):

        return self.df.copy()