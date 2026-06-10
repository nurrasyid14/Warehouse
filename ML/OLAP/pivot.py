from __future__ import annotations

import pandas as pd

from .cube import Cube


def pivot_cube(
    cube: Cube,
    index,
    columns,
    values,
    aggfunc="sum"
) -> pd.DataFrame:

    return pd.pivot_table(
        cube.data,
        index=index,
        columns=columns,
        values=values,
        aggfunc=aggfunc,
        fill_value=0
    )