# Architecture

This project uses a synthetic architecture that mirrors a modern ingestion pipeline without connecting to a real service.

## Flow

`Synthetic API source -> Raw JSON -> Bronze CSV -> Silver model -> Gold summaries -> Power BI`

## Components

- Synthetic API source: `scripts/generate_synthetic_api_data.py` creates deterministic JSON payloads that mimic REST responses.
- Raw layer: `data/raw/` stores the generated payloads in source-like JSON format.
- Bronze layer: `scripts/transform_bronze.py` flattens the raw payloads into normalized CSV files in `data/bronze/`.
- Silver layer: `scripts/transform_silver.py` cleans data types, applies validation rules, and creates analytics-ready dimensions and fact tables in `data/silver/`.
- Gold layer: `scripts/build_gold_summary.py` aggregates the silver model into reporting-friendly summaries in `data/gold/`.
- BI layer: Power BI can import the silver and gold CSV outputs directly for dashboard creation.

## Production-Control Blueprint

The local runner demonstrates the data layers. The companion
[incremental refresh pattern](./incremental-refresh-pattern.md) documents the
delivery-informed control plane for a scheduled Microsoft Fabric implementation:

```text
Single-row watermark
    -> freeze one run window
    -> paginated API extraction
    -> run-isolated raw files
    -> transform, validate, and publish
    -> archive raw evidence
    -> commit watermark after all branches succeed
```

The data plane and control plane have separate responsibilities:

- The data plane extracts, lands, transforms, and publishes records.
- The control plane owns run boundaries, pagination state, dependencies,
  retries, validation gates, archival order, notifications, and recovery.
- The success boundary never advances on a partial run.
- Retries reuse the uncommitted window and remain safe through deterministic
  deduplication or key-based merge logic.

## Design Notes

- The project uses a fixed random seed for reproducibility.
- Status events simulate event history and current-state tracking.
- The silver model is intentionally simple and portfolio-friendly, centered around one fact table and supporting dimensions.
- Logging and validation are included in each step to demonstrate pipeline observability.
- Documentation derived from private delivery experience is rewritten as a
  vendor-neutral clean-room pattern; deployment identifiers and internal
  implementation details are intentionally excluded.
