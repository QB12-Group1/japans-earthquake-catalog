from collections import namedtuple
from datetime import datetime
from unittest import TestCase

from config.settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
from src.database.models import Earthquake, EarthquakeCategory, EarthquakeSource
from src.database.object import Database


class TestDataBaseTransform(TestCase):
    def setUp(self) -> None:
        url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test"
        self.db = Database(url)
        EarthquakeTuple = namedtuple(
            "Earthquake",
            [
                "time",
                "latitude",
                "longitude",
                "depth",
                "mag",
                "magType",
                "nst",
                "gap",
                "dmin",
                "rms",
                "net",
                "eid",
                "updated",
                "place",
                "type",
                "horizontalError",
                "depthError",
                "magError",
                "magNst",
                "status",
                "locationSource",
                "magSource",
                "source",
                "notes",
            ],
            defaults=None,
        )
        self.earthquakes = [
            EarthquakeTuple(
                time=datetime(2026, 7, 3, 14, 37, 27),
                latitude=40.4,
                longitude=142.0,
                depth=55.1,
                mag=4.1,
                place="31 km NE of Kuji, Japan",
                source="USGS",
            ),
            EarthquakeTuple(
                time=datetime(2025, 9, 17, 14, 10, 5),
                latitude=43.1,
                longitude=141.4,
                depth=10.2,
                mag=4.8,
                place="Hokkaido, Japan region",
                source="DATASET",
            ),
            EarthquakeTuple(
                time=datetime(2026, 8, 1, 2, 48),
                latitude=41.3,
                longitude=141.9,
                depth=72.0,
                mag=5.5,
                place="HOKKAIDO, JAPAN REGION",
                source="EMSC",
            ),
            EarthquakeTuple(
                time=datetime(2026, 7, 19, 1, 40, 5),
                latitude=38.7,
                longitude=133.5,
                depth=450.0,
                mag=4.3,
                place="Sea of Japan",
                source="GEOFON",
            ),
        ]
        with self.db.transaction():
            self.db.run_script("schema.sql")
            for earthquake in self.earthquakes:
                self.db.run(
                    "INSERT INTO earthquakes (time, latitude, longitude, depth, mag, place, source) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        earthquake.time,
                        earthquake.latitude,
                        earthquake.longitude,
                        earthquake.depth,
                        earthquake.mag,
                        earthquake.place,
                        earthquake.source,
                    ),
                )

    def tearDown(self) -> None:
        with self.db.transaction():
            self.db.run("DROP TABLE IF EXISTS earthquakes")
        self.db.close()


