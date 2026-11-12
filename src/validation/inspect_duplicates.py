
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

file_path = (
    BASE_DIR / "data" / "raw" / "olist"
    / "olist_order_reviews_dataset.csv"
)

df = pd.read_csv(file_path)

duplicates = df[
    df.duplicated(subset=["review_id"], keep=False)
].sort_values("review_id")

print("Total review records:", len(df))
print("Duplicate review records:", len(duplicates))
print("Unique review IDs:", df["review_id"].nunique())

print("\nSample duplicate records:")
print(duplicates.head(15).to_string(index=False))

print("\nDuplicate review ID frequency:")
print(
    duplicates["review_id"]
    .value_counts()
    .head(10)
)

print("\nExact duplicate rows:", df.duplicated().sum())

print("\n========== DUPLICATE REVIEW ANALYSIS ==========")

duplicate_ids = (
    df["review_id"]
    .value_counts()
)

duplicate_ids = duplicate_ids[duplicate_ids > 1].index

sample_ids = list(duplicate_ids[:5])

for review_id in sample_ids:
    print(f"\nReview ID: {review_id}")

    records = df[df["review_id"] == review_id]

    print(records.to_string(index=False))

    print("Associated order IDs:")
    print(records["order_id"].tolist())


