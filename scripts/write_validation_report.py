from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
GOLD = DATA / "gold"


def read_csv(relative_path: str) -> pd.DataFrame:
    return pd.read_csv(DATA / relative_path)


def check(condition: bool, label: str, detail: str) -> dict[str, str]:
    return {
        "Check": label,
        "Result": "PASS" if condition else "FAIL",
        "Detail": detail,
    }


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    GOLD.mkdir(parents=True, exist_ok=True)

    dim_project = read_csv("silver/dim_project.csv")
    dim_work_item = read_csv("silver/dim_work_item.csv")
    dim_status = read_csv("silver/dim_status.csv")
    dim_contractor = read_csv("silver/dim_contractor.csv")
    fact_status_event = read_csv("silver/fact_status_event.csv")
    project_summary = read_csv("gold/project_progress_summary.csv")
    contractor_summary = read_csv("gold/contractor_performance_summary.csv")
    monthly_summary = read_csv("gold/monthly_progress_summary.csv")

    row_counts = {
        "dim_project": len(dim_project),
        "dim_work_item": len(dim_work_item),
        "dim_status": len(dim_status),
        "dim_contractor": len(dim_contractor),
        "fact_status_event": len(fact_status_event),
        "project_progress_summary": len(project_summary),
        "contractor_performance_summary": len(contractor_summary),
        "monthly_progress_summary": len(monthly_summary),
    }

    latest_counts = fact_status_event.groupby("WorkItemID")["IsLatestStatus"].sum()
    checks = [
        check(not dim_project["ProjectID"].isna().any(), "Project primary keys", "ProjectID has no null values."),
        check(not dim_work_item["WorkItemID"].isna().any(), "Work item primary keys", "WorkItemID has no null values."),
        check(not fact_status_event["StatusEventID"].isna().any(), "Event primary keys", "StatusEventID has no null values."),
        check(dim_project["ProjectID"].is_unique, "Project key uniqueness", "ProjectID is unique."),
        check(dim_work_item["WorkItemID"].is_unique, "Work item key uniqueness", "WorkItemID is unique."),
        check(fact_status_event["StatusEventID"].is_unique, "Event key uniqueness", "StatusEventID is unique."),
        check(
            set(dim_work_item["ProjectID"]).issubset(set(dim_project["ProjectID"])),
            "Work item project relationship",
            "Every work item ProjectID exists in dim_project.",
        ),
        check(
            set(fact_status_event["WorkItemID"]).issubset(set(dim_work_item["WorkItemID"])),
            "Event work item relationship",
            "Every event WorkItemID exists in dim_work_item.",
        ),
        check(
            set(fact_status_event["StatusID"]).issubset(set(dim_status["StatusID"])),
            "Event status relationship",
            "Every event StatusID exists in dim_status.",
        ),
        check(
            set(fact_status_event["ContractorID"]).issubset(set(dim_contractor["ContractorID"])),
            "Event contractor relationship",
            "Every event ContractorID exists in dim_contractor.",
        ),
        check(
            bool((latest_counts == 1).all()) and len(latest_counts) == len(dim_work_item),
            "Latest event flag",
            "Every work item has exactly one latest status event.",
        ),
        check(
            row_counts["project_progress_summary"] == row_counts["dim_project"],
            "Gold project summary grain",
            "Project progress summary is one row per project.",
        ),
    ]

    failed = [row for row in checks if row["Result"] != "PASS"]
    status = "PASS" if not failed else "FAIL"
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    health_rows = [
        {"Metric": "ValidationStatus", "Value": status},
        {"Metric": "FailedChecks", "Value": len(failed)},
        {"Metric": "TotalChecks", "Value": len(checks)},
        {"Metric": "Projects", "Value": row_counts["dim_project"]},
        {"Metric": "WorkItems", "Value": row_counts["dim_work_item"]},
        {"Metric": "StatusEvents", "Value": row_counts["fact_status_event"]},
        {"Metric": "Contractors", "Value": row_counts["dim_contractor"]},
        {"Metric": "MonthlySummaryRows", "Value": row_counts["monthly_progress_summary"]},
    ]
    pd.DataFrame(health_rows).to_csv(GOLD / "pipeline_health_summary.csv", index=False)

    lines = [
        "# Validation Report",
        "",
        f"Generated: {generated_at}",
        "",
        f"Overall status: **{status}**",
        "",
        "## Dataset Row Counts",
        "",
        "| Table | Rows |",
        "| --- | ---: |",
    ]
    lines.extend(f"| `{name}` | {count:,} |" for name, count in row_counts.items())
    lines.extend(
        [
            "",
            "## Quality Checks",
            "",
            "| Check | Result | Detail |",
            "| --- | --- | --- |",
        ]
    )
    lines.extend(f"| {row['Check']} | {row['Result']} | {row['Detail']} |" for row in checks)
    lines.extend(
        [
            "",
            "## Why This Matters",
            "",
            "This report gives reviewers a quick way to verify that the portfolio pipeline produces consistent, analytics-ready outputs without using private employer data.",
            "",
            "The same validation pattern can be used for operational reporting pipelines before publishing data into Power BI or other BI tools.",
        ]
    )

    (DOCS / "validation-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Validation status: {status}")
    print("Wrote docs/validation-report.md")
    print("Wrote data/gold/pipeline_health_summary.csv")


if __name__ == "__main__":
    main()
