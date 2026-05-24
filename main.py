from pathlib import Path

from helpers.extractor import Extractor
from helpers.transformers import SilverTransformer, GoldTransformer
from helpers.loader import Loader


def run_pipeline():
    print("Starting pipeline...")
    project_root = Path(__file__).resolve().parent

    raw_path    = project_root / "data" / "raw"
    bronze_path = project_root / "data" / "bronze"
    silver_path = project_root / "data" / "silver"
    gold_path   = project_root / "data" / "gold"

    loader = Loader()

    # Bronze: extract raw files
    extractor = Extractor(str(raw_path), str(bronze_path))
    raw_data = extractor.load_all()

    # Silver: clean and standardise
    silver_data = SilverTransformer().transform(raw_data)
    print("\n--- Silver: Saving ---")
    loader.save(silver_data, str(silver_path))

    # Gold: build star schema
    gold_data = GoldTransformer().transform(silver_data)
    print("\n--- Gold: Saving ---")
    loader.save(gold_data, str(gold_path))

    print("\nPipeline complete.")


if __name__ == "__main__":
    run_pipeline()
