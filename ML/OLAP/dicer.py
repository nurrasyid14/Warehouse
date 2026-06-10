from __future__ import annotations

from .cube import Cube


def dice_cube(
    cube: Cube,
    **conditions
) -> Cube:
    """
    Multi-dimensional filter.

    Example
    -------
    dice_cube(
        cube,
        year=2025,
        month=3,
        division_name="Casting"
    )
    """

    df = cube.data.copy()

    for column, value in conditions.items():

        if column not in df.columns:

            raise ValueError(
                f"Column '{column}' "
                f"not found in cube."
            )

        if isinstance(
            value,
            (list, tuple, set)
        ):

            df = df[
                df[column].isin(value)
            ]

        else:

            df = df[
                df[column] == value
            ]

    return Cube(
        name=cube.name,
        data=df
    )