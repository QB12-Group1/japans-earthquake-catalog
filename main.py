import argparse

from config.settings import DATABASE_URL
from src.database.loader import drop_table, load_to_sql
from src.database.object import Database
from src.transform.merge import (
    get_emsc_df,
    get_geofon_df,
    get_side_dataset_df,
    get_usgs_df,
)


def main():
    arg_parser = argparse.ArgumentParser(
        description="Collect data for the last 30 days and run analysis.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    arg_parser.add_argument(
        "--fetch",
        type=bool,
        required=True,
        action=argparse.BooleanOptionalAction,
        help=(
            "Fetch fresh data and rebuild plots, replacing existing data and graphs."
            "Use --no-fetch to reuse existing local data."
        ),
    )
    args = arg_parser.parse_args()
    if args.fetch:
        drop_table()

    df_loaders = [get_usgs_df, get_side_dataset_df, get_geofon_df, get_emsc_df]
    for df_loader in df_loaders:
        df = df_loader(args.fetch)
        load_to_sql(df)

    db = Database(DATABASE_URL)  # noqa: F841


if __name__ == "__main__":
    main()
