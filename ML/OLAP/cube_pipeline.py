# ML/OLAP/cube_pipeline.py

from __future__ import annotations

from .validator import CubeValidator


class CubePipeline:

    def __init__(
        self,
        cube
    ):

        self.cube = cube

        self.validator = CubeValidator(
            cube
        )

    # ==========================================
    # VALIDATE
    # ==========================================

    def validate(self):

        return (
            self.validator
            .validate()
        )

    # ==========================================
    # TRANSFORM
    # ==========================================

    def transform(
        self,
        func,
        *args,
        **kwargs
    ):

        self.cube = func(
            self.cube,
            *args,
            **kwargs
        )

        return self

    # ==========================================
    # CLUSTER
    # ==========================================

    def cluster(
        self,
        model,
        features
    ):

        X = self.cube.data[
            features
        ]

        model.fit(X)

        self.cube.data[
            "cluster"
        ] = model.labels_

        return self

    # ==========================================
    # FORECAST
    # ==========================================

    def forecast(
        self,
        model,
        data
    ):

        model.fit(data)

        self.forecast_model = model

        return self

    # ==========================================
    # EXPORT
    # ==========================================

    def dataframe(self):

        return self.cube.data

    def result(self):

        return self.cube