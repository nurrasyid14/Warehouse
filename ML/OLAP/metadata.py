# ML/OLAP/metadata.py

from __future__ import annotations

import pandas as pd


class CubeMetadata:
    """
    Cube metadata inspector.

    Extracts:
    - dimensions
    - measures
    - time columns
    - numeric columns
    - categorical columns
    """

    TIME_COLUMNS = {
        "date",
        "date_id",
        "full_date",
        "year",
        "quarter",
        "month",
        "month_name",
        "week_of_year",
        "day",
        "day_name",
        "day_of_week",
        "is_weekend"
    }

    def __init__(
        self,
        dataframe: pd.DataFrame
    ):

        self.df = dataframe

    # ==================================================
    # BASIC
    # ==================================================

    @property
    def columns(self):

        return list(
            self.df.columns
        )

    @property
    def shape(self):

        return self.df.shape

    # ==================================================
    # NUMERIC
    # ==================================================

    @property
    def numeric_columns(self):

        return [
            col
            for col in self.df.columns
            if pd.api.types.is_numeric_dtype(
                self.df[col]
            )
        ]

    # ==================================================
    # CATEGORICAL
    # ==================================================

    @property
    def categorical_columns(self):

        return [
            col
            for col in self.df.columns
            if (
                self.df[col].dtype == "object"
                or str(
                    self.df[col].dtype
                ).startswith("category")
            )
        ]

    # ==================================================
    # TIME
    # ==================================================

    @property
    def time_columns(self):

        return [
            col
            for col in self.df.columns
            if col in self.TIME_COLUMNS
        ]

    # ==================================================
    # MEASURES
    # ==================================================

    @property
    def measures(self):

        excluded = set(
            self.time_columns
        )

        return [
            col
            for col in self.numeric_columns
            if col not in excluded
        ]

    # ==================================================
    # DIMENSIONS
    # ==================================================

    @property
    def dimensions(self):

        dimensions = []

        for col in self.df.columns:

            if col in self.time_columns:
                dimensions.append(col)

            elif col in self.categorical_columns:
                dimensions.append(col)

        return dimensions

    # ==================================================
    # UNIQUE COUNTS
    # ==================================================

    def cardinality(
        self,
        column: str
    ):

        if column not in self.df.columns:

            raise ValueError(
                f"{column} not found."
            )

        return int(
            self.df[column].nunique()
        )

    def cardinalities(self):

        return {
            col: int(
                self.df[col].nunique()
            )
            for col in self.df.columns
        }

    # ==================================================
    # DATA TYPES
    # ==================================================

    def dtypes(self):

        return {
            col: str(dtype)
            for col, dtype
            in self.df.dtypes.items()
        }

    # ==================================================
    # SUMMARY
    # ==================================================

    def summary(self):

        return {
            "rows": len(self.df),
            "columns": len(self.df.columns),

            "dimensions":
                self.dimensions,

            "measures":
                self.measures,

            "time_columns":
                self.time_columns,

            "numeric_columns":
                self.numeric_columns,

            "categorical_columns":
                self.categorical_columns
        }

    def __repr__(self):

        return (
            f"CubeMetadata("
            f"dimensions={len(self.dimensions)}, "
            f"measures={len(self.measures)}"
            f")"
        )