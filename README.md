```markdown
# Special Olympics Belgium — Data Pipeline & Analytics
**Integrated Lab | Thomas More | r0913836 | 2025–2026**

A local Python ETL pipeline that ingests raw Excel exports from Special Olympics Belgium,
transforms them through Bronze → Silver → Gold layers, and outputs clean CSVs ready for
Power BI reporting.



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

Output CSVs will be written to `data/gold/`.



## Folder Structure

```
├── main.py                  # Pipeline entry point
├── requirements.txt
├── helpers/
│   ├── __init__.py
│   ├── extractor.py         # Bronze: raw ingestion classes
│   ├── transformer.py       # Silver: cleaning and standardisation
│   └── loader.py            # Gold: Star Schema output + MySQL (bonus)
├── data/
│   ├── raw/                 # Source XLSX files (not committed)
│   ├── bronze/              # Raw ingested copies
│   ├── silver/              # Cleaned and filtered data
│   └── gold/                # Final fact and dimension CSVs
└── README.md
```



## Dependencies

| Package    | Purpose                        |
|------------|--------------------------------|
| pandas     | Data manipulation & transformation |
| openpyxl   | Reading `.xlsx` files          |



## Output Files (Gold Layer)

| File | Description |
|------|-------------|
| `fact_results.csv` | Core fact table — athlete results per event |
| `dim_athlete.csv` | Athlete dimension |
| `dim_club.csv` | Club dimension |
| `dim_sport.csv` | Sport dimension |
| `dim_event.csv` | Event dimension |
| `dim_date.csv` | Date dimension (derived) |

