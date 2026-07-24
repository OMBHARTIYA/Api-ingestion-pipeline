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

## Microsoft Fabric Control Plane

The local runner demonstrates the data layers. The companion
[operating case study](./incremental-refresh-pattern.md) reconstructs the
scheduled Microsoft Fabric control plane I authored, using only synthetic
public labels:

```text
Read exactly one state row
    -> capture one run-end boundary
    -> persist the active, uncommitted boundary
    -> run incremental and reference branches
    -> paginate incremental streams to an explicit terminal signal
    -> land pages in a run-specific raw location
    -> flatten, type, deduplicate, and publish curated Delta outputs
    -> reconcile pages, rows, keys, schema, time, and freshness
    -> archive raw evidence before working-file cleanup
    -> commit the active boundary only after every required branch succeeds
```

The data plane and control plane have separate responsibilities:

- The data plane extracts, lands, transforms, and publishes records.
- The control plane owns run boundaries, pagination state, dependencies,
  retries, validation gates, archival order, notifications, and recovery.
- The success boundary never advances on a partial run.
- Retries reuse the uncommitted window and remain safe through deterministic
  deduplication and key-based replacement or merge logic.
- Required snapshot branches join the same success gate as the incremental
  streams when their outputs are part of the reporting contract.
- Pipeline-level failure handling records the unchanged window and first failed
  activity even when the final state activity is never reached.

## Design Notes

- The project uses a fixed random seed for reproducibility.
- Status events simulate event history and current-state tracking.
- The silver model is intentionally simple and portfolio-friendly, centered around one fact table and supporting dimensions.
- Logging and validation are included in each step to demonstrate pipeline observability.
- The operating case study preserves the real workflow and review findings but
  replaces or omits every organization, source, project, environment, artifact,
  connection, schema, path, credential, record, and deployment identifier.
