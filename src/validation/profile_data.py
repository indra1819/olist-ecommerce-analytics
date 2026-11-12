
from pathlib import Path
import pandas as pd

# Project paths
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "raw" / "olist"
REPORT_DIR = BASE_DIR / "data" / "processed" / "profiling"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

print("\n========== OLIST DATA PROFILING ==========\n")

summary = []

for file_path in DATA_DIR.glob("*.csv"):

    print(f"\nDataset: {file_path.name}")

    try:
        df = pd.read_csv(file_path, low_memory=False)

        rows, columns = df.shape
        missing = int(df.isnull().sum().sum())
        duplicates = int(df.duplicated().sum())

        print("Rows:", rows)
        print("Columns:", columns)
        print("Missing Values:", missing)
        print("Duplicate Rows:", duplicates)

        print("\nColumn Details:")
        print(df.dtypes)

        print("\nSample Records:")
        print(df.head(3))

        summary.append({
            "dataset": file_path.name,
            "rows": rows,
            "columns": columns,
            "missing_values": missing,
            "duplicate_rows": duplicates
        })

    except Exception as error:
        print("ERROR:", error)

# Save profiling report
report = pd.DataFrame(summary)

report.to_csv(
    REPORT_DIR / "profiling_summary.csv",
    index=False
)

print("\n========== PROFILING COMPLETED ==========")
print(report)
print("\nReport saved successfully!")
