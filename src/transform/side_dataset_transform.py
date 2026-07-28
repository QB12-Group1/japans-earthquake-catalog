import re
from datetime import datetime

import pandas as pd
from word2number.w2n import word_to_num

from config.settings import BASE_DIR


def clean_invalid_depth_rows(df: pd.DataFrame) -> pd.DataFrame:
    try:
        temp_depth = pd.to_numeric(df["depth"], errors="coerce")
        condition = temp_depth.isna() | (temp_depth > 0)  # pyright: ignore[reportOperatorIssue, reportAttributeAccessIssue]
        return df.loc[condition]
    except Exception as e:
        raise ValueError("Failed to remove reports with invalid depths.") from e


def clean_empty_attr_rows(df: pd.DataFrame, attr: str) -> pd.DataFrame:
    condition = df[attr].notna()
    return df.loc[condition]


def clean_not_coordinated_rows(df: pd.DataFrame) -> pd.DataFrame:
    try:
        temp_latitude = pd.to_numeric(df["latitude"], errors="coerce")
        temp_longitude = pd.to_numeric(df["longitude"], errors="coerce")
        condition = temp_latitude.notna() & temp_longitude.notna()  # pyright: ignore[reportAttributeAccessIssue]
        return df.loc[condition]
    except Exception as e:
        raise ValueError("Failed to remove reports without coordinates.") from e


def clean_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    try:
        indicies = [
            "latitude",
            "longitude",
            "depth",
            "mag",
            "place",
        ]
        return df.drop_duplicates(indicies)
    except TypeError as e:
        raise ValueError("Failed to remove duplicate reports.") from e


def clean_depth_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    depth_min_km, depth_max_km = 10, 750
    temp_depth = pd.to_numeric(df["depth"], errors="coerce")
    condition = (temp_depth >= depth_min_km) & (temp_depth <= depth_max_km)  # pyright: ignore[reportOperatorIssue]
    return df.loc[condition]


def transform_mag(df: pd.DataFrame) -> pd.DataFrame:
    def convert_text_to_num(value: str) -> float:
        try:
            return float(value)
        except ValueError:
            pass

        value = value.lower()
        try:
            return word_to_num(value)
        except ValueError:
            pass

        num_str = value.replace(".", " point ")
        return word_to_num(num_str)

    df["mag"] = df["mag"].apply(convert_text_to_num).apply(lambda num: round(num, 2))
    return df


def transform_units(df: pd.DataFrame) -> pd.DataFrame:
    def convert_to_km(value: str) -> float:
        try:
            return float(value)
        except ValueError:
            pass
        value = value.strip()
        result = re.search(r"(\d+)(\.\d+)?\s?(\w+)?", value)
        if result is None:
            return -1

        num = float(result.group(1) + (result.group(2) or ""))
        unit = result.group(3) or ""

        match unit.lower():
            case "km", "kilometers":
                return num
            case "meters":
                return num / 1000
            case "miles":
                return num * 1.60933999997549
            case _:
                return num

    df["depth"] = df["depth"].apply(convert_to_km).apply(lambda num: round(num, 2))
    return df


def transform_datetime(df: pd.DataFrame) -> pd.DataFrame:
    def normalize_datetime(date_str: str) -> datetime:
        date_str = date_str.strip('"').strip()
        non_iso_formats = [
            "%b %d, %Y, %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%Y-%m-%d %I:%M %p",
            "%Y-%m-%dT%H:%M:%S",
        ]
        try:
            return datetime.strptime(date_str, non_iso_formats[0])
        except ValueError:
            pass

        try:
            return datetime.strptime(date_str, non_iso_formats[1])
        except ValueError:
            pass

        try:
            return datetime.strptime(date_str, non_iso_formats[2])
        except ValueError:
            pass

        try:
            return datetime.strptime(date_str, non_iso_formats[3])
        except ValueError:
            pass

        return datetime.fromisoformat(date_str)

    df["time"] = (
        df["time"]
        .apply(normalize_datetime)
        .apply(lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S"))
    )
    return df


def transform_columns(df: pd.DataFrame) -> pd.DataFrame:
    df["source"] = "DATASET"
    return df.drop(columns=["notes", "status"])


def export_transformed(df: pd.DataFrame) -> None:
    dataset_file_path = BASE_DIR / "data" / "processed" / "side_dataset.csv"
    if not dataset_file_path.is_file():
        dataset_file_path.touch()

    df = transform_datetime(df)
    df = transform_units(df)
    df = transform_mag(df)
    df = transform_columns(df)

    df = clean_duplicates(df)
    df = clean_not_coordinated_rows(df)
    df = clean_invalid_depth_rows(df)
    df = clean_empty_attr_rows(df, "depth")
    df = clean_empty_attr_rows(df, "mag")
    df = clean_depth_anomalies(df)

    df.to_csv(dataset_file_path, encoding="utf-8", index=False)


def load_transformed() -> pd.DataFrame:
    dataset_file_path = BASE_DIR / "data" / "processed" / "side_dataset.csv"
    if not dataset_file_path.is_file():
        raise FileNotFoundError(f"Dataset file not found: '{dataset_file_path}'. ")

    try:
        return pd.read_csv(dataset_file_path)
    except pd.errors.EmptyDataError as e:
        raise ValueError(f"Dataset file is empty: '{dataset_file_path}'") from e
    except pd.errors.ParserError as e:
        raise ValueError(
            f"Dataset file could not be parsed as CSV: '{dataset_file_path}'"
        ) from e
