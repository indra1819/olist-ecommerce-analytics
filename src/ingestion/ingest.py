
from pathlib import Path
import logging
import pandas as pd

from src.database.connection import engine

logger = logging.getLogger(__name__)

# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = BASE_DIR / "data" / "raw" / "olist"


def ingest_csv(file_path):
    """Read a CSV file and load it into PostgreSQL."""

    file_path = Path(file_path)

    try:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix.lower() != ".csv":
            raise ValueError("Only CSV files are supported")

        # Read CSV
        df = pd.read_csv(file_path)

        if df.empty:
            raise ValueError("CSV contains no records")

        records_read = len(df)

        # Generate table name
        table_name = file_path.stem.lower()

        # Load data into PostgreSQL
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",
            index=False,
            chunksize=5000,
            method="multi"
        )

        records_loaded = len(df)

        logger.info(
            "Loaded %s records into %s",
            records_loaded,
            table_name
        )

        return {
            "file": file_path.name,
            "table": table_name,
            "records_read": records_read,
            "records_loaded": records_loaded,
            "status": "SUCCESS"
        }

    except Exception:
        logger.exception("Ingestion failed: %s", file_path.name)
        raise


def ingest_all_csvs():
    """Automatically ingest all CSV datasets."""

    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(
            f"Raw data directory not found: {RAW_DATA_DIR}"
        )

    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError("No CSV files found")

    results = []

    print("\n========== DATA INGESTION STARTED ==========\n")

    for file_path in csv_files:

        print(f"Processing: {file_path.name}")

        result = ingest_csv(file_path)

        results.append(result)

        print(f"Records loaded: {result['records_loaded']}")
        print(f"Status: {result['status']}\n")

    report = pd.DataFrame(results)

    print("\n========== INGESTION SUMMARY ==========\n")
    print(report.to_string(index=False))

    print("\nTotal datasets:", len(results))
    print(
        "Total records loaded:",
        report["records_loaded"].sum()
    )

    print("\nINGESTION COMPLETED SUCCESSFULLY!")

    return report


if __name__ == "__main__":
    ingest_all_csvs()
