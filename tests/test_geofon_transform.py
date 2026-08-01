import os
import tempfile
from unittest import TestCase

import pandas as pd

from src.transform.geofon_transform import (
    export_transformed,
    transform_geofon_data,
)


class TestGeofonTransform(TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()

        self.input_filepath = os.path.join(self.test_dir.name, "geofon_raw.csv")
        self.output_filepath = os.path.join(self.test_dir.name, "geofon_processed.csv")

    def tearDown(self):
        self.test_dir.cleanup()

    def create_mock_geofon_file(self):
        with open(self.input_filepath, "w", encoding="utf-8") as f:
            f.write(
                "time,latitude,longitude,depth,mag,place\n"
                '2026-07-24 18:43:05.7,31.58°N,141.51°E,39*,4.6,"Southeast of Honshu, Japan"\n'
                '2026-07-23 09:22:23.9,27.94°N,130.15°E,10*,5.1,"Ryukyu Islands, Japan"\n'
                "2026-07-19 01:40:05.2,38.68°N,133.53°E,450*,4.3,Sea of Japan\n"
            )

    def test_transform_geofon_data(self):
        self.create_mock_geofon_file()

        result = transform_geofon_data(self.input_filepath)

        self.assertIsInstance(result, pd.DataFrame)

        self.assertEqual(len(result), 3)

        self.assertEqual(result.iloc[0]["latitude"], 31.58)

        self.assertEqual(result.iloc[1]["longitude"], 130.15)

        self.assertEqual(result.iloc[2]["depth"], "450")

        self.assertEqual(result.iloc[0]["time"], "2026-07-24 18:43:05")

        self.assertEqual(result.iloc[0]["source"], "GEOFON")

    def test_export_transformed(self):
        self.create_mock_geofon_file()

        export_transformed(self.input_filepath, self.output_filepath)

        self.assertTrue(os.path.exists(self.output_filepath))

        df = pd.read_csv(self.output_filepath, encoding="utf-8")

        self.assertEqual(len(df), 3)

        self.assertEqual(df.iloc[0]["source"], "GEOFON")

        self.assertEqual(df.iloc[0]["latitude"], 31.58)
