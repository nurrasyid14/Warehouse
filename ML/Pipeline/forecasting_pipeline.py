from __future__ import annotations

from .base_pipeline import BasePipeline
from .pipeline_result import PipelineResult
from ML.OLAP import ForecastFeeder

class ForecastingPipeline(BasePipeline):

    def __init__(
        self,
        engine,
        cube_name,
        model,
        target
    ):

        super().__init__(
            engine,
            cube_name
        )

        self.model = model

        self.target = target

    def run(self):

        self.start_timer()

        cube = self.load_cube()

        feeder = (
            ForecastFeeder(cube)
        )

        series = (
            feeder.arima(
                self.target
            )
        )

        self.model.fit(
            series
        )

        forecast = (
            self.model.forecast()
        )

        duration = (
            self.stop_timer()
        )

        return PipelineResult(

            pipeline_name=
                "forecasting",

            model_name=
                self.model.__class__.__name__,

            parameters=
                self.model.__dict__,

            metrics={},

            predictions=
                forecast,

            duration=
                duration
        )