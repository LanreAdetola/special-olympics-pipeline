from pathlib import Path

from helpers.extractor import Extractor

def run_pipeline():
    print("Starting pipeline..")
    # Bronze phase
    project_root = Path(__file__).resolve().parent
    raw_path = project_root / "data" / "raw"
    bronze_path = project_root / "data" / "bronze"

    extractor = Extractor(str(raw_path), str(bronze_path))
    extractor.load_all()

    # Silver phase
    # Gold phase

if __name__ == "__main__":
    run_pipeline()