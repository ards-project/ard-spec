# ADR-0004: Exclusion of Complex EBNF Filters and Sorting from the Search API

## Status
Accepted

## Context
During the design of the `POST /search` API in v0.4.2 of the Agent Finder specification, we debated whether to support a generic EBNF-style Boolean filter string (`filter`) and custom sort orders (`orderBy`) inside semantic search requests—similar to the deterministic `/agents` browsing endpoint.

The core architectural problem was:
1. **Relevance Score Integrity**: In semantic natural language search, the primary sorting vector is the dynamics-based relevance score (`score` 0-100). Sorting by metadata fields (e.g., `displayName` or `created_at DESC`) conflicts with and destroys relevance-based ranking, returning newer or alphabetical records that do not satisfy the semantic query intent.
2. **LLM and Client Ergonomics**: Asking simple HTTP clients or LLM orchestrators to generate complex EBNF Boolean logic strings (e.g., `"type = 'application/mcp-server-card+json' AND contains(description, 'translate')"`) inside search payloads is error-prone and prone to LLM parser hallucinations.
3. **Database Index Efficiency**: Parsing and executing complex arbitrary Boolean query strings on the fly inside high-concurrency semantic text and vector search queries adds severe computational overhead.

## Decision
We decided **NOT to include complex EBNF-style filters or custom sorting in the `POST /search` API**.

Instead, we enforce a strict architectural separation of concerns:
* **`POST /search` (Relevance-Driven)**: Dedicated strictly to semantic, natural-language queries where results are ordered exclusively by match score. To support necessary structural filtering (like filtering by protocol or publisher), we expose **explicit, flat JSON fields** in the `query` object (`type`, `compliance`, `publisher`).
* **`GET /agents` (Browse-Driven)**: Dedicated to deterministic SQL-like catalog browsing. This is the exclusive home of the EBNF `filter` string and metadata `orderBy` parameters, where exact Boolean logic applies and no relevance scores exist.

## Consequences
* **Optimized Index pre-filtering**: Registry implementations can map flat JSON filter keys directly to high-performance inverted database indexes before running semantic scoring, maintaining sub-millisecond search times.
* **Simplified Client Contracts**: Client applications and LLM prompts only need to generate simple, flat JSON key-value pairs to restrict search spaces, dramatically improving integration robustness.
* **Relevance Integrity**: Guarantees that search queries remain sorted by semantic alignment.
