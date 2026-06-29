# Data Dictionary

## Raw and Bronze Tables

### `projects_raw.json` and `projects_bronze.csv`

- `ProjectID`: Synthetic project identifier
- `ProjectName`: Generated project label
- `ClientName`: Fake client name
- `Country`: Generated country
- `City`: Generated city
- `ProjectType`: Generic project classification
- `StartDate`: Planned project start date
- `EndDate`: Planned project finish date
- `ProjectStatus`: High-level project lifecycle status

### `work_items_raw.json` and `work_items_bronze.csv`

- `WorkItemID`: Synthetic work item identifier
- `ProjectID`: Parent project identifier
- `WorkItemCode`: Project-scoped work item code
- `WorkItemName`: Generated work item label
- `WorkItemCategory`: Category such as Structure or Electrical
- `WorkItemType`: Item type such as Task or Milestone
- `PlannedStartDate`: Planned item start date
- `PlannedFinishDate`: Planned item finish date
- `Quantity`: Synthetic quantity value
- `UnitOfMeasure`: Generic unit label
- `Priority`: Priority flag
- `CurrentStatusID`: Current workflow status identifier

### `status_events_raw.json` and `status_events_bronze.csv`

- `StatusEventID`: Synthetic status-event identifier
- `WorkItemID`: Related work item identifier
- `ProjectID`: Related project identifier
- `StatusID`: Current status at the time of the event
- `EventDate`: Event date
- `EventDateTime`: Event timestamp
- `PreviousStatusID`: Prior workflow status
- `DaysInPreviousStatus`: Number of days spent in prior status
- `UpdatedBy`: Synthetic contractor identifier captured at the raw stage
- `SourceSystem`: Synthetic source-system name
- `Comment`: Fake free-text event comment
- `IsLatestStatus`: Boolean flag for the latest event on a work item

### `contractors_raw.json` and `contractors_bronze.csv`

- `ContractorID`: Synthetic contractor identifier
- `ContractorName`: Fake contractor name
- `ContractorType`: Generic contractor classification
- `Country`: Contractor country
- `City`: Contractor city
- `ActiveFlag`: Boolean activity flag

## Silver Tables

### `dim_project.csv`

- `ProjectID`
- `ProjectName`
- `ClientName`
- `Country`
- `City`
- `ProjectType`
- `StartDate`
- `EndDate`
- `ProjectStatus`

### `dim_work_item.csv`

- `WorkItemID`
- `ProjectID`
- `WorkItemCode`
- `WorkItemName`
- `WorkItemCategory`
- `WorkItemType`
- `PlannedStartDate`
- `PlannedFinishDate`
- `Quantity`
- `UnitOfMeasure`
- `Priority`
- `CurrentStatusID`

### `dim_status.csv`

- `StatusID`
- `StatusName`
- `ProgressWeight`

### `dim_contractor.csv`

- `ContractorID`
- `ContractorName`
- `ContractorType`
- `Country`
- `City`
- `ActiveFlag`

### `fact_status_event.csv`

- `StatusEventID`
- `WorkItemID`
- `ProjectID`
- `StatusID`
- `EventDate`
- `EventDateTime`
- `PreviousStatusID`
- `DaysInPreviousStatus`
- `SourceSystem`
- `Comment`
- `IsLatestStatus`
- `ContractorID`

## Gold Tables

### `project_progress_summary.csv`

- `ProjectID`
- `ProjectName`
- `TotalWorkItems`
- `CompletedWorkItems`
- `ApprovedWorkItems`
- `BlockedWorkItems`
- `CompletionPercent`
- `AverageProgressWeight`

### `contractor_performance_summary.csv`

- `ContractorID`
- `ContractorName`
- `TotalEvents`
- `CompletedEvents`
- `BlockedEvents`
- `ReworkEvents`

### `monthly_progress_summary.csv`

- `YearMonth`
- `ProjectID`
- `EventsCount`
- `CompletedCount`
- `ApprovedCount`
- `BlockedCount`
