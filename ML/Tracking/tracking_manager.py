from __future__ import annotations

from datetime import datetime

from .experiment import (
    ExperimentRecord
)

from .registry import (
    ExperimentRegistry
)

from .leaderboard import (
    Leaderboard
)

from .history import (
    ExperimentHistory
)


class TrackingManager:

    def __init__(self):

        self.registry = (
            ExperimentRegistry()
        )

        self.history = (
            ExperimentHistory(
                self.registry
            )
        )

        self.leaderboard = (
            Leaderboard(
                self.registry
            )
        )

    def log_result(
        self,
        result,
        cube_name,
        experiment_name
    ):

        record = (
            ExperimentRecord(

                experiment_name=
                    experiment_name,

                pipeline_name=
                    result.pipeline_name,

                model_name=
                    result.model_name,

                cube_name=
                    cube_name,

                timestamp=
                    datetime.now(),

                parameters=
                    result.parameters,

                metrics=
                    result.metrics,

                duration=
                    result.duration
            )
        )

        self.registry.add(
            record
        )

        return record