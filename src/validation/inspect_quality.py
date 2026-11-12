
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "raw" / "olist"
REPORT_DIR = BASE_DIR / "data" / "processed" / "profiling"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

key_columns = {
    "olist_customers_dataset.csv": ["customer_id"],
    "olist_orders_dataset.csv": ["order_id"],
    "olist_order_items_dataset.csv": ["order_id", "order_item_id"],
    "olist_order_payments_dataset.csv": ["order_id", "payment_sequential"],
    "olist_order_reviews_dataset.csv": ["review_id"],
    "olist_products_dataset.csv": ["product_id"],
    "olist_sellers_dataset.csv": ["seller_id"],
    "product_category_name_translation.csv": ["product_category_name"]
}

reports = []

for file in DATA_DIR.glob("*.csv"):

    df = pd.read_csv(file, low_memory=False)

    print(f"\n========== {file.name} ==========")

    # Missing values by column
    null_counts = df.isnull().sum()

    for column, count in null_counts.items():
        if count > 0:
            print(f"Missing: {column} = {count}")

            reports.append({
                "dataset": file.name,
                "column": column,
                "missing_values": int(count),
                "missing_percentage": round(
                    count / len(df) * 100, 2
                )
            })

    # Duplicate inspection
    print("Exact duplicate rows:", df.duplicated().sum())

    # Primary key candidate inspection
    keys = key_columns.get(file.name)

    if keys:
        duplicate_keys = df.duplicated(subset=keys).sum()
        print("Duplicate key records:", duplicate_keys)

    print("Data types:")
    print(df.dtypes)

# Save detailed report
pd.DataFrame(reports).to_csv(
    REPORT_DIR / "column_quality_report.csv",
    index=False
)

print("\nDetailed quality inspection completed!")
