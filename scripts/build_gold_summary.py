from __future__ import annotations

import logging

import pandas as pd

from pipeline_utils import GOLD_DIR, SILVER_DIR, ensure_directories, read_csv, setup_logging, write_csv


def main() -> None:
    setup_logging()
    ensure_directories()
    logging.info("Aggregating silver tables into gold summaries")

    dim_project = read_csv(SILVER_DIR / "dim_project.csv")
    dim_work_item = read_csv(SILVER_DIR / "dim_work_item.csv")
    dim_status = read_csv(SILVER_DIR / "dim_status.csv")
    dim_contractor = read_csv(SILVER_DIR / "dim_contractor.csv")
    fact_status_event = read_csv(SILVER_DIR / "fact_status_event.csv")

    progress_map = dim_status.set_index("StatusID")["ProgressWeight"]

    work_item_progress = (
        dim_work_item.assign(ProgressWeight=dim_work_item["CurrentStatusID"].map(progress_map))
        .groupby("ProjectID", as_index=False)
        .agg(
            TotalWorkItems=("WorkItemID", "count"),
            CompletedWorkItems=("CurrentStatusID", lambda s: int((s == "STS-004").sum())),
            ApprovedWorkItems=("CurrentStatusID", lambda s: int((s == "STS-005").sum())),
            BlockedWorkItems=("CurrentStatusID", lambda s: int((s == "STS-006").sum())),
            AverageProgressWeight=("ProgressWeight", "mean"),
        )
    )
    project_progress_summary = dim_project[["ProjectID", "ProjectName"]].merge(work_item_progress, on="ProjectID", how="left")
    project_progress_summary["CompletionPercent"] = (
        (project_progress_summary["ApprovedWorkItems"] + project_progress_summary["CompletedWorkItems"])
        / project_progress_summary["TotalWorkItems"]
        * 100
    ).round(2)
    project_progress_summary["AverageProgressWeight"] = project_progress_summary["AverageProgressWeight"].round(4)

    contractor_events = (
        fact_status_event.groupby("ContractorID", as_index=False)
        .agg(
            TotalEvents=("StatusEventID", "count"),
            CompletedEvents=("StatusID", lambda s: int((s == "STS-004").sum())),
            BlockedEvents=("StatusID", lambda s: int((s == "STS-006").sum())),
            ReworkEvents=("StatusID", lambda s: int((s == "STS-007").sum())),
        )
    )
    contractor_performance_summary = dim_contractor[["ContractorID", "ContractorName"]].merge(
        contractor_events, on="ContractorID", how="left"
    )

    fact_status_event["YearMonth"] = pd.to_datetime(fact_status_event["EventDate"]).dt.strftime("%Y-%m")
    monthly_progress_summary = (
        fact_status_event.groupby(["YearMonth", "ProjectID"], as_index=False)
        .agg(
            EventsCount=("StatusEventID", "count"),
            CompletedCount=("StatusID", lambda s: int((s == "STS-004").sum())),
            ApprovedCount=("StatusID", lambda s: int((s == "STS-005").sum())),
            BlockedCount=("StatusID", lambda s: int((s == "STS-006").sum())),
        )
        .sort_values(["YearMonth", "ProjectID"])
    )

    write_csv(project_progress_summary, GOLD_DIR / "project_progress_summary.csv")
    write_csv(contractor_performance_summary.fillna(0), GOLD_DIR / "contractor_performance_summary.csv")
    write_csv(monthly_progress_summary, GOLD_DIR / "monthly_progress_summary.csv")

    logging.info("Gold summary build completed successfully")


if __name__ == "__main__":
    main()
