"""
Loader — saves DataFrames to CSV for each layer.
"""

import os
import pandas as pd


class Loader:
    def __init__(
        self,
        silver_path: str = "data/silver/",
        gold_path: str = "data/gold/",
    ):
        self.silver_path = silver_path
        self.gold_path = gold_path

    def _save(self, data: dict, output_path: str) -> None:
        os.makedirs(output_path, exist_ok=True)
        for name, df in data.items():
            filepath = os.path.join(output_path, f"{name}.csv")
            df.to_csv(filepath, index=False)
            print(f"  [LOAD] Saved {name}.csv ({len(df):,} rows)")

    def save_silver(self, data: dict) -> None:
        """Save cleaned silver DataFrames to data/silver/ with silver_ prefix."""
        print("\n--- Silver: Saving ---")
        prefixed = {f"silver_{k}": v for k, v in data.items()}
        self._save(prefixed, self.silver_path)

    def save_all(self, data: dict) -> None:
        """Save gold star schema DataFrames to data/gold/."""
        print("\n--- Gold: Saving ---")
        self._save(data, self.gold_path)
