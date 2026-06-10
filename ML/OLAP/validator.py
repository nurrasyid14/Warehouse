# ML/OLAP/validator.py

from __future__ import annotations

import pandas as pd


class CubeValidator:

    def __init__(
        self,
        cube
    ):

        self.cube = cube

    # ==========================================
    # EMPTY
    # ==========================================

    def has_rows(self):

        return len(
            self.cube.data
        ) > 0

    # ==========================================
    # NULLS
    # ==========================================

    def null_summary(self):

        return (
            self.cube.data
            .isnull()
            .sum()
        )

    def has_nulls(self):

        return (
            self.null_summary() > 0
        ).any()

    # ==========================================
    # DUPLICATES
    # ==========================================

    def duplicate_count(self):

        return int(
            self.cube.data
            .duplicated()
            .sum()
        )

    # ==========================================
    # DIMENSIONS
    # ==========================================

    def validate_dimensions(self):

        return len(
            self.cube.dimensions
        ) > 0

    # ==========================================
    # MEASURES
    # ==========================================

    def validate_measures(self):

        return len(
            self.cube.measures
        ) > 0

    # ==========================================
    # REPORT
    # ==========================================

    def report(self):

        return {
            "rows":
                len(self.cube),

            "columns":
                len(self.cube.columns),

            "dimensions":
                len(self.cube.dimensions),

            "measures":
                len(self.cube.measures),

            "duplicates":
                self.duplicate_count(),

            "has_nulls":
                self.has_nulls()
        }

    # ==========================================
    # PASS / FAIL
    # ==========================================

    def validate(self):

        checks = [

            self.has_rows(),

            self.validate_dimensions(),

            self.validate_measures()

        ]

        return all(
            checks
        )