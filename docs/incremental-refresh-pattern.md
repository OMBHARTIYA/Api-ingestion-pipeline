# Incremental Refresh and Pagination Pattern

This document captures the delivery controls I use when designing, reviewing,
and operating scheduled Microsoft Fabric ingestion pipelines. The public
example maps those controls to this repository's synthetic raw-to-gold
workflow. It is not a copy of a production pipeline, and it contains no real
project, tenant, workspace, storage, connection, endpoint, schema, table,
credential, or source-record value.

## Why the Control Plane Matters

Incremental extraction is reliable only when the pipeline can answer four
questions for every run:

1. What exact source window belongs to this run?
2. How do we know every page in that window was captured?
3. Can a failed window be replayed without duplicates or stale files?
4. When is it safe to advance the success boundary?

The safe answer is to freeze the window once, keep pagination state explicit,
isolate raw files per run, and commit the watermark only after all required
work succeeds.

## Reference Sequence

```text
Read one committed watermark row
    ->
Capture the run end boundary once
    ->
Persist the active run boundary
    ->
Extract each incremental branch with the same fixed window
    ->
Follow the API page pointer until its documented end signal
    ->
Write each page to a run-specific raw location
    ->
Flatten, type, deduplicate, and merge into curated tables
    ->
Run count, key, status, freshness, and schema checks
    ->
Archive raw evidence before working-file cleanup
    ->
Commit the active boundary as successful
    ->
Send a run summary
```

Full-snapshot reference branches may run beside the incremental branches, but
they must join the same final success gate if their outputs are required by the
reporting model.

## Failure-Safe Invariants

- The lower boundary comes from the last committed successful run.
- The upper boundary is captured once and reused by every page request.
- The API's inclusive or exclusive timestamp behavior is confirmed and
  documented before scheduling.
- The watermark lookup filters to exactly one pipeline record and fails on a
  missing or duplicate record.
- Page state starts from a known value and stops only on the API's documented
  terminal signal.
- Raw filenames are unique inside a run-specific folder.
- Working raw files are removed only after a retained archive exists.
- The success watermark advances only after extraction, transformation,
  validation, required snapshot branches, and raw-file lifecycle steps pass.
- A failed run leaves the committed lower boundary unchanged, so the same
  window can be replayed.
- Replays are idempotent through a deterministic business key and merge or
  replacement rule.

## Generic Pseudocode

```text
state = read_exactly_one_watermark(pipeline_key)
window_start = state.last_success
window_end = current_utc_boundary()
save_active_boundary(pipeline_key, window_end)

for dataset in incremental_datasets:
    page_pointer = dataset.first_page

    while page_pointer is not terminal:
        response = request_page(
            dataset=dataset,
            start=window_start,
            end=window_end,
            page=page_pointer,
            page_size=configured_page_size
        )
        write_raw_page(run_id, dataset, page_pointer, response.items)
        page_pointer = normalize_terminal_pointer(response.next_page)

publish_curated_outputs(run_id)
assert_required_quality_checks(run_id)
archive_raw_pages(run_id)
clean_working_pages(run_id)
commit_success_boundary(pipeline_key, window_end)
notify_run_summary(run_id)
```

## Validation Gates

Before the watermark commit, record and evaluate:

- source response count and raw page count by dataset
- raw, deduplicated, rejected, inserted, and updated row counts
- null and duplicate primary keys
- orphaned foreign keys
- allowed status or category values
- minimum and maximum event timestamps
- unexpected zero-row loads
- schema drift and required-column presence
- final-page termination evidence
- curated-table freshness

A quality failure should block the watermark commit and trigger the same
pipeline-level failure path as an extraction or transformation failure.

## Hardening Checklist

| Priority | Control | Reason |
| --- | --- | --- |
| High | Filter and enforce one watermark row | Prevents the wrong run state from being selected. |
| High | Use run-specific raw staging | Prevents stale pages from an interrupted run being processed later. |
| High | Add pipeline-level failure handling | Ensures failures before the final activity still generate an alert. |
| High | Normalize empty-response behavior | Makes a valid zero-row window complete predictably. |
| Medium | Promote source scope to runtime configuration | Avoids editing and republishing the definition for each scope. |
| Medium | Avoid separate metadata and payload calls per page | Reduces API traffic and response drift. |
| Medium | Lock or serialize watermark updates | Prevents overlapping runs from sharing active state. |
| Medium | Use an atomic Delta merge at scale | Improves write efficiency and replay safety. |
| Low | Standardize names and data types | Reduces operational ambiguity and maintenance cost. |
| Low | Persist quality metrics with the run record | Makes audit, support, and trend monitoring easier. |

## Safe Recovery

1. Keep the committed success boundary unchanged.
2. Record the failed run window and first failed activity.
3. Preserve the failed run's raw evidence.
4. Remove or quarantine only the known working folder for that run.
5. Replay the same window.
6. Compare source, raw, curated, and rejected counts.
7. Confirm archive creation, quality gates, and the final watermark commit.

Never advance the watermark manually unless the missing interval has been
independently reconciled.

## Public Repository Boundary

This repository demonstrates the pattern with deterministic synthetic data.
Production exports, live URLs, identifiers, connection metadata, credentials,
internal naming, real schemas, actual source records, screenshots, and run
history do not belong in this public repository.
