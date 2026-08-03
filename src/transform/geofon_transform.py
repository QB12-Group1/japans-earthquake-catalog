import re
from datetime import datetime

import pandas as pd


def transform_geofon_data(path: str = "data/raw/genfon.csv") -> pd.DataFrame:
    raw_rows = pd.read_csv(path, encoding="utf-8")
    raw_rows = raw_rows.to_dict("records")

    processed_rows = []

    for row in raw_rows:
        try:
            longitude = float(row["longitude"].replace("°E", "").strip())
            latitude = float(row["latitude"].replace("°N", "").strip())

            depth_match = re.search(r"\d+", row["depth"])

            if depth_match is None:
                raise ValueError("Invalid depth")

            depth = depth_match.group()

            time = datetime.strptime(row["time"], "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            processed_rows.append(
                {
                    "time": time,
                    "latitude": latitude,
                    "longitude": longitude,
                    "depth": depth,
                    "mag": row["mag"],
                    "place": row["place"],
                    "source": "GEOFON",
                }
            )
        except Exception as error:
            print(f"Error processing event : {error}")
            continue
    return pd.DataFrame(processed_rows)


def export_transformed(
    input_path="data/raw/geofon.csv", output_path="data/processed/geofon.csv"
):
    df = transform_geofon_data(input_path)

    df.to_csv(output_path, index=False, encoding="utf-8")


def load_transformed() -> pd.DataFrame:
    file_path = "data/processed/geofon.csv"

    try:
        return pd.read_csv(file_path, encoding="utf-8")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Dataset file not found: '{file_path}'.") from e
    except pd.errors.EmptyDataError as e:
        raise ValueError(f"Dataset file is empty: '{file_path}'") from e
    except pd.errors.ParserError as e:
        raise ValueError(
            f"Dataset file could not be parsed as CSV: '{file_path}'"
        ) from e
