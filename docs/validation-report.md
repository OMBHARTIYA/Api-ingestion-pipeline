# Validation Report

Generated: 2026-07-07 14:32 UTC

Overall status: **PASS**

## Dataset Row Counts

| Table | Rows |
| --- | ---: |
| `dim_project` | 5 |
| `dim_work_item` | 7,500 |
| `dim_status` | 8 |
| `dim_contractor` | 20 |
| `fact_status_event` | 45,194 |
| `project_progress_summary` | 5 |
| `contractor_performance_summary` | 20 |
| `monthly_progress_summary` | 66 |

## Quality Checks

| Check | Result | Detail |
| --- | --- | --- |
| Project primary keys | PASS | ProjectID has no null values. |
| Work item primary keys | PASS | WorkItemID has no null values. |
| Event primary keys | PASS | StatusEventID has no null values. |
| Project key uniqueness | PASS | ProjectID is unique. |
| Work item key uniqueness | PASS | WorkItemID is unique. |
| Event key uniqueness | PASS | StatusEventID is unique. |
| Work item project relationship | PASS | Every work item ProjectID exists in dim_project. |
| Event work item relationship | PASS | Every event WorkItemID exists in dim_work_item. |
| Event status relationship | PASS | Every event StatusID exists in dim_status. |
| Event contractor relationship | PASS | Every event ContractorID exists in dim_contractor. |
| Latest event flag | PASS | Every work item has exactly one latest status event. |
| Gold project summary grain | PASS | Project progress summary is one row per project. |

## Why This Matters

This report gives reviewers a quick way to verify that the portfolio pipeline produces consistent, analytics-ready outputs without using private employer data.

The same validation pattern can be used for operational reporting pipelines before publishing data into Power BI or other BI tools.
