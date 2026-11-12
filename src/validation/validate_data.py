
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "raw" / "olist"
REPORT_DIR = BASE_DIR / "data" / "processed" / "validation"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Primary key definitions
primary_keys = {
    "olist_customers_dataset.csv": ["customer_id"],
    "olist_orders_dataset.csv": ["order_id"],
    "olist_order_items_dataset.csv": ["order_id", "order_item_id"],
    "olist_order_payments_dataset.csv": ["order_id", "payment_sequential"],
    "olist_order_reviews_dataset.csv": ["review_id", "order_id"],
    "olist_products_dataset.csv": ["product_id"],
    "olist_sellers_dataset.csv": ["seller_id"],
    "product_category_name_translation.csv": ["product_category_name"]
}

results = []

for file, keys in primary_keys.items():

    df = pd.read_csv(DATA_DIR / file, low_memory=False)

    null_keys = int(df[keys].isnull().any(axis=1).sum())
    duplicate_keys = int(df.duplicated(subset=keys).sum())

    status = (
        "PASS"
        if null_keys == 0 and duplicate_keys == 0
        else "CHECK"
    )

    results.append({
        "dataset": file,
        "records": len(df),
        "null_key_records": null_keys,
        "duplicate_key_records": duplicate_keys,
        "status": status
    })

    print(f"\nDataset: {file}")
    print("Null key records:", null_keys)
    print("Duplicate key records:", duplicate_keys)
    print("Status:", status)

report = pd.DataFrame(results)

report.to_csv(
    REPORT_DIR / "validation_report.csv",
    index=False
)

print("\n========== VALIDATION SUMMARY ==========")
print(report)
print("\nValidation report saved!")
