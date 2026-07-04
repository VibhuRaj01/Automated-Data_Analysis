from typing import Any
import pandas as pd


def profile_dataset(df: pd.DataFrame) -> dict[str, Any]:
    """
    Create a compact dataset profile for downstream LLM agents.
    """

    profile: dict[str, Any] = {
        "profile_version": "1.0",
        "dataset": {
            "rows": len(df),
            "columns": len(df.columns),
            "duplicates": int(df.duplicated().sum()),
            "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
        },
        "columns": [],
    }

    for column in df.columns:

        series = df[column]

        info = {
            "name": column,
            "dtype": str(series.dtype),
            "missing": int(series.isna().sum()),
            "unique": int(series.nunique(dropna=True)),
        }

        if pd.api.types.is_numeric_dtype(series):

            info["semantic_type"] = "numeric"

            info["statistics"] = {
                "mean": (float(series.mean()) if not series.dropna().empty else None),
                "median": (
                    float(series.median()) if not series.dropna().empty else None
                ),
                "std": (float(series.std()) if not series.dropna().empty else None),
                "min": (float(series.min()) if not series.dropna().empty else None),
                "max": (float(series.max()) if not series.dropna().empty else None),
            }

        elif pd.api.types.is_datetime64_any_dtype(series):

            info["semantic_type"] = "datetime"

            info["statistics"] = {
                "min": str(series.min()),
                "max": str(series.max()),
            }

        else:

            info["semantic_type"] = "categorical"

            top_values = series.value_counts(dropna=True).head(5).to_dict()

            info["statistics"] = {"top_values": top_values}

        info["sample_values"] = series.dropna().head(5).tolist()

        profile["columns"].append(info)

    return profile
