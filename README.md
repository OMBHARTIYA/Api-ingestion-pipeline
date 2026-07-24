# API Ingestion Pipeline

This repository combines two forms of public proof:

1. a runnable local raw-to-gold pipeline using deterministic generated data
2. a syntheticized reconstruction of a Microsoft Fabric API ingestion
   operating design I authored for scheduled construction-data delivery

The sample records are generated. The documented orchestration, pagination,
state, PySpark curation, raw-file lifecycle, validation, and recovery design
comes from real delivery work rather than an invented portfolio architecture.

No real API, organization, project, production environment, source name, or
confidential implementation value is included.

## Reviewer Value

This repo is designed to show both implementation and operating judgment:

- land nested JSON-style source payloads in a raw layer
- normalize source records into bronze CSV tables
- build silver fact and dimension outputs for reporting
- produce gold summaries for Power BI consumption
- run row-count, key, status, and latest-event validation checks
- orchestrate incremental streams and reference snapshots in Microsoft Fabric
- freeze one extraction window across every paginated request
- isolate raw evidence by run and archive it before cleanup
- curate nested payloads with PySpark and publish Delta outputs
- commit pipeline state only after all required branches and quality gates pass
- replay a failed window without losing or duplicating its logical changes
- identify hardening needs around state selection, stale pages, failure
  visibility, empty windows, request efficiency, concurrency, and Delta scale

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
│   ├── generate_synthetic_api_data.py
│   ├── ingest_raw.py
│   ├── transform_bronze.py
│   ├── transform_silver.py
│   ├── build_gold_summary.py
│   └── pipeline_utils.py
├── docs/
│   ├── architecture.md
│   ├── data-dictionary.md
│   ├── incremental-refresh-pattern.md
│   ├── pipeline-flow.md
│   └── power-bi-model.md
└── notebooks/
    └── exploratory_validation.ipynb
```

## Synthetic Entities

- `projects`: 5 synthetic projects
- `work_items`: 7,500 synthetic work items
- `status_events`: deterministic high-volume status history records
- `contractors`: 20 synthetic contractors
- `dim_status`: 8 generic workflow statuses

## Pipeline Flow

```text
Synthetic API Source
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

## Microsoft Fabric Operating Case Study

The detailed
[Microsoft Fabric operating case study](./docs/incremental-refresh-pattern.md)
reconstructs the authored delivery design with synthetic public labels:

- workload matrix for incremental streams and supporting snapshots
- pipeline state contract and frozen-window semantics
- end-to-end orchestration and dependency sequence
- pagination state machine and single-request hardening
- run-isolated OneLake-style landing and archive lifecycle
- PySpark key-replacement logic and Delta `MERGE` scale path
- empty-window, validation, alerting, failure, and replay contracts
- prioritized findings from the structural operating review

This is a reconstruction, not a production export. The public labels cannot be
used to infer a private endpoint, environment, artifact, or identifier.

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the pipeline:

```bash
python scripts/run_pipeline.py
```

The full runner regenerates raw, bronze, silver, and gold outputs, then writes a validation report.

You can also run the individual steps manually:

```bash
python scripts/generate_synthetic_api_data.py
python scripts/ingest_raw.py
python scripts/transform_bronze.py
python scripts/transform_silver.py
python scripts/build_gold_summary.py
python scripts/write_validation_report.py
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
- `data/gold/pipeline_health_summary.csv`

## Proof for Reviewers

- [Validation report](./docs/validation-report.md): row counts, key checks, relationship checks, latest-event checks, and gold-output checks.
- [Pipeline flow](./docs/pipeline-flow.md): how raw JSON becomes reporting-ready CSV outputs.
- [Power BI model](./docs/power-bi-model.md): suggested star-schema layout for BI reporting.
- [Microsoft Fabric operating case study](./docs/incremental-refresh-pattern.md): the real control-plane design, syntheticized for safe public review.

## Power BI Modeling

Load the silver and gold CSV files into Power BI Desktop and relate them through `ProjectID`, `WorkItemID`, `StatusID`, and `ContractorID`. See `docs/power-bi-model.md` for the recommended star-schema layout.

## Safety Note

All repository data is synthetic. The operating workflow is reconstructed from
design work I authored, but every organization, source product, endpoint,
credential, project or tenant identifier, workspace, lakehouse, warehouse,
storage or connection identifier, internal artifact name, production schema or
path, source record, screenshot, run history, and exported definition is
excluded or replaced.
