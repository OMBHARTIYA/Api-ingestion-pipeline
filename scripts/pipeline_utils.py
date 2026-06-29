from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterable

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"
CONFIG_PATH = ROOT_DIR / "config" / "sample_config.json"

ALLOWED_STATUSES = [
    ("STS-001", "Not Started", 0.00),
    ("STS-002", "Released", 0.15),
    ("STS-003", "In Progress", 0.50),
    ("STS-004", "Completed", 0.85),
    ("STS-005", "Approved", 1.00),
    ("STS-006", "Blocked", 0.25),
    ("STS-007", "Rework", 0.40),
    ("STS-008", "Cancelled", 0.00),
]


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def ensure_directories() -> None:
    for path in [RAW_DIR, BRONZE_DIR, SILVER_DIR, GOLD_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(payload: dict, path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)
    logging.info("Wrote %s rows to %s", len(df), path.relative_to(ROOT_DIR))


def read_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    logging.info("Loaded %s rows from %s", len(df), path.relative_to(ROOT_DIR))
    return df


def validate_not_null(df: pd.DataFrame, columns: Iterable[str], table_name: str) -> None:
    for column in columns:
        if df[column].isna().any():
            raise ValueError(f"{table_name}.{column} contains null values")


def validate_foreign_key(
    child_df: pd.DataFrame,
    child_column: str,
    parent_df: pd.DataFrame,
    parent_column: str,
    relationship_name: str,
) -> None:
    missing = set(child_df[child_column]) - set(parent_df[parent_column])
    if missing:
        sample = list(sorted(missing))[:5]
        raise ValueError(f"{relationship_name} is invalid. Missing keys sample: {sample}")


def validate_allowed_statuses(df: pd.DataFrame, status_column: str) -> None:
    allowed = {status_id for status_id, _, _ in ALLOWED_STATUSES}
    invalid = set(df[status_column]) - allowed
    if invalid:
        raise ValueError(f"Unexpected statuses found: {sorted(invalid)}")


def validate_dates(df: pd.DataFrame, columns: Iterable[str], table_name: str) -> None:
    for column in columns:
        parsed = pd.to_datetime(df[column], errors="coerce")
        if parsed.isna().any():
            raise ValueError(f"{table_name}.{column} contains invalid dates")


def validate_latest_event_flag(df: pd.DataFrame) -> None:
    latest_counts = df.groupby("WorkItemID")["IsLatestStatus"].sum()
    invalid = latest_counts[latest_counts != 1]
    if not invalid.empty:
        raise ValueError("Each work item must have exactly one latest event flag")


def log_row_count(label: str, df: pd.DataFrame) -> None:
    logging.info("%s row count: %s", label, len(df))
