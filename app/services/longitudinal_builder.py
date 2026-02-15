import pandas as pd


def build_longitudinal_dataset(metrics):

    df = pd.DataFrame(metrics)

    # Keep only key columns
    df = df[[
        "metric_key",
        "year",
        "value",
        "unit",
        "source_type",
        "confidence_score"
    ]]

    # Aggregate per metric per year (if multiple)
    df = df.groupby(
        ["metric_key", "year", "unit"],
        as_index=False
    ).agg({
        "value": "sum",
        "confidence_score": "mean"
    })

    return df
