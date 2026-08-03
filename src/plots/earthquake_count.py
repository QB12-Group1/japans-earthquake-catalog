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


def magnitude_distribution_by_source_hist_chart(db: Database) -> None:
    name = "magnitude_distribution_by_source_hist_chart"
    result = db.run_script(f"analysis/plots/{name}.sql")
    if not result:
        return

    magnitudes_by_source: dict[str, list[float]] = {}
    for record in result:  # pyright: ignore
        magnitudes_by_source.setdefault(record.source, []).append(record.magnitude)  # pyright: ignore

    fig, ax = plt.subplots()

    ax.hist(
        magnitudes_by_source.values(),  # pyright: ignore
        bins=15,
        linewidth=0.5,
        edgecolor="white",
        stacked=True,
        label=list(magnitudes_by_source.keys()),
    )

    ax.set(
        title="Distribution of Earthquake Magnitudes by Source",
        xlabel="Magnitude",
        ylabel="Number of Earthquakes",
    )
    ax.legend(title="Source")
    output_dir = BASE_DIR / "outputs"
    plt.savefig(
        output_dir / f"{name}.png",
        dpi=300,
        bbox_inches="tight",
    )


def magnitude_over_time_scatter_chart(db: Database) -> None:
    name = "magnitude_over_time_scatter_chart"
    result = db.run_script(f"analysis/plots/{name}.sql")
    if not result:
        return

    x = [record.time for record in result]  # pyright: ignore
    y = [float(record.magnitude) for record in result]  # pyright: ignore

    fig, ax = plt.subplots()
    fig.autofmt_xdate(rotation=45, ha="right")

    ax.scatter(x, y, alpha=0.5)
    ax.set(
        title="Earthquake Magnitude Over Time",
        xlabel="Time",
        ylabel="Magnitude",
    )

    output_dir = BASE_DIR / "outputs"
    plt.savefig(
        output_dir / f"{name}.png",
        dpi=300,
        bbox_inches="tight",
    )


def magnitude_depth_boxplot(db: Database) -> None:
    name = "magnitude_depth_boxplot"
    result = db.run_script(f"analysis/plots/{name}.sql")
    if not result:
        return

    shallow: list[float] = []
    intermediate: list[float] = []
    deep: list[float] = []

    for record in result:  # pyright: ignore
        magnitude = float(record.magnitude)  # pyright: ignore

        if record.depth_group == "Shallow":  # pyright: ignore
            shallow.append(magnitude)
        elif record.depth_group == "Intermediate":  # pyright: ignore
            intermediate.append(magnitude)
        else:
            deep.append(magnitude)

    fig, ax = plt.subplots()

    ax.boxplot(
        [shallow, intermediate, deep],
        tick_labels=["Shallow", "Intermediate", "Deep"],
    )
    ax.set(
        title="Magnitude Distribution by Depth Group",
        xlabel="Depth Group",
        ylabel="Magnitude",
    )

    output_dir = BASE_DIR / "outputs"
    plt.savefig(
        output_dir / f"{name}.png",
        dpi=300,
        bbox_inches="tight",
    )
