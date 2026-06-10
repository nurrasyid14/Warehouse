from __future__ import annotations

import pandas as pd

from sqlalchemy import text

from .cube import Cube


class CubeReader:

    def __init__(
        self,
        engine
    ):

        self.engine = engine

    def list_cubes(self):

        query = """
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema='public'
        ORDER BY table_name;
        """

        with self.engine.connect() as conn:

            result = conn.execute(
                text(query)
            )

            return [
                row[0]
                for row in result.fetchall()
            ]

    def read_sql(
        self,
        query: str
    ):

        return pd.read_sql(
            query,
            self.engine
        )

    def load(
        self,
        cube_name: str
    ) -> Cube:

        df = pd.read_sql(
            f"SELECT * FROM {cube_name}",
            self.engine
        )

        return Cube(
            name=cube_name,
            data=df
        )

    def head(
        self,
        cube_name: str,
        n: int = 5
    ):

        query = (
            f"SELECT * "
            f"FROM {cube_name} "
            f"LIMIT {n}"
        )

        return pd.read_sql(
            query,
            self.engine
        )