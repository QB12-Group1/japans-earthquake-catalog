# Cleans/transforms USGS data

from datetime import datetime

import pandas as pd

from config.settings import BASE_DIR

FILE_PATH = BASE_DIR / "data" / "processed" / "usgs.csv"


def transform_datetime(df: pd.DataFrame) -> pd.DataFrame:
    def normalize_datetime(date_str: str) -> datetime:
        date_str = date_str.strip()
        return datetime.fromisoformat(date_str)

    df["time"] = (
        df["time"]
        .apply(normalize_datetime)
        .apply(lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S"))
    )
    return df


def transform_columns(df: pd.DataFrame) -> pd.DataFrame:
    df["source"] = "USGS"
    return df


def export_transformed(df: pd.DataFrame) -> None:
    if not FILE_PATH.is_file():
        FILE_PATH.touch()

    df = transform_datetime(df)
    df = transform_columns(df)
    df.to_csv(FILE_PATH, index=False)


def load_transformed() -> pd.DataFrame:
    if not FILE_PATH.is_file():
        raise FileNotFoundError(f"Dataset file not found: '{FILE_PATH}'. ")

    try:
        return pd.read_csv(FILE_PATH)
    except pd.errors.EmptyDataError as e:
        raise ValueError(f"Dataset file is empty: '{FILE_PATH}'") from e
    except pd.errors.ParserError as e:
        raise ValueError(
            f"Dataset file could not be parsed as CSV: '{FILE_PATH}'"
        ) from e
