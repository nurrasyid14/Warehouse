from __future__ import annotations

from .cube import Cube


TIME_HIERARCHY = [
    "year",
    "quarter",
    "month",
    "week_of_year",
    "day"
]


def drilldown(
    cube: Cube,
    level: str
) -> Cube:

    df = cube.data.copy()

    if level not in TIME_HIERARCHY:

        raise ValueError(
            f"Invalid level: {level}"
        )

    idx = TIME_HIERARCHY.index(level)

    group_cols = [
        col
        for col in TIME_HIERARCHY[: idx + 1]
        if col in df.columns
    ]

    if not group_cols:

        raise ValueError(
            "No hierarchy columns found."
        )

    numeric_cols = [
        c
        for c in cube.measures
        if c not in group_cols
    ]

    agg_dict = {
        c: "sum"
        for c in numeric_cols
    }

    result = (
        df.groupby(group_cols)
        .agg(agg_dict)
        .reset_index()
    )

    return Cube(
        name=f"{cube.name}_drilldown_{level}",
        data=result
    )