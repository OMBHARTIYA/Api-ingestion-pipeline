from __future__ import annotations

import logging

import pandas as pd

from pipeline_utils import BRONZE_DIR, RAW_DIR, ensure_directories, load_json, log_row_count, setup_logging, write_csv


def normalize_payload(file_name: str, root_key: str) -> pd.DataFrame:
    payload = load_json(RAW_DIR / file_name)
    return pd.json_normalize(payload[root_key])


def main() -> None:
    setup_logging()
    ensure_directories()
    logging.info("Normalizing raw JSON into bronze CSV files")

    tables = {
        "projects_bronze.csv": normalize_payload("projects_raw.json", "projects"),
        "work_items_bronze.csv": normalize_payload("work_items_raw.json", "work_items"),
        "status_events_bronze.csv": normalize_payload("status_events_raw.json", "status_events"),
        "contractors_bronze.csv": normalize_payload("contractors_raw.json", "contractors"),
    }

    for file_name, df in tables.items():
        log_row_count(file_name, df)
        write_csv(df, BRONZE_DIR / file_name)

    logging.info("Bronze transformation completed successfully")


if __name__ == "__main__":
    main()
