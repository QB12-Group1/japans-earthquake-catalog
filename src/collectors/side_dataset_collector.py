import pandas as pd

from config.settings import BASE_DIR


def load_raw() -> pd.DataFrame:
    dataset_file_path = BASE_DIR / "data" / "raw" / "side_dataset.csv"
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
