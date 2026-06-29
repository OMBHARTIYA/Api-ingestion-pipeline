# API Ingestion Pipeline

This repository is a portfolio-safe synthetic API ingestion pipeline case study. I built this synthetic API ingestion pipeline to demonstrate how operational data can be extracted, normalized, transformed, validated, and prepared for analytics reporting.

No real API, company, client, employer, production environment, or confidential implementation detail is included. The full workflow runs locally using deterministic fake data generated from scratch.

## What the Project Covers

- Synthetic REST-style source payload generation
- Raw JSON landing files
- Bronze-layer normalization to flat CSV tables
- Silver-layer cleaning, type casting, and fact/dimension modeling
- Gold-layer summary tables for reporting
- Logging, row-count validation, and basic data quality checks
- Power BI-ready CSV outputs

## Repository Structure

```text
api-ingestion-pipeline/
├── README.md
├── .gitignore
├── requirements.txt
├── config/
│   └── sample_config.json
├── data/
│   ├── raw/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── scripts/
│   ├── generate_fake_api_data.py
│   ├── ingest_raw.py
│   ├── transform_bronze.py
│   ├── transform_silver.py
│   ├── build_gold_summary.py
│   └── pipeline_utils.py
├── docs/
│   ├── architecture.md
│   ├── data-dictionary.md
│   ├── pipeline-flow.md
│   └── power-bi-model.md
└── notebooks/
    └── exploratory_validation.ipynb
```

## Synthetic Entities

- `projects`: 5 fake projects
- `work_items`: 7,500 fake work items
- `status_events`: deterministic high-volume status history records
- `contractors`: 20 fake contractors
- `dim_status`: 8 generic workflow statuses

## Pipeline Flow

```text
Fake API Source
    ->
Raw JSON
    ->
Bronze CSV
    ->
Silver Fact and Dimensions
    ->
Gold Summaries
    ->
Power BI
```

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the pipeline:

```bash
python scripts/generate_fake_api_data.py
python scripts/ingest_raw.py
python scripts/transform_bronze.py
python scripts/transform_silver.py
python scripts/build_gold_summary.py
```

## Data Quality Checks

The pipeline enforces these checks during the silver transformation step:

- No null primary keys
- Foreign keys must exist
- Event dates must be valid
- Status values must match allowed statuses
- Latest event per work item can be identified
- Row counts are logged after each pipeline step

## Gold Outputs

- `data/gold/project_progress_summary.csv`
- `data/gold/contractor_performance_summary.csv`
- `data/gold/monthly_progress_summary.csv`

## Power BI Modeling

Load the silver and gold CSV files into Power BI Desktop and relate them through `ProjectID`, `WorkItemID`, `StatusID`, and `ContractorID`. See `docs/power-bi-model.md` for the recommended star-schema layout.

## Safety Note

All data in this repository is synthetic. No real company, client, API endpoint, credential, source system, BIM/model data, or operational data is included.
