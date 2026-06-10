from __future__ import annotations

from .cube import Cube


def slice_cube(
    cube: Cube,
    column: str,
    value
) -> Cube:
    """
    OLAP Slice.

    Memilih satu nilai dari satu dimensi.

    Example
    -------
    slice_cube(
        cube,
        "year",
        2025
    )
    """

    df = cube.data.copy()

    if column not in df.columns:

        raise ValueError(
            f"Column '{column}' not found."
        )

    df = df[
        df[column] == value
    ]

    return Cube(
        name=cube.name,
        data=df
    )