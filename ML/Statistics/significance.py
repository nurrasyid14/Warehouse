from __future__ import annotations

from scipy.stats import ttest_rel, wilcoxon, f_oneway

def paired_ttest(x, y):
    """Paired t-test between x and y."""
    return ttest_rel(x, y)

def wilcoxon_test(x, y):
    """Wilcoxon signed-rank test between x and y."""
    return wilcoxon(x, y)

def anova(*args):
    """One-way ANOVA test on multiple groups."""
    return f_oneway(*args)