import re
import unittest
from collections import namedtuple
from datetime import datetime
from unittest import TestCase

from psycopg2.errors import UndefinedColumn

from config.settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
from src.database.models import Earthquake, EarthquakeCategory, EarthquakeSource
from src.database.object import Database


class TestDataBaseTransform(TestCase):
    def setUp(self) -> None:
        url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test"
        self.db = Database(url)
        fields = [
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
        ]
        EarthquakeTuple = namedtuple(
            "Earthquake",
            fields,
            defaults=[None for _ in range(len(fields))],
        )
        self.all_earthquakes = [
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
            EarthquakeTuple(  # duplicate of the above record
                time=datetime(2025, 9, 17, 14, 10, 8),
                latitude=43.1,
                longitude=141.7,
                depth=10.2,
                mag=4.8,
                place="Hokkaido, Japan region",
                source="EMSC",
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
            EarthquakeTuple(  # duplicate of the above record
                time=datetime(2026, 7, 19, 1, 40, 5),
                latitude=39.7,
                longitude=133.5,
                depth=450.0,
                mag=4.3,
                place="Sea of Japan",
                source="DATASET",
            ),
            EarthquakeTuple(  # data anomaly
                time=datetime(2025, 10, 9, 9, 5, 0),
                latitude=35.6,
                longitude=139.6,
                depth=2000.0,
                mag=5.8,
                place="Tokyo, Japan",
                source="DATASET",
            ),
        ]
        self.earthquakes = [self.all_earthquakes[i] for i in [0, 1, 3, 4, 5]]
        with self.db.transaction():
            self.db.run_script("schema.sql")
            for earthquake in self.all_earthquakes:
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

            self.db.run_script("transform/alter_column_types.sql")
            self.db.run_script("transform/round_float_values.sql")
            self.db.run_script("transform/clean_incomplete_reports.sql")
            self.db.run_script("transform/clean_reports_with_error.sql")
            self.db.run_script("transform/clean_report_anomalies.sql")

            self.db.run_script("transform/column_month.sql")
            self.db.run_script("transform/trim_place_str.sql")
            self.db.run_script("transform/add_region_column.sql")
            self.db.run_script("transform/remove_column.sql")
            self.db.run_script("transform/create_indexes.sql")
            self.db.run_script("transform/categorize_by_mag.sql")
            self.db.run_script("transform/clean_duplicates.sql")

    def test_column_month_transform(self) -> None:
        Record = namedtuple("Record", ["month"])
        expected = [
            Record(month=earthquake.time.month) for earthquake in self.earthquakes
        ]
        result = self.db.all("SELECT month FROM earthquakes")
        self.assertSetEqual(set(expected), set(result))

    def test_remove_column(self) -> None:
        with self.assertRaises(UndefinedColumn), self.db.transaction():
            self.db.one("SELECT locationSource FROM earthquakes")

    def test_create_indexes(self) -> None:
        Record = namedtuple("Record", ["indexname"])
        expected = [
            Record("earthquakes_pkey"),
            Record("index_mag"),
            Record("index_region"),
            Record("index_time"),
        ]
        with self.db.transaction():
            result = self.db.all(
                """SELECT indexname FROM pg_indexes WHERE tablename = 'earthquakes' ORDER BY indexname"""
            )
            self.assertSetEqual(set(expected), set(result))

    def test_trim_place_str(self) -> None:
        result = self.db.all("SELECT place FROM earthquakes")
        for record in result:
            place = record._asdict()["place"]
            self.assertFalse(place != place.strip())

    def test_clean_duplicates(self) -> None:
        result = self.db.all("SELECT * FROM earthquakes")
        self.assertNotEqual(len(result), len(self.all_earthquakes))

    def test_add_region_column(self) -> None:
        Record = namedtuple("Record", ["region"])
        expected = []
        for earthquake in self.earthquakes:
            region = earthquake.place.lower()
            region = re.sub(",.+", "", region)
            region = re.sub(".+,", "", region)
            region = re.sub(".+of ", "", region)
            region = region.title()
            record = Record(region)
            expected.append(record)
        result = self.db.all("SELECT region FROM earthquakes")
        self.assertSetEqual(set(expected), set(result))

    def test_categorize_by_mag(self) -> None:
        Record = namedtuple("Record", ["category"])
        expected = []
        for earthquake in self.earthquakes:
            category = None
            mag = earthquake.mag
            if mag < 4:
                category = EarthquakeCategory.WEAK
            elif mag >= 4 and mag <= 6:
                category = EarthquakeCategory.MODERATE
            else:
                category = EarthquakeCategory.STRONG

            record = Record(category)
            expected.append(record)
        result = self.db.all("SELECT category FROM earthquakes")
        self.assertSetEqual(set(expected), set(result))

    def test_alter_column_types(self) -> None:
        Record = namedtuple(
            "Record", ["lat_type", "long_type", "mag_type", "depth_type", "time_type"]
        )
        expected = Record(
            "double precision",
            "double precision",
            "double precision",
            "double precision",
            "timestamp without time zone",
        )
        result = self.db.one("""SELECT pg_typeof(latitude)  AS lat_type,
       pg_typeof(longitude) AS long_type,
       pg_typeof(mag)       AS mag_type,
       pg_typeof(depth)     AS depth_type,
       pg_typeof(time)      AS time_type
FROM earthquakes
LIMIT 1""")
        self.assertEqual(expected, result)

    def test_round_float_values(self) -> None:
        expected = self.earthquakes[0]._asdict()
        expected = {
            "latitude": str(expected["latitude"]),
            "longitude": str(expected["longitude"]),
            "depth": str(expected["depth"]),
            "mag": str(expected["mag"]),
        }
        result = self.db.one("""SELECT latitude,
       longitude,
       mag,
       depth
FROM earthquakes
ORDER BY id
LIMIT 1""")
        if not result:
            self.fail("Table is empty.")
        result = result._asdict()
        for k, v in result.items():
            v = round(v, 1)
            result[k] = str(v)
        self.assertDictEqual(expected, result)

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
        self.assertEqual(row_count, len(self.earthquakes))

    def test_table_report(self) -> None:
        Record = namedtuple(
            "Record", ["col_count", "col_name", "col_type", "total_records"]
        )
        col_count, total_records = 11, len(self.earthquakes)
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

        record_map = {}
        for earthquake in self.earthquakes:
            source = earthquake.source
            if not record_map.get(source):
                record_map[source] = {
                    "source": source,
                    "count": 0,
                }

            record_map[source]["count"] += 1

        expected = [Record(**record) for _, record in record_map.items()]
        result = self.db.run_script("analysis/source_counts.sql")
        self.assertSetEqual(set(expected), set(result))

    def test_dangerous_quakes(self) -> None:
        expected = []
        for earthquake in self.earthquakes:
            if earthquake.mag > 6 and earthquake.depth < 50:
                expected.append(earthquake.to_record_namedtuple())
        result = self.db.run_script("analysis/dangerous_quakes.sql")
        self.assertCountEqual(expected, result)
        self.assertSequenceEqual(expected, result)

    def test_recent_top10_destructive_quakes(self) -> None:
        expected = sorted(self.earthquakes, key=lambda v: v.mag, reverse=True)[:10]
        result = self.db.run_script("analysis/recent_top10_destructive_quakes.sql")
        self.assertSequenceEqual(
            result, [earthquake.to_record_namedtuple() for earthquake in expected]
        )

    def test_average_magnitude(self) -> None:
        Record = namedtuple("Record", ["source", "region", "Average"])

        record_map = {}
        for earthquake in self.earthquakes:
            key = earthquake.source, earthquake.region
            if not record_map.get(key):
                record_map[key] = {
                    "count": 0,
                    "source": earthquake.source.name,
                    "region": earthquake.region,
                    "Average": 0,
                }

            record_map[key]["count"] += 1
            record_map[key]["Average"] = (
                record_map[key]["Average"] + earthquake.mag
            ) / record_map[key]["count"]

        expected = [
            Record(
                source=record["source"],
                region=record["region"],
                Average=record["Average"],
            )
            for _, record in record_map.items()
        ]
        result = self.db.run_script("analysis/avg_magnitude.sql")
        self.assertSetEqual(set(result), set(expected))

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

        record_map = {}
        for earthquake in self.earthquakes:
            region = earthquake.region
            if not record_map.get(region):
                record_map[region] = {
                    "region": region,
                    "earthquake_count": 0,
                    "avg_depth": 0,
                    "avg_magnitude": 0,
                    "max_magnitude": 0,
                    "deepest_depth": 0,
                }

            if not record_map[region].get("shallowest_depth"):
                record_map[region]["shallowest_depth"] = earthquake.depth

            record_map[region]["earthquake_count"] += 1
            count = record_map[region]["earthquake_count"]

            record_map[region]["avg_depth"] = (
                record_map[region]["avg_depth"] + earthquake.depth
            ) / count
            record_map[region]["avg_magnitude"] = (
                record_map[region]["avg_magnitude"] + earthquake.mag
            ) / count

            if earthquake.mag > record_map[region]["max_magnitude"]:
                record_map[region]["max_magnitude"] = earthquake.mag

            if earthquake.depth > record_map[region]["deepest_depth"]:
                record_map[region]["deepest_depth"] = earthquake.depth

            if earthquake.depth < record_map[region]["shallowest_depth"]:
                record_map[region]["shallowest_depth"] = earthquake.depth

        expected = [Record(**record) for _, record in record_map.items()]
        result = self.db.run_script("analysis/regional_quake_report.sql")
        self.assertSetEqual(set(expected), set(result))

    def test_montly_stats(self) -> None:
        Record = namedtuple("Record", ["month", "count"])

        record_map = {}
        for earthquake in self.earthquakes:
            month = earthquake.month
            if not record_map.get(month):
                record_map[month] = {"month": month, "count": 0}

            record_map[month]["count"] += 1

        expected = [Record(**record) for _, record in record_map.items()]
        result = self.db.run_script("analysis/monthly_stats.sql")
        self.assertSequenceEqual(expected, sorted(result, key=lambda r: r.month))

    def test_grouped_analysis(self) -> None:
        Record = namedtuple(
            "Record", ["month", "region", "category", "count", "avg_mag", "avg_depth"]
        )

        record_map = {}
        for earthquake in self.earthquakes:
            key = earthquake.source, earthquake.region
            if not record_map.get(key):
                record_map[key] = {
                    "month": earthquake.month,
                    "region": earthquake.region,
                    "category": str(earthquake.category),
                    "count": 0,
                    "avg_mag": 0,
                    "avg_depth": 0,
                }

            record_map[key]["count"] += 1
            count = record_map[key]["count"]

            record_map[key]["avg_depth"] = (
                record_map[key]["avg_depth"] + earthquake.depth
            ) / count
            record_map[key]["avg_mag"] = (
                record_map[key]["avg_mag"] + earthquake.mag
            ) / count

        expected = [Record(**record) for _, record in record_map.items()]
        result = self.db.run_script("analysis/grouped_analysis.sql")
        self.assertSetEqual(set(result), set(expected))

    def test_clean_report_anomalies(self) -> None:
        for record in self.db.all("SELECT depth FROM earthquakes"):
            depth = record._asdict()["depth"]
            self.assertFalse(depth <= 1 or depth >= 750)

    def test_clean_incomplete_reports(self) -> None:
        for record in self.db.all(
            "SELECT latitude, longitude, depth, mag FROM earthquakes"
        ):
            record = record._asdict()
            self.assertFalse(
                record["latitude"] is None
                or record["longitude"] is None
                or record["depth"] is None
                or record["mag"] is None
            )

    def test_clean_reports_with_error(self) -> None:
        for record in self.db.all("SELECT depth, mag FROM earthquakes"):
            record = record._asdict()
            self.assertFalse(record["depth"] == 0 or record["mag"] == 0)

    def tearDown(self) -> None:
        with self.db.transaction():
            self.db.run("DROP TABLE IF EXISTS earthquakes")
        self.db.close()


if __name__ == "__main__":
    unittest.main()
