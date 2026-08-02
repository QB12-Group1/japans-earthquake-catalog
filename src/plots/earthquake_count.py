import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from config.settings import BASE_DIR
from src.database.object import Database


def earthquake_count_by_date_bar_chart(db: Database) -> None:
    name = "earthquake_count_by_date_bar_chart"
    result = db.run_script(f"analysis/plots/{name}.sql")
    if not result:
        return

    x = [record.time for record in result]  # pyright: ignore[reportAttributeAccessIssue]
    y = [float(record.earthquake_count) for record in result]  # pyright: ignore[reportAttributeAccessIssue]

    fig, ax = plt.subplots()

    ax.bar(x, y)
    fig.autofmt_xdate(rotation=45, ha="right")
    ax.set(
        title="Earthquake Count by Date",
        xlabel="Date",
        ylabel="Number of Earthquakes",
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

    ax.grid(True, axis="y")
    fig.tight_layout()

    output_dir = BASE_DIR / "outputs"
    plt.savefig(
        output_dir / f"{name}.png",
        dpi=300,
        bbox_inches="tight",
    )


def earthquake_count_by_dow_line_chart(db: Database) -> None:
    name = "earthquake_count_by_dow_line_chart"
    result = db.run_script(f"analysis/plots/{name}.sql")
    if not result:
        return

    x = [record.dow for record in result]  # pyright: ignore[reportAttributeAccessIssue]
    y = [float(record.earthquake_count) for record in result]  # pyright: ignore[reportAttributeAccessIssue]

    fig, ax = plt.subplots()

    ax.plot(x, y, marker="o")
    ax.set(
        title="Earthquake Count by Day of the Week",
        xlabel="Day of the Week",
        ylabel="Number of Earthquakes",
    )
    ax.grid(True)

    output_dir = BASE_DIR / "outputs"
    plt.savefig(
        output_dir / f"{name}.png",
        dpi=300,
        bbox_inches="tight",
    )


def earthquake_count_by_hour_line_chart(db: Database) -> None:
    name = "earthquake_count_by_hour_line_chart"
    result = db.run_script(f"analysis/plots/{name}.sql")
    if not result:
        return

    x = [record.hour for record in result]  # pyright: ignore[reportAttributeAccessIssue]
    y = [float(record.earthquake_count) for record in result]  # pyright: ignore[reportAttributeAccessIssue]

    fig, ax = plt.subplots()

    ax.plot(x, y, marker="o")
    ax.set(
        title="Earthquake Count by Hour of the Day",
        xlabel="Hour of the day",
        ylabel="Number of Earthquakes",
    )
    ax.grid(True)

    output_dir = BASE_DIR / "outputs"
    plt.savefig(
        output_dir / f"{name}.png",
        dpi=300,
        bbox_inches="tight",
    )
