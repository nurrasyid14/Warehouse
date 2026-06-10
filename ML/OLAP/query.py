# ML/OLAP/query.py

from __future__ import annotations

from typing import Any


class CubeQuery:

    def __init__(
        self,
        cube_name: str
    ):

        self.cube_name = cube_name

        self._select = "*"
        self._where = []

        self._groupby = []
        self._orderby = []

        self._limit = None

    # ==========================================
    # FILTERS
    # ==========================================

    def where(
        self,
        column: str,
        value: Any
    ):

        if isinstance(value, str):

            clause = (
                f"{column} = '{value}'"
            )

        else:

            clause = (
                f"{column} = {value}"
            )

        self._where.append(
            clause
        )

        return self

    def between(
        self,
        column: str,
        start,
        end
    ):

        self._where.append(
            f"{column} BETWEEN '{start}' AND '{end}'"
        )

        return self

    # ==========================================
    # GROUPING
    # ==========================================

    def groupby(
        self,
        *columns
    ):

        self._groupby.extend(
            columns
        )

        return self

    # ==========================================
    # ORDERING
    # ==========================================

    def orderby(
        self,
        column,
        ascending=True
    ):

        direction = (
            "ASC"
            if ascending
            else "DESC"
        )

        self._orderby.append(
            f"{column} {direction}"
        )

        return self

    # ==========================================
    # LIMIT
    # ==========================================

    def limit(
        self,
        n: int
    ):

        self._limit = n

        return self

    # ==========================================
    # BUILD
    # ==========================================

    def sql(self):

        query = (
            f"SELECT {self._select} "
            f"FROM {self.cube_name}"
        )

        if self._where:

            query += (
                " WHERE "
                + " AND ".join(
                    self._where
                )
            )

        if self._groupby:

            query += (
                " GROUP BY "
                + ", ".join(
                    self._groupby
                )
            )

        if self._orderby:

            query += (
                " ORDER BY "
                + ", ".join(
                    self._orderby
                )
            )

        if self._limit:

            query += (
                f" LIMIT {self._limit}"
            )

        return query

    def __repr__(self):

        return self.sql()