"""
Special Olympics ETL Pipeline
Entry point — orchestrates Extract → Transform → Load → MySQL (bonus).
"""

import argparse
from helpers.extractor import Extractor
from helpers.transformers import SilverTransformer, GoldTransformer
from helpers.loader import Loader


def run_pipeline(load_mysql: bool = False):
    print("=" * 50)
    print("  Special Olympics ETL Pipeline")
    print("=" * 50)

    loader = Loader(silver_path="data/silver/", gold_path="data/gold/")

    # --- Extract (Bronze) ---
    extractor = Extractor(raw_path="data/raw/", bronze_path="data/bronze/")
    raw = extractor.load_all()

    # --- Transform Silver ---
    silver = SilverTransformer().transform(raw)
    loader.save_silver(silver)

    # --- Transform Gold ---
    gold = GoldTransformer().transform(silver)
    loader.save_all(gold)

    # --- Load MySQL (bonus) ---
    if load_mysql:
        from helpers.mysql_loader import MySQLLoader
        mysql = MySQLLoader(
            host="localhost",
            user="root",
            password="",
            database="special_olympics",
            gold_path="data/gold/",
            export_path="data/",
        )
        mysql.load_all(gold)
        mysql.verify()
        mysql.export_sql("r0913836_DatabaseExport.sql")

    print("\nPipeline complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Special Olympics ETL Pipeline")
    parser.add_argument(
        "--mysql",
        action="store_true",
        help="Also load gold tables into MySQL and export .sql dump",
    )
    args = parser.parse_args()
    run_pipeline(load_mysql=args.mysql)
