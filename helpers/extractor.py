"""
Extractor — Bronze layer
Loads all raw source files into DataFrames without modification.
"""

import os
import shutil
import pandas as pd


RESULT_YEARS = [2015, 2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025]


class Extractor:
    """Reads raw Excel files from data/raw/ and copies them to data/bronze/."""

    def __init__(self, raw_path: str, bronze_path: str = None):
        self.raw_path = raw_path
        self.bronze_path = bronze_path

    def _load(self, filename: str) -> pd.DataFrame:
        """Load one Excel file and optionally back it up to bronze."""
        filepath = os.path.join(self.raw_path, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Raw file not found: {filepath}")

        print(f"  [EXTRACT] {filename}")
        df = pd.read_excel(filepath)

        if self.bronze_path:
            os.makedirs(self.bronze_path, exist_ok=True)
            shutil.copy2(filepath, os.path.join(self.bronze_path, filename))

        return df

    def load_certifications(self) -> pd.DataFrame:
        return self._load("Thomas More Data Certifications.xlsx")

    def load_clubs(self) -> pd.DataFrame:
        return self._load("Thomas More Data Clubs.xlsx")

    def load_results(self, year: int) -> pd.DataFrame:
        return self._load(f"Thomas More Results {year}.xlsx")

    def load_all_results(self) -> pd.DataFrame:
        """Load and combine all yearly results into one DataFrame."""
        frames = []
        for year in RESULT_YEARS:
            try:
                df = self.load_results(year)
                df["edition_year"] = year
                frames.append(df)
            except FileNotFoundError:
                print(f"  [EXTRACT] Skipping {year}: file not found")

        combined = pd.concat(frames, ignore_index=True)
        print(f"  [EXTRACT] Combined results: {len(combined):,} rows across {len(frames)} files loaded")
        return combined

    def load_all(self) -> dict:
        """Load all source files and return them as a dictionary."""
        print("\n--- Bronze: Extracting raw sources ---")
        return {
            "certifications": self.load_certifications(),
            "clubs":          self.load_clubs(),
            "results":        self.load_all_results(),
        }
