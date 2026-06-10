from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class BaseBenchmark(ABC):

    @abstractmethod
    def run(self):
        ...

    @abstractmethod
    def evaluate(self):
        ...

    @abstractmethod
    def to_dataframe(self):
        ...