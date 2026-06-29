# Power BI Model

## Recommended Imports

Import these CSV files into Power BI Desktop:

- `data/silver/dim_project.csv`
- `data/silver/dim_work_item.csv`
- `data/silver/dim_status.csv`
- `data/silver/dim_contractor.csv`
- `data/silver/fact_status_event.csv`
- `data/gold/project_progress_summary.csv`
- `data/gold/contractor_performance_summary.csv`
- `data/gold/monthly_progress_summary.csv`

## Recommended Relationships

- `dim_project[ProjectID]` one-to-many `dim_work_item[ProjectID]`
- `dim_project[ProjectID]` one-to-many `fact_status_event[ProjectID]`
- `dim_work_item[WorkItemID]` one-to-many `fact_status_event[WorkItemID]`
- `dim_status[StatusID]` one-to-many `fact_status_event[StatusID]`
- `dim_contractor[ContractorID]` one-to-many `fact_status_event[ContractorID]`

## Suggested Report Pages

- Executive overview
- Project progress summary
- Contractor performance
- Monthly event movement
- Data quality validation

## Modeling Tips

- Hide technical columns that are not useful for reporting, such as comments if you want a cleaner model.
- Mark `EventDate` as a date field and create a calendar table if time-intelligence measures are needed.
- Use the gold tables for quick summaries and the silver model for drill-through analysis.
