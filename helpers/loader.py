"""
Loader — saves dataFrames to csv for each layer.
"""

import os
import pandas as pd


class Loader:
    def save(self, data: dict, output_path: str) -> None:
        os.makedirs(output_path, exist_ok=True)
        for name, df in data.items():
            filepath = os.path.join(output_path, f"{name}.csv")
            df.to_csv(filepath, index=False)
            print(f"  [LOAD] Saved {name}.csv ({len(df):,} rows)")
