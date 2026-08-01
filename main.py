import argparse

from config.settings import DATABASE_URL
from src.database.loader import create_table, drop_table, load_to_sql
from src.database.object import Database
from src.database.report import get_table_report
from src.transform.merge import (
    get_emsc_df,
    get_geofon_df,
    get_side_dataset_df,
    get_usgs_df,
)


def print_table_report(report: dict[str, str | list[tuple[str, str]]]) -> None:
    columns_str = "\n".join(
        f"\t{column_name}: {column_type}"
        for column_name, column_type in report["columns"]
    )
    print(f"""columns count: {report["column_count"]}
total_records: {report["total_records"]}
columns:
{columns_str}""")


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

    drop_table()
    create_table()

    sources = [get_emsc_df, get_geofon_df, get_side_dataset_df, get_usgs_df]
    for source in sources:
        df = source(args.fetch)
        load_to_sql(df)

    db = Database(DATABASE_URL)

    # Alter data types for time, latitude, longitude, depth, and mag columns
    with db.transaction():
        report = get_table_report(db)
        print_table_report(report)

        db.run_script("transform/alter_column_types.sql")
        db.run_script("transform/round_float_values.sql")
        db.run_script("transform/clean_incomplete_reports.sql")
        db.run_script("transform/clean_reports_with_error.sql")
        db.run_script("transform/clean_report_anomalies.sql")

        db.run_script("transform/column_month.sql")
        db.run_script("transform/trim_place_str.sql")
        db.run_script("transform/add_region_column.sql")
        db.run_script("transform/remove_column.sql")
        db.run_script("transform/create_indexes.sql")
        db.run_script("transform/categorize_by_mag.sql")
        db.run_script("transform/clean_duplicates.sql")

    db.close()


if __name__ == "__main__":
    main()
