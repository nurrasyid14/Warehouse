from __future__ import annotations

from .cube import Cube


def aggregate_cube(
    cube: Cube,
    dimensions,
    measures,
    agg="sum"
) -> Cube:

    df = cube.data.copy()

    if isinstance(
        dimensions,
        str
    ):
        dimensions = [dimensions]

    if isinstance(
        measures,
        str
    ):
        measures = [measures]

    agg_dict = {
        m: agg
        for m in measures
    }

    result = (
        df.groupby(dimensions)
        .agg(agg_dict)
        .reset_index()
    )

    return Cube(
        name=f"{cube.name}_aggregate",
        data=result
    )