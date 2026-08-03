from src.database.object import Database


def get_table_report(db: Database) -> dict[str, str | list[tuple[str, str]]]:
    records = db.run_script("report/table_info.sql")
    if not records:
        raise
    info_dict = {
        "column_count": None,
        "total_records": None,
        "columns": [],
    }
    for record in records:
        record = record._asdict()
        if not info_dict["column_count"]:
            info_dict["column_count"] = record["col_count"]
        if not info_dict["total_records"]:
            info_dict["total_records"] = record["total_records"]
        info_dict["columns"].append((record["col_name"], record["col_type"]))
    return info_dict
