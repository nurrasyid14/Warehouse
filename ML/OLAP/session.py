# ML/OLAP/session.py

from __future__ import annotations

import pandas as pd

from sqlalchemy import text

from .cube import Cube
from .query import CubeQuery

from .slicer import slice_cube
from .dicer import dice_cube

from .rollup import rollup
from .drilldown import drilldown

from .aggregation import aggregate_cube


class OLAPSession:

    def __init__(
        self,
        engine
    ):

        self.engine = engine

    # ==========================================
    # LOAD
    # ==========================================

    def load(
        self,
        cube_name: str
    ) -> Cube:

        query = (
            f"SELECT * "
            f"FROM {cube_name}"
        )

        df = pd.read_sql(
            query,
            self.engine
        )

        return Cube(
            name=cube_name,
            data=df
        )

    # ==========================================
    # QUERY BUILDER
    # ==========================================

    def query(
        self,
        cube_name: str
    ):

        return CubeQuery(
            cube_name
        )

    # ==========================================
    # EXECUTE SQL
    # ==========================================

    def execute(
        self,
        query: CubeQuery
    ) -> Cube:

        sql = query.sql()

        df = pd.read_sql(
            sql,
            self.engine
        )

        return Cube(
            name=query.cube_name,
            data=df
        )

    # ==========================================
    # CONVENIENCE WRAPPERS
    # ==========================================

    def slice(
        self,
        cube,
        column,
        value
    ):

        return slice_cube(
            cube,
            column,
            value
        )

    def dice(
        self,
        cube,
        filters
    ):

        return dice_cube(
            cube,
            filters
        )

    def rollup(
        self,
        cube,
        level
    ):

        return rollup(
            cube,
            level
        )

    def drilldown(
        self,
        cube,
        level
    ):

        return drilldown(
            cube,
            level
        )

    def aggregate(
        self,
        cube,
        dimensions,
        measures,
        agg="sum"
    ):

        return aggregate_cube(
            cube,
            dimensions,
            measures,
            agg
        )