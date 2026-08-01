from pathlib import Path
from unittest import TestCase

from src.transform.geofon_transform import transform_genfon_data

RAW_PATH = Path("data/raw/geofon.csv")


class TestGeofonTransform(TestCase):
    def setUp(self) -> None:
        self._backup = RAW_PATH.read_text() if RAW_PATH.exists() else None

    def write_raw(self, *rows: str) -> None:
        header = "time,latitude,longitude,depth,mag,place\n"
        RAW_PATH.write_text(header + "\n".join(rows), encoding="utf-8")

    def test_valid_row_is_transformed(self) -> None:
        self.write_raw(
            '"2026-07-09 12:58:57.9","35.6762°N","139.6503°E","10*","5.1","Near Tokyo, Japan"'
        )
        result = transform_genfon_data()
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["time"], "2026-07-09 12:58:57")
        self.assertEqual(result.iloc[0]["latitude"], 35.6762)
        self.assertEqual(result.iloc[0]["longitude"], 139.6503)
        self.assertEqual(result.iloc[0]["depth"], "10")

    def test_source_column_is_added(self):
        self.write_raw(
            '"2026-07-09 12:58:57.9","35.6762°N","139.6503°E","10*","5.1","Tokyo"'
        )
        result = transform_genfon_data()
        self.assertEqual(result.iloc[0]["source"], "GEOFON")

    def test_empty_csv_returns_empty_dataframe(self) -> None:
        self.write_raw()
        result = transform_genfon_data()
        self.assertEqual(len(result), 0)

    def tearDown(self) -> None:
        if self._backup is not None:
            RAW_PATH.write_text(self._backup, encoding="utf-8")
        else:
            RAW_PATH.unlink()
