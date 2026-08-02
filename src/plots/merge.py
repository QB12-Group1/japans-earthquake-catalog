from src.database.object import Database
from src.plots.earthquake_count import (
    earthquake_count_by_date_bar_chart,
    earthquake_count_by_dow_line_chart,
    earthquake_count_by_hour_line_chart,
    magnitude_distribution_by_source_hist_chart,
)


def plot_and_save(db: Database) -> None:
    earthquake_count_by_date_bar_chart(db)
    earthquake_count_by_hour_line_chart(db)
    earthquake_count_by_dow_line_chart(db)
    magnitude_distribution_by_source_hist_chart(db)
