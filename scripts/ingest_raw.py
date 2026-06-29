from __future__ import annotations

import logging

from pipeline_utils import RAW_DIR, ensure_directories, load_json, setup_logging


def main() -> None:
    setup_logging()
    ensure_directories()
    logging.info("Validating synthetic raw JSON payloads")

    payload_names = [
        "projects_raw.json",
        "work_items_raw.json",
        "status_events_raw.json",
        "contractors_raw.json",
    ]

    for payload_name in payload_names:
        payload = load_json(RAW_DIR / payload_name)
        entity_name = next(iter(payload))
        row_count = len(payload[entity_name])
        logging.info("Validated %s with %s records", payload_name, row_count)

    logging.info("Raw ingestion simulation completed successfully")


if __name__ == "__main__":
    main()
