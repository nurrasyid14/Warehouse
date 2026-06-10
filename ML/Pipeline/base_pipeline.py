from __future__ import annotations

import time

from ML.OLAP import (
    CubeReader,
    FeatureBuilder
)

from .pipeline_result import (
    PipelineResult
)


class BasePipeline:
    def __init__(self,engine,cube_name: str):
        self.engine = engine
        self.cube_name = cube_name
        self.reader = CubeReader(engine)

    # =====================================
    # LOAD
    # =====================================

    def load_cube(self):
        return self.reader.load(
            self.cube_name
        )

    # =====================================
    # FEATURES
    # =====================================

    def build_features(self,cube):
        return (
            FeatureBuilder(cube)
            .fillna()
            .build()
        )

    # =====================================
    # TIMER
    # =====================================

    def start_timer(self):
        self._start = time.time()

    def stop_timer(self):
        return (
            time.time()
            - self._start
        )

    # =====================================
    # RESULT
    # =====================================

    def make_result(self,**kwargs):
        return PipelineResult(
            **kwargs
        )