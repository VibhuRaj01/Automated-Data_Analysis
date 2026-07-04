from pathlib import Path
from typing import Union

import pandas as pd

READERS = {
    ".csv": pd.read_csv,
    ".xlsx": pd.read_excel,
    ".xls": pd.read_excel,
    ".parquet": pd.read_parquet,
    ".json": lambda p: pd.read_json(p, orient="records"),
    ".feather": pd.read_feather,
}


def load_dataset(path: Union[str, Path]) -> pd.DataFrame:
    """
    Load a dataset from disk.

    Parameters
    ----------
    path : str | Path
        Path to the dataset.

    Returns
    -------
    pd.DataFrame
    """

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} does not exist.")

    extension = file_path.suffix.lower()

    if extension not in READERS:
        raise ValueError(
            f"Unsupported file format '{extension}'. "
            f"Supported formats: {list(READERS.keys())}"
        )

    try:
        df = READERS[extension](file_path)
    except Exception as e:
        raise RuntimeError(f"Unable to load dataset: {e}") from e

    if df.empty:
        raise ValueError("Dataset is empty.")

    return df
