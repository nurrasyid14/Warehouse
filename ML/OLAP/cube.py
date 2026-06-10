from __future__ import annotations

import pandas as pd

from .metadata import CubeMetadata


class Cube:
    """
    OLAP Cube wrapper.

    Stores:
    - cube name
    - dataframe
    - metadata
    """

    def __init__(
        self,
        name: str,
        data: pd.DataFrame
    ):

        self.name = name
        self.data = data

        self.metadata = CubeMetadata(
            self.data
        )

    # ==================================================
    # BASIC INFO
    # ==================================================

    @property
    def shape(self):

        return self.data.shape

    @property
    def columns(self):

        return self.metadata.columns

    # ==================================================
    # DIMENSIONS & MEASURES
    # ==================================================

    @property
    def dimensions(self):

        return self.metadata.dimensions

    @property
    def measures(self):

        return self.metadata.measures

    @property
    def time_columns(self):

        return self.metadata.time_columns

    @property
    def numeric_columns(self):

        return self.metadata.numeric_columns

    @property
    def categorical_columns(self):

        return self.metadata.categorical_columns

    # ==================================================
    # INSPECTION
    # ==================================================

    def summary(self):

        return self.metadata.summary()

    def cardinality(
        self,
        column: str
    ):

        return self.metadata.cardinality(
            column
        )

    def cardinalities(self):

        return self.metadata.cardinalities()

    def dtypes(self):

        return self.metadata.dtypes()

    # ==================================================
    # DATAFRAME OPERATIONS
    # ==================================================

    def head(
        self,
        n: int = 5
    ):

        return self.data.head(n)

    def tail(
        self,
        n: int = 5
    ):

        return self.data.tail(n)

    def describe(self):

        return self.data.describe(
            include="all"
        )

    def sample(
        self,
        n: int = 5,
        random_state: int = 42
    ):

        return self.data.sample(
            n=n,
            random_state=random_state
        )

    def copy(self):

        return Cube(
            name=self.name,
            data=self.data.copy()
        )

    def to_dataframe(self):

        return self.data.copy()

    # ==================================================
    # MAGIC METHODS
    # ==================================================

    def __len__(self):

        return len(
            self.data
        )

    def __getitem__(
        self,
        key
    ):

        return self.data[key]

    def __repr__(self):

        return (
            f"Cube("
            f"name='{self.name}', "
            f"rows={len(self.data)}, "
            f"cols={self.data.shape[1]}, "
            f"dimensions={len(self.dimensions)}, "
            f"measures={len(self.measures)}"
            f")"
        )