# Copyright 2020 (c) Cognizant Digital Business, Evolutionary AI. All rights reserved. Issued under the Apache 2.0 License.

import os
import unittest
import urllib.request

import pandas as pd

from validation.scenario_generator import generate_scenario, NPI_COLUMNS, MAX_NPIS

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_PATH = os.path.join(ROOT_DIR, 'fixtures')
DATA_FILE = os.path.join(FIXTURES_PATH, "OxCGRT_latest.csv")
DATA_URL = "https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv"

ONE_NPIS = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]


def _get_dataset():
    # Download and cache the raw data file if it doesn't exist
    if not os.path.exists(DATA_FILE):
        urllib.request.urlretrieve(DATA_URL, DATA_FILE)
    latest_df = pd.read_csv(DATA_FILE,
                            parse_dates=['Date'],
                            encoding="ISO-8859-1",
                            error_bad_lines=False)
    latest_df["RegionName"] = latest_df["RegionName"].fillna("")
    return latest_df


class TestScenarioGenerator(unittest.TestCase):

    def test_generate_scenario_historical(self):
        latest_df = _get_dataset()
        start_date_str = "2020-08-01"
        end_date_str = "2020-08-4"
        countries = ["Italy"]
        scenario_df = generate_scenario(start_date_str, end_date_str, latest_df, countries)
        self.assertIsNotNone(scenario_df)
        # Misleading name but checks the elements, regardless of order
        self.assertCountEqual(countries, scenario_df.CountryName.unique(), "Not the requested countries")
        # Inception is 1/1/2020
        self.assertEqual(217, len(scenario_df), "Expected the number of days between inception and end date")

        # Check multiple countries
        countries = ["France", "Italy"]
        scenario_df = generate_scenario(start_date_str, end_date_str, latest_df, countries)
        self.assertIsNotNone(scenario_df)
        # Misleading name but checks the elements, regardless of order
        self.assertCountEqual(countries, scenario_df.CountryName.unique(), "Not the requested countries")
        # Inception is 1/1/2020
        self.assertEqual(217*2, len(scenario_df), "Expected the number of days between inception and end date")

        # All countries: do not pass a countries list
        scenario_df = generate_scenario(start_date_str, end_date_str, latest_df)
        self.assertIsNotNone(scenario_df)
        # Misleading name but checks the elements, regardless of order
        self.assertCountEqual(latest_df.CountryName.unique(), scenario_df.CountryName.unique(),
                              "Not the requested countries")
        # Inception is 1/1/2020
        # Contains the regions too. -1 to remove the NaN region, already counted as a country
        nb_geos = len(latest_df.CountryName.unique()) + len(latest_df.RegionName.unique()) - 1
        self.assertEqual(217*nb_geos,
                         len(scenario_df),
                         "Expected the number of days between inception and end date")

    def test_generate_scenario_future(self):
        # Scenario = Freeze
        latest_df = _get_dataset()
        start_date_str = "2021-01-01"
        end_date_str = "2021-01-31"
        countries = ["Italy"]
        scenario_df = generate_scenario(start_date_str, end_date_str, latest_df, countries, scenario="Freeze")
        self.assertIsNotNone(scenario_df)
        # Misleading name but checks the elements, regardless of order
        self.assertCountEqual(countries, scenario_df.CountryName.unique(), "Not the requested countries")
        # Inception is 1/1/2020
        self.assertEqual(397, len(scenario_df), "Expected the number of days between inception and end date")
        # The last 31 rows must be the same
        self.assertEqual(0, scenario_df.tail(31)[NPI_COLUMNS].diff().sum().sum(),
                         "Expected the last 31 rows to have the same frozen IP")

        # Scenario = MIN
        scenario_df = generate_scenario(start_date_str, end_date_str, latest_df, countries, scenario="MIN")
        self.assertIsNotNone(scenario_df)
        # Misleading name but checks the elements, regardless of order
        self.assertCountEqual(countries, scenario_df.CountryName.unique(), "Not the requested countries")
        # Inception is 1/1/2020
        self.assertEqual(397, len(scenario_df), "Expected the number of days between inception and end date")
        # The last 31 rows must be the same
        self.assertEqual(0, scenario_df.tail(31)[NPI_COLUMNS].sum().sum(),
                         "Expected the last 31 rows to have NPIs set to 0")

        # Scenario = MAX
        scenario_df = generate_scenario(start_date_str, end_date_str, latest_df, countries, scenario="MAX")
        self.assertIsNotNone(scenario_df)
        # Misleading name but checks the elements, regardless of order
        self.assertCountEqual(countries, scenario_df.CountryName.unique(), "Not the requested countries")
        # Inception is 1/1/2020
        self.assertEqual(397, len(scenario_df), "Expected the number of days between inception and end date")
        # The last 31 rows must be the same
        self.assertEqual(sum(MAX_NPIS), scenario_df.tail(31)[NPI_COLUMNS].mean().sum(),
                         "Expected the last 31 rows to have NPIs set to their max value")

        # Scenario = Custom
        scenario_df = generate_scenario(start_date_str, end_date_str, latest_df, countries, scenario=ONE_NPIS)
        self.assertIsNotNone(scenario_df)
        # Misleading name but checks the elements, regardless of order
        self.assertCountEqual(countries, scenario_df.CountryName.unique(), "Not the requested countries")
        # Inception is 1/1/2020
        self.assertEqual(397, len(scenario_df), "Expected the number of days between inception and end date")
        # The last 31 rows must be the same
        self.assertEqual(1, scenario_df.tail(31)[NPI_COLUMNS].mean().mean(),
                         "Expected the last 31 rows to have all NPIs set to 1")

        # Check 2 countries
        countries = ["France", "Italy"]
        scenario_df = generate_scenario(start_date_str, end_date_str, latest_df, countries, scenario="Freeze")
        self.assertIsNotNone(scenario_df)
        # Misleading name but checks the elements, regardless of order
        self.assertCountEqual(countries, scenario_df.CountryName.unique(), "Not the requested countries")
        # Inception is 1/1/2020
        self.assertEqual(397*2, len(scenario_df), "Expected the number of days between inception and end date")
