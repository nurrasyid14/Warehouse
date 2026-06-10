from __future__ import annotations

from scipy.stats import pearsonr
from scipy.stats import spearmanr


def pearson(
    x,
    y
):

    return pearsonr(
        x,
        y
    )


def spearman(
    x,
    y
):

    return spearmanr(
        x,
        y
    )