import re
import pandas as pd 
from datetime import datetime

def transform_genfon_data() -> pd.DataFrame:
    raw_rows = pd.read_csv("data/raw/geofon.csv")
    raw_rows = raw_rows.to_dict("records")

    processed_rows = []

    for row in raw_rows:
        try:
            longitude = float(row["longitude"].replace("°E", "").strip())
            latitude = float(row["latitude"].replace("°N", "").strip())

            depth = re.search(r"\d+", row["depth"]).group()
            
            time = datetime.strptime(row["time"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")

            processed_rows.append({
                "time": time ,
                "latitude": latitude,
                "longitude": longitude,
                "depth": depth,
                "mag": row["mag"],
                "place": row["place"],
                "source": "GEOFON",
            })
        except Exception as error:
            print(f"Error processing event : {error}")
            continue
    return pd.DataFrame(processed_rows)

def export_transformed(df: pd.DataFrame) -> None:
    file_path = "data/processed/geofon.csv"

    df.to_csv(file_path, index=False ,encoding="utf-8")


def load_transformed() -> pd.DataFrame:
    file_path = "data/processed/geofon.csv"

    try:
        return pd.read_csv(file_path , encoding="utf-8")
    except FileNotFoundError as e:
            raise FileNotFoundError(f"Dataset file not found: '{file_path}'.") from e
    except pd.errors.EmptyDataError as e:
        raise ValueError(f"Dataset file is empty: '{file_path}'") from e
    except pd.errors.ParserError as e:
        raise ValueError(
            f"Dataset file could not be parsed as CSV: '{file_path}'"
        ) from e