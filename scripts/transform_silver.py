from __future__ import annotations

import logging

import pandas as pd

from pipeline_utils import (
    ALLOWED_STATUSES,
    BRONZE_DIR,
    SILVER_DIR,
    ensure_directories,
    log_row_count,
    read_csv,
    setup_logging,
    validate_allowed_statuses,
    validate_dates,
    validate_foreign_key,
    validate_latest_event_flag,
    validate_not_null,
    write_csv,
)


def main() -> None:
    setup_logging()
    ensure_directories()
    logging.info("Transforming bronze tables into silver dimensions and facts")

    projects = read_csv(BRONZE_DIR / "projects_bronze.csv")
    work_items = read_csv(BRONZE_DIR / "work_items_bronze.csv")
    status_events = read_csv(BRONZE_DIR / "status_events_bronze.csv")
    contractors = read_csv(BRONZE_DIR / "contractors_bronze.csv")

    dim_project = projects.copy()
    dim_work_item = work_items.copy()
    dim_contractor = contractors.copy()
    dim_status = pd.DataFrame(ALLOWED_STATUSES, columns=["StatusID", "StatusName", "ProgressWeight"])

    fact_status_event = status_events.copy()
    fact_status_event["EventDate"] = pd.to_datetime(fact_status_event["EventDate"]).dt.date.astype(str)
    fact_status_event["EventDateTime"] = pd.to_datetime(fact_status_event["EventDateTime"]).dt.strftime("%Y-%m-%dT%H:%M:%S")
    fact_status_event["DaysInPreviousStatus"] = fact_status_event["DaysInPreviousStatus"].fillna(0).astype(int)
    fact_status_event["IsLatestStatus"] = fact_status_event["IsLatestStatus"].astype(bool)
    fact_status_event["ContractorID"] = fact_status_event["UpdatedBy"]
    fact_status_event = fact_status_event.drop(columns=["UpdatedBy"])

    validate_not_null(dim_project, ["ProjectID"], "dim_project")
    validate_not_null(dim_work_item, ["WorkItemID", "ProjectID", "CurrentStatusID"], "dim_work_item")
    validate_not_null(dim_contractor, ["ContractorID"], "dim_contractor")
    validate_not_null(fact_status_event, ["StatusEventID", "WorkItemID", "ProjectID", "StatusID", "ContractorID"], "fact_status_event")

    validate_foreign_key(dim_work_item, "ProjectID", dim_project, "ProjectID", "dim_work_item -> dim_project")
    validate_foreign_key(fact_status_event, "ProjectID", dim_project, "ProjectID", "fact_status_event -> dim_project")
    validate_foreign_key(fact_status_event, "WorkItemID", dim_work_item, "WorkItemID", "fact_status_event -> dim_work_item")
    validate_foreign_key(fact_status_event, "ContractorID", dim_contractor, "ContractorID", "fact_status_event -> dim_contractor")
    validate_allowed_statuses(dim_work_item, "CurrentStatusID")
    validate_allowed_statuses(fact_status_event, "StatusID")
    validate_dates(dim_project, ["StartDate", "EndDate"], "dim_project")
    validate_dates(dim_work_item, ["PlannedStartDate", "PlannedFinishDate"], "dim_work_item")
    validate_dates(fact_status_event, ["EventDate", "EventDateTime"], "fact_status_event")
    validate_latest_event_flag(fact_status_event)

    for label, df in {
        "dim_project": dim_project,
        "dim_work_item": dim_work_item,
        "dim_status": dim_status,
        "dim_contractor": dim_contractor,
        "fact_status_event": fact_status_event,
    }.items():
        log_row_count(label, df)

    write_csv(dim_project, SILVER_DIR / "dim_project.csv")
    write_csv(dim_work_item, SILVER_DIR / "dim_work_item.csv")
    write_csv(dim_status, SILVER_DIR / "dim_status.csv")
    write_csv(dim_contractor, SILVER_DIR / "dim_contractor.csv")
    write_csv(fact_status_event, SILVER_DIR / "fact_status_event.csv")

    logging.info("Silver transformation completed successfully")


if __name__ == "__main__":
    main()
