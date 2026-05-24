"""
MySQL Loader — Bonus layer
Ingests all gold star schema tables into a local MySQL database.
Also exports a .sql dump file for submission.
"""

import os
import subprocess
import pandas as pd
from sqlalchemy import create_engine, text


# Table load order — dimensions before fact to satisfy foreign key logic
LOAD_ORDER = [
    "dim_date",
    "dim_sport",
    "dim_event",
    "dim_club",
    "dim_athlete",
    "fact_results",
]


class MySQLLoader:
    """
    Connects to a local MySQL database and loads all gold CSV tables into it.
    Also generates a .sql export file for submission.
    """

    def __init__(
        self,
        host: str = "localhost",
        user: str = "root",
        password: str = "",
        database: str = "special_olympics",
        gold_path: str = "data/gold/",
        export_path: str = "data/",
    ):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.gold_path = gold_path
        self.export_path = export_path
        self.engine = self._create_engine()

    def _create_engine(self):
        """Create SQLAlchemy engine for MySQL connection."""
        if self.password:
            url = f"mysql+pymysql://{self.user}:{self.password}@{self.host}/{self.database}"
        else:
            url = f"mysql+pymysql://{self.user}@{self.host}/{self.database}"
        engine = create_engine(url, echo=False)
        print(f"  [MYSQL] Connected to {self.host}/{self.database}")
        return engine

    def load_table(self, df: pd.DataFrame, table_name: str) -> None:
        """Load a single DataFrame into MySQL, replacing the table if it exists."""
        with self.engine.begin() as conn:
            df.to_sql(
                name=table_name,
                con=conn,
                if_exists="replace",   # drop and recreate on each run
                index=False,
                chunksize=1000,        # batch inserts for performance
            )
        print(f"  [MYSQL] Loaded {table_name:<30} {len(df):>7,} rows")

    def load_all(self, tables: dict) -> None:
        """Load all gold tables into MySQL in the correct order."""
        print("\n--- MySQL: Loading star schema tables ---")
        for name in LOAD_ORDER:
            if name in tables:
                self.load_table(tables[name], name)
            else:
                print(f"  [WARN] Table '{name}' not found — skipping")
        print(f"\n  Done. All tables loaded into {self.database}")

    def export_sql(self, filename: str = "r0913836_DatabaseExport.sql") -> None:
        """
        Export the full database to a .sql file using mysqldump.
        This is the file required for submission.
        """
        output_path = os.path.join(self.export_path, filename)
        os.makedirs(self.export_path, exist_ok=True)

        print(f"\n--- MySQL: Exporting .sql dump ---")

        # Build mysqldump command
        cmd = [
            "mysqldump",
            f"--user={self.user}",
            "--no-tablespaces",
            "--routines",
            "--triggers",
            self.database,
        ]

        # Add password flag only if password is set
        if self.password:
            cmd.insert(2, f"--password={self.password}")

        try:
            with open(output_path, "w") as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)

            if result.returncode == 0:
                size_kb = os.path.getsize(output_path) / 1024
                print(f"  [MYSQL] Exported: {output_path} ({size_kb:.1f} KB)")
            else:
                print(f"  [ERROR] mysqldump failed: {result.stderr}")

        except FileNotFoundError:
            print("  [ERROR] mysqldump not found. Make sure MySQL is installed and in PATH.")

    def verify(self) -> None:
        """Print row counts for all tables in the database as a sanity check."""
        print("\n--- MySQL: Verification ---")
        with self.engine.connect() as conn:
            for table in LOAD_ORDER:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  {table:<30} {count:>7,} rows")
                except Exception as e:
                    print(f"  {table:<30} ERROR — {e}")
