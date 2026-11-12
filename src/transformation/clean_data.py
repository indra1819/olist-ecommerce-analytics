
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def clean_dataframe(df, dataset_name):
    """
    Clean a DataFrame without blindly deleting business records.
    """

    if df is None or df.empty:
        raise ValueError("DataFrame is empty")

    original_rows = len(df)

    # 1. Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # 2. Remove exact duplicate rows
    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # 3. Handle empty string values
    df = df.replace(r"^\s*$", pd.NA, regex=True)

    # 4. Trim whitespace in text columns
    text_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:
        df[column] = df[column].apply(
            lambda value: value.strip()
            if isinstance(value, str)
            else value
        )

    # 5. Convert known date columns
    date_columns = [
        column for column in df.columns
        if column.endswith("_date")
        or column.endswith("_timestamp")
    ]

    for column in date_columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    # 6. Report cleaning results
    cleaned_rows = len(df)
    missing_values = int(df.isna().sum().sum())

    report = {
        "dataset": dataset_name,
        "original_rows": original_rows,
        "cleaned_rows": cleaned_rows,
        "duplicates_removed": duplicate_count,
        "missing_values_remaining": missing_values,
        "status": "SUCCESS"
    }

    logger.info("Cleaning completed: %s", report)

    return df, report