class TestDataBaseQueries(TestCase):
    def setUp(self) -> None:
        self.earthquakes = [
            Earthquake(
                id=1,
                time=datetime(2026, 7, 18, 21, 54, 57),
                latitude=43.4,
                longitude=132.5,
                depth=497.0,
                mag=4.2,
                place="Primor'ye, Russia",
                source=EarthquakeSource.GEOFON,
                month=7,
                region="Pr imor'Ye",
                category=EarthquakeCategory.MODERATE,
            ),
            Earthquake(
                id=2,
                time=datetime(2026, 7, 28, 10, 9, 38),
                latitude=32.4,
                longitude=130.7,
                depth=10.0,
                mag=4.4,
                place="10 km SE of Honmachi, Japan",
                source=EarthquakeSource.USGS,
                month=7,
                region="Honmachi",
                category=EarthquakeCategory.MODERATE,
            ),
            Earthquake(
                id=3,
                time=datetime(2026, 7, 28, 9, 37, 30),
                latitude=32.6,
                longitude=130.6,
                depth=10.0,
                mag=3.1,
                place="KYUSHU, JAPAN",
                source=EarthquakeSource.EMSC,
                month=7,
                region="Kyushu",
                category=EarthquakeCategory.WEAK,
            ),
            Earthquake(
                id=4,
                time=datetime(2026, 7, 28, 7, 27, 14),
                latitude=32.7,
                longitude=130.7,
                depth=10.0,
                mag=6.8,
                place="KYUSHU, JAPAN",
                source=EarthquakeSource.GEOFON,
                month=7,
                region="Kyushu",
                category=EarthquakeCategory.STRONG,
            ),
            Earthquake(
                id=5,
                time=datetime(2025, 10, 2, 13, 1, 2),
                latitude=32.8,
                longitude=129.9,
                depth=25.3,
                mag=4.9,
                place="Nagasaki",
                source=EarthquakeSource.DATASET,
                month=10,
                region="Nagasaki",
                category=EarthquakeCategory.MODERATE,
            ),
        ]
        url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test"
        self.db = Database(url)
        with self.db.transaction():
            self.db.run("""CREATE TABLE IF NOT EXISTS earthquakes (
            id SERIAL PRIMARY KEY,
            time TIMESTAMP,
            latitude FLOAT,
            longitude FLOAT,
            depth FLOAT,
            mag FLOAT,
            place TEXT,
            source TEXT,
            month INTEGER,
            region TEXT,
            category TEXT
            )""")
            for earthquake in self.earthquakes:
                self.db.run(
                    "INSERT INTO earthquakes (time, latitude, longitude, depth, mag, place, source, month, region, category) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        earthquake.time,
                        earthquake.latitude,
                        earthquake.longitude,
                        earthquake.depth,
                        earthquake.mag,
                        earthquake.place,
                        earthquake.source,
                        earthquake.month,
                        earthquake.region,
                        earthquake.category,
                    ),
                )

    def test_row_count(self) -> None:
        self.db.run("SELECT * FROM earthquakes")
        row_count = self.db._cursor.rowcount
        self.assertEqual(row_count, 5)

    def test_table_report(self) -> None:
        Record = namedtuple(
            "Record", ["col_count", "col_name", "col_type", "total_records"]
        )
        col_count, total_records = 11, 5
        expected = [
            Record(col_count, "id", "integer", total_records),
            Record(col_count, "time", "timestamp without time zone", total_records),
            Record(col_count, "latitude", "double precision", total_records),
            Record(col_count, "longitude", "double precision", total_records),
            Record(col_count, "depth", "double precision", total_records),
            Record(col_count, "mag", "double precision", total_records),
            Record(col_count, "place", "text", total_records),
            Record(col_count, "source", "text", total_records),
            Record(col_count, "month", "integer", total_records),
            Record(col_count, "region", "text", total_records),
            Record(col_count, "category", "text", total_records),
        ]
        result = self.db.run_script("report/table_info.sql")
        self.assertSetEqual(set(expected), set(result))

    def test_source_counts(self) -> None:
        Record = namedtuple("Record", ["source", "count"])
        expected = [
            Record("GEOFON", 2),
            Record("DATASET", 1),
            Record("EMSC", 1),
            Record("USGS", 1),
        ]
        result = self.db.run_script("analysis/source_counts.sql")
        self.assertSetEqual(set(expected), set(result))  # pyright: ignore[reportArgumentType]

    def test_dangerous_quakes(self) -> None:
        expected = [self.earthquakes[3].to_record_namedtuple()]
        result = self.db.run_script("analysis/dangerous_quakes.sql")
        self.assertCountEqual(expected, result)
        self.assertSequenceEqual(expected, result)

    def test_recent_top10_destructive_quakes(self) -> None:
        expected = sorted(self.earthquakes, key=lambda v: v.mag, reverse=True)
        result = self.db.run_script("analysis/recent_top10_destructive_quakes.sql")
        self.assertSequenceEqual(
            result, [earthquake.to_record_namedtuple() for earthquake in expected]
        )

    def test_regional_report(self) -> None:
        Record = namedtuple(
            "Record",
            [
                "region",
                "earthquake_count",
                "avg_depth",
                "avg_magnitude",
                "max_magnitude",
                "deepest_depth",
                "shallowest_depth",
            ],
        )
        expected = [
            Record(
                "Pr imor'Ye",
                1,
                497.00,
                4.20,
                4.20,
                497.00,
                497.00,
            ),
            Record(
                "Honmachi",
                1,
                10.00,
                4.40,
                4.40,
                10.00,
                10.00,
            ),
            Record(
                "Kyushu",
                2,
                10.00,
                4.95,
                6.80,
                10.00,
                10.00,
            ),
            Record(
                "Nagasaki",
                1,
                25.30,
                4.90,
                4.90,
                25.30,
                25.30,
            ),
        ]
        result = self.db.run_script("analysis/regional_quake_report.sql")
        self.assertSetEqual(set(expected), set(result))

    def tearDown(self) -> None:
        with self.db.transaction():
            self.db.run("DROP TABLE IF EXISTS earthquakes")
        self.db.close()
