from __future__ import annotations
import pandas as pd

from .base_pipeline import BasePipeline
from .pipeline_result import PipelineResult
from ML.Clustering.evals import evaluate_clustering


class ClusteringPipeline(
    BasePipeline
):

    def __init__(
        self,
        engine,
        cube_name,
        model,
        features
    ):

        super().__init__(
            engine,
            cube_name
        )

        self.model = model

        self.features = features

    def run(self):

        self.start_timer()

        cube = self.load_cube()

        X = (
            cube.data[
                self.features
            ]
            .copy()
        )

        self.model.fit(X)

        labels = (
            self.model.labels_
        )

        metrics = (
            evaluate_clustering(
                X,
                labels
            )
        )

        duration = (
            self.stop_timer()
        )

        return PipelineResult(

            pipeline_name=
                "clustering",

            model_name=
                self.model.__class__.__name__,

            parameters=
                self.model.__dict__,

            metrics=
                metrics,

            labels=
                labels,

            duration=
                duration
        )