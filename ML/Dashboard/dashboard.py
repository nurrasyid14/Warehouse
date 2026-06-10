from __future__ import annotations

from typing import Dict
from typing import Any


class Dashboard:

    """
    Dashboard container.

    Holds:
    - benchmark outputs
    - statistics outputs
    - plotly figures
    """

    def __init__(self):

        self.pages: Dict[
            str,
            Any
        ] = {}

    def add_page(
        self,
        name: str,
        figure
    ):

        self.pages[name] = figure

    def get_page(
        self,
        name: str
    ):

        return self.pages.get(name)

    def list_pages(self):

        return list(
            self.pages.keys()
        )

    def clear(self):

        self.pages.clear()

    def __len__(self):

        return len(
            self.pages
        )

    def __repr__(self):

        return (
            f"Dashboard("
            f"pages={len(self.pages)}"
            f")"
        )