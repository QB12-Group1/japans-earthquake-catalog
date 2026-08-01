import re
import sqlite3
import unittest

from config.settings import BASE_DIR

SQL_DIR = BASE_DIR / "sql"


def to_sqlite_compatible(sql: str) -> str:
    return re.sub(r"::\w+(\(\d+(,\s*\d+)?\))?", "", sql)


class TestAvgMagnitudeSorting(unittest.TestCase):
    SCHEMA = """
    CREATE TABLE earthquakes (
        id INTEGER PRIMARY KEY,
        source TEXT,
        region TEXT,
        mag REAL
    );
    """

    FIXTURE_ROWS = [
        ("GEOFON", "Kyoto", 8.0),
        ("USGS", "Tokyo", 6.0),
        ("USGS", "Tokyo", 7.0),
        ("USGS", "Osaka", 5.0),
        ("GEOFON", "Tokyo", 4.0),
        ("GEOFON", "Tokyo", 4.0),
        ("EMSC", "Osaka", 3.0),
        ("EMSC", "Osaka", 3.0),
        ("EMSC", "Osaka", 3.0),
    ]

    EXPECTED_ORDER = [
        ("GEOFON", "Kyoto", 8.0),
        ("USGS", "Tokyo", 6.5),
        ("USGS", "Osaka", 5.0),
        ("GEOFON", "Tokyo", 4.0),
        ("EMSC", "Osaka", 3.0),
    ]

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(self.SCHEMA)
        self.conn.executemany(
            "INSERT INTO earthquakes (source, region, mag) VALUES (?, ?, ?)",
            self.FIXTURE_ROWS,
        )
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def run_query(self):
        query = (SQL_DIR / "analysis/avg_magnitude.sql").read_text()
        query = to_sqlite_compatible(query)
        return self.conn.execute(query).fetchall()

    def test_results_are_sorted_descending_by_average(self):
        rows = self.run_query()
        averages = [r[2] for r in rows]
        self.assertEqual(averages, sorted(averages, reverse=True))

    def test_exact_group_order_matches_expected(self):
        rows = self.run_query()
        actual = [(r[0], r[1], r[2]) for r in rows]
        self.assertEqual(actual, self.EXPECTED_ORDER)


class TestIndexesExist(unittest.TestCase):
    SCHEMA = """
    CREATE TABLE earthquakes (
        id INTEGER PRIMARY KEY,
        time TEXT,
        region TEXT,
        mag REAL
    );
    """

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(self.SCHEMA)
        create_indexes_sql = (SQL_DIR / "transform/create_indexes.sql").read_text()
        self.conn.executescript(create_indexes_sql)
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def _indexed_columns(self) -> set[str]:
        index_rows = self.conn.execute("PRAGMA index_list('earthquakes')").fetchall()
        columns_with_index = set()
        for index_row in index_rows:
            index_name = index_row[1]
            info_rows = self.conn.execute(
                f"PRAGMA index_info('{index_name}')"
            ).fetchall()
            for info_row in info_rows:
                columns_with_index.add(info_row[2])
        return columns_with_index

    def test_time_region_and_mag_are_indexed(self):
        columns_with_index = self._indexed_columns()
        self.assertIn("time", columns_with_index)
        self.assertIn("region", columns_with_index)
        self.assertIn("mag", columns_with_index)

    def test_at_least_three_indexes_were_created(self):
        index_rows = self.conn.execute("PRAGMA index_list('earthquakes')").fetchall()
        self.assertGreaterEqual(len(index_rows), 3)
