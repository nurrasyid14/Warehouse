from __future__ import annotations

from .experiment import (
    Experiment
)


class ExperimentPipeline:

    def __init__(
        self,
        name,
        cube_name
    ):

        self.experiment = (
            Experiment(
                name,
                cube_name
            )
        )

    def run(
        self,
        pipelines
    ):

        for pipeline in pipelines:

            result = (
                pipeline.run()
            )

            self.experiment.add_result(
                result
            )

        return self.experiment