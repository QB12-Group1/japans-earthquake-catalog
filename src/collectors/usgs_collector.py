from datetime import datetime, timedelta

import pandas as pd
import requests

from config.settings import BASE_DIR

FILE_PATH = BASE_DIR / "data" / "raw" / "usgs.csv"


def export_raw() -> None:
    if not FILE_PATH.is_file():
        FILE_PATH.touch()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    params = {
        "format": "csv",
        "starttime": start_date,
        "endtime": end_date,
        "minlatitude": 24,
        "maxlatitude": 46,
        "minlongitude": 123,
        "maxlongitude": 146,
        "minmagnitude": 1,
    }
    response = requests.get(
        "https://earthquake.usgs.gov/fdsnws/event/1/query", params=params
    )

    try:
        with open(FILE_PATH, mode="w", encoding="utf-8") as file:
            file.write(response.text)
    except OSError as e:
        raise ValueError(f"Could not open: '{FILE_PATH}'") from e


def load_raw() -> pd.DataFrame:
    if not FILE_PATH.is_file():
        raise FileNotFoundError(f"Dataset file not found: '{FILE_PATH}'. ")

    try:
        return pd.read_csv(FILE_PATH, encoding="utf-8")
    except pd.errors.EmptyDataError as e:
        raise ValueError(f"Dataset file is empty: '{FILE_PATH}'") from e
    except pd.errors.ParserError as e:
        raise ValueError(
            f"Dataset file could not be parsed as CSV: '{FILE_PATH}'"
        ) from e
