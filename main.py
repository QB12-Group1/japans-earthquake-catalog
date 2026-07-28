from src.collectors.side_dataset_collector import load_raw
from src.transform.side_dataset_transform import export_transformed


def main():
    df = load_raw()
    export_transformed(df)
    print("Hello from japans-earthquake-catalog!")


if __name__ == "__main__":
    main()
