
import logging
import pandas as pd

from src.database.connection import engine
from src.transformation.clean_data import clean_dataframe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TABLES = [
    "olist_customers_dataset",
    "olist_geolocation_dataset",
    "olist_orders_dataset",
    "olist_order_items_dataset",
    "olist_order_payments_dataset",
    "olist_order_reviews_dataset",
    "olist_products_dataset",
    "olist_sellers_dataset",
    "product_category_name_translation"
]


def transform_all_tables():

    reports = []

    print("\n========== TRANSFORMATION STARTED ==========\n")

    for table_name in TABLES:

        print(f"Processing: {table_name}")

        try:
            # Read raw PostgreSQL table
            df = pd.read_sql_table(
                table_name,
                con=engine
            )

            # Apply cleaning
            cleaned_df, report = clean_dataframe(
                df,
                table_name
            )

            # Create separate cleaned table
            cleaned_table = f"{table_name}_cleaned"

            cleaned_df.to_sql(
                name=cleaned_table,
                con=engine,
                if_exists="replace",
                index=False,
                chunksize=1000
            )

            report["output_table"] = cleaned_table

            reports.append(report)

            print(f"Original rows: {report['original_rows']}")
            print(f"Cleaned rows: {report['cleaned_rows']}")
            print(f"Duplicates removed: {report['duplicates_removed']}")
            print(f"Missing values remaining: {report['missing_values_remaining']}")
            print("Status: SUCCESS\n")

        except Exception:
            logger.exception("Transformation failed: %s", table_name)
            raise

    # Generate transformation report
    report_df = pd.DataFrame(reports)

    print("\n========== TRANSFORMATION SUMMARY ==========\n")
    print(report_df.to_string(index=False))

    report_df.to_csv(
        "logs/transformation_report.csv",
        index=False
    )

    print("\nTotal datasets transformed:", len(reports))
    print("\nTRANSFORMATION COMPLETED SUCCESSFULLY!")

    return report_df


if __name__ == "__main__":
    transform_all_tables()
