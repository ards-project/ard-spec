# ADR-0010: Direct ARD Entry Lookup by Identifier

## Status

Proposed

## Context

ARD identifiers are stable, globally unique primary keys, but the Registry API previously offered only semantic Search and optional deterministic List operations. Search requires natural-language input and adds ranking metadata. List returns a paginated collection and does not define canonical exact-identifier semantics. Neither operation lets a client efficiently resolve an identifier retained from earlier discovery.

The lookup operation also needs a clear federation boundary. Automatically forwarding a primary-key lookup would make latency and authority unpredictable, while returning a Search result would expose fields that are not part of the complete ARD entry.

## Decision

Agent Registries expose mandatory `GET /agents/{identifier}` lookup.

The complete identifier is UTF-8 percent-encoded as one path segment. A registry decodes it exactly once, validates the decoded ARD identifier, and performs an exact, case-sensitive lookup against its local index. The registry does not query upstream registries for this operation. Entries ingested from external publishers remain eligible because they are part of the local index.

A successful lookup returns the complete ARD entry without Search-only fields. Malformed identifiers return `400 INVALID_ARGUMENT`; valid identifiers absent from the local index return `404 NOT_FOUND`. The endpoint follows the deployment's existing Registry authentication policy and standard HTTP caching semantics.

## Consequences

- Clients can resolve a retained ARD identifier in one deterministic request.
- OpenAPI clients receive a typed identifier parameter and `ArdEntry` response.
- Registries need an indexed exact-match route in addition to semantic Search.
- Clients retaining federated Search results should retain `source` with the identifier and use it to resolve the entry at its originating registry.
- Conformance testing verifies encoded success, malformed identifiers, and unknown identifiers.
