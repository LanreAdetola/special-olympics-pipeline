# Special Olympics Belgium — Data Pipeline & Analytics

Integrated Lab | Thomas More | r0913836 | 2025–2026

A local Python ETL pipeline that ingests raw Excel exports from Special
Olympics Belgium, transforms them through Bronze → Silver → Gold layers,
and outputs clean CSVs ready for Power BI reporting.

## How to Run

**Requirements:** Python 3.11+

1. Clone the repository

   ```bash
   git clone https://github.com/LanreAdetola/special-olympics-pipeline.git
   cd special-olympics-pipeline
   ```

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Place the raw Excel files in `data/raw/`

4. Run the pipeline

   ```bash
   python main.py
   ```

Output CSVs will be written to `data/silver/` and `data/gold/`.

## Folder Structure

```text
├── main.py                        # Pipeline entry point
├── requirements.txt
├── docs/
│   └── star_schema.png            # Star schema diagram
├── helpers/
│   ├── __init__.py
│   ├── extractor.py               # Bronze: loads raw Excel files
│   ├── loader.py                  # Saves DataFrames to CSV for each layer
│   └── transformers/
│       ├── __init__.py
│       ├── silver_transformer.py  # Silver: cleans and standardises raw data
│       └── gold_transformer.py    # Gold: builds star schema tables
├── data/
│   ├── raw/                       # Source XLSX files (not committed)
│   ├── bronze/                    # Raw file copies (audit trail)
│   ├── silver/                    # Cleaned and standardised CSVs
│   └── gold/                      # Final fact and dimension CSVs
└── README.md
```

## Dependencies

| Package  | Purpose                            |
| -------- | ---------------------------------- |
| pandas   | Data manipulation & transformation |
| openpyxl | Reading `.xlsx` files              |

## Silver Output Files

| File                  | Description                          |
| --------------------- | ------------------------------------ |
| `results.csv`         | All athlete results across all years |
| `clubs.csv`           | Club master data, cleaned            |
| `certifications.csv`  | Athlete certifications, cleaned      |

## Gold Output Files

| File               | Description                                    |
| ------------------ | ---------------------------------------------- |
| `fact_results.csv` | Core fact table — results per event (112k rows)|
| `dim_athlete.csv`  | Athlete dimension (16,124 athletes)            |
| `dim_club.csv`     | Club dimension (548 clubs including historical)|
| `dim_sport.csv`    | Sport dimension (22 sports)                    |
| `dim_event.csv`    | Event dimension (375 events)                   |
| `dim_date.csv`     | Date dimension — 9 editions                    |
