import argparse

from config.settings import DATABASE_URL
from src.database.loader import load_to_sql
from src.database.object import Database
from src.transform.merge import get_merged_sources_df


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

    merged_df = get_merged_sources_df(args.fetch)
    load_to_sql(merged_df)

    db = Database(DATABASE_URL)

    # Alter data types for time, latitude, longitude, depth, and mag columns
    with db.transaction():
        db.run_script("transform/alter_column_types.sql")

        db.run_script("transform/column_month.sql")
        db.run_script("transform/remove_column.sql")


if __name__ == "__main__":
    main()
