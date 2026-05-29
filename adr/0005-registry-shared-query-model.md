# ADR-0005: Registry Shared Query Model and POST /explore Endpoint

## Status
Accepted

## Context
Based on the feedback from huggingface and others, the Working Group recognized the need for "Registry Introspection" to allow autonomous clients to explore registry statistics, facet allocations, and capability distribution seamlessly.

Additionally, to ensure strong programmatic developer ergonomics and prevent namespace collisions (where dynamic pre-filter values could pollute protocol reserved keywords), we had to unify the query schemas used for both dynamic search and registry exploration.

## Decision
We formalized and accepted the following specification updates in version 0.5.0:

1. **The Shared Query Model (Lifting the Query Envelope)**:
   * We abstracted and extracted the `query` object into an authoritative, shared structural block referenced identical semantics across both `POST /search` and `POST /explore`.
   * The query block enforces a Wrapped `"filter": { ... }` object schema, isolating metadata filters and protecting reserved protocol keywords (such as `text` or `federation`).
   * Backwards-compatible flat keys (`type`, `compliance`, `publisher`) were retained as primary developer shorthands alongside dynamic dot-notation JSON paths for Schema.org and `metadata.*` filtering.

2. **The Introduction of the Optional `/explore` Endpoint**:
   * Introduced `POST /explore` to process dynamic facet aggregations over filtered subsets, improving orchestrator planning and reducing blind server relevance-scoring load.
   * Mandated that registries omitting implementation fallback to a standard `501 Not Implemented` HTTP status code.

## Consequences
* **Clean OpenAPI Stubs**: Programmatic clients utilizing code generators (OpenAPI, TypeScript, Pydantic) receive a fully isolated, strictly-typed query namespace for both endpoints.
* **Unified Parsing Middleware**: Registry implementations utilize a single, pre-filtered database engine to resolve constraints for both dynamic search and aggregation operations.
* **Federation Sovereignty**: `/explore` operations are explicitly isolated locally and forbidden from upstream federation to maintain data integrity across disparate database indexes.
