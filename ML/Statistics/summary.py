from __future__ import annotations


def summarize_best(
    df,
    metric
):

    best = (
        df.sort_values(
            metric,
            ascending=False
        )
        .iloc[0]
    )

    return (
        f"Best cube: "
        f"{best['cube_name']} | "
        f"Model: {best['model_name']} | "
        f"{metric}: {best[metric]:.4f}"
    )