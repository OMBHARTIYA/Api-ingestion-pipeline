# Pipeline Flow

## `scripts/generate_fake_api_data.py`

- Loads the sample configuration and random seed
- Generates fake projects, contractors, work items, and status events
- Writes REST-style JSON payloads to `data/raw/`

## `scripts/ingest_raw.py`

- Simulates a raw ingestion step
- Reads each JSON payload from `data/raw/`
- Validates that the expected root entities exist
- Logs source record counts

## `scripts/transform_bronze.py`

- Reads the raw JSON payloads
- Uses `pandas.json_normalize` to flatten the records
- Writes normalized CSV outputs to `data/bronze/`

## `scripts/transform_silver.py`

- Reads bronze tables into pandas DataFrames
- Builds dimension and fact tables
- Type-casts event dates and boolean fields
- Runs data-quality checks for keys, dates, statuses, and latest-event logic
- Writes clean silver outputs to `data/silver/`

## `scripts/build_gold_summary.py`

- Reads the silver model
- Calculates project progress metrics
- Summarizes contractor event performance
- Aggregates monthly event progress by project
- Writes the results to `data/gold/`
