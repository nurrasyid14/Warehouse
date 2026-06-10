from __future__ import annotations

import pandas as pd

from .cube import Cube


DEFAULT_AGGREGATIONS = {
    "sum": [
        "total_output",
        "total_defects",
        "good_output",
        "planned_quantity",
        "actual_quantity",
        "production_minutes",
        "runs"
    ],

    "mean": [
        "avg_productivity",
        "avg_defect_rate",
        "defect_rate",
        "productivity_index"
    ]
}


def rollup(
    cube: Cube,
    level: str
) -> Cube:
    """
    Rollup aggregation.

    day -> week
    week -> month
    month -> quarter
    quarter -> year

    Example
    -------
    rollup(
        cube,
        level="month"
    )
    """

    df = cube.data.copy()

    hierarchy = {
        "day": [
            "year",
            "month",
            "day"
        ],

        "week": [
            "year",
            "week_of_year"
        ],

        "month": [
            "year",
            "month"
        ],

        "quarter": [
            "year",
            "quarter"
        ],

        "year": [
            "year"
        ]
    }

    if level not in hierarchy:

        raise ValueError(
            f"Unsupported level '{level}'."
        )

    group_cols = [
        c
        for c in hierarchy[level]
        if c in df.columns
    ]

    if not group_cols:

        raise ValueError(
            f"No hierarchy columns found "
            f"for level '{level}'."
        )

    agg_dict = {}

    for col in df.columns:

        if col in group_cols:
            continue

        if pd.api.types.is_numeric_dtype(
            df[col]
        ):

            if (
                col
                in DEFAULT_AGGREGATIONS["mean"]
            ):

                agg_dict[col] = "mean"

            else:

                agg_dict[col] = "sum"

    rolled = (
        df.groupby(
            group_cols,
            dropna=False
        )
        .agg(
            agg_dict
        )
        .reset_index()
    )

    return Cube(
        name=f"{cube.name}_{level}",
        data=rolled
    )