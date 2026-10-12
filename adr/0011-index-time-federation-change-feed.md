# ADR-0011: Index-Time Federation via a Change Feed of Identifiers

## Status

Proposed — tracks [Issue #96](https://github.com/ards-project/ard-spec/issues/96)

## Context

ARD v0.91 federates only at query time (§5.4). A registry fans a search out to every upstream and merges the results (`auto`), or refers the client to the upstreams (`referrals`). Latency is the slowest upstream's; a complete answer needs every upstream to respond, and nothing marks a partial one; `score` values from different registries share no scale, so hubs merge by rank (#87); every query costs N upstream queries; and Explore never federates (§5.3.3). In the field, each of the four public registries probed in #88 answered `auto` from its own catalogue.

Nothing in v0.91 lets a registry learn what another registry holds before a query arrives. Crawling (§5.2) gives a registry one index of its own, but a crawler cannot know which publisher domains exist or when they changed.

## Decision

Add one optional endpoint, `GET /changes` (§5.5): an ordered, cursor-driven, replayable feed of the identifiers a registry added, updated, or removed, and nothing else.

- **Identifiers, not entries.** A change is `{cursor, op, time, identifier}`. A consumer that learns an identifier fetches the entry from the identifier's authority — for the domain-anchored identifier of Appendix C, the `<publisher>` domain resolved as §5.1 directs — and confirms every delete there. The feed says what exists and what changed; the authority says what the entry says.
- **Cursors are opaque** and compared for equality only. Delivery is at-least-once, latest change per identifier; a registry MAY compact superseded changes. A registry never issues a cursor it would reject.
- **The retention window contains the whole frontier.** A registry either retains changes indefinitely and never answers `410`, or re-emits an identifier's latest change before it ages out of the window. A consumer with no cursor therefore replays the window once and holds every live identifier, with no snapshot endpoint and no `410` mid-replay. A cursor older than the window receives `410 CURSOR_EXPIRED`, and the consumer replays into a staging set; the live index is never emptied.
- **Emit only what you ingested and admitted.** A registry emits a change only when its own index changed through its own ingestion — a crawl, a fetch induced by a feed, or another §5.2 pipeline — never because a peer reported an identifier. A consumer fetches on every `upsert`, since a change carries no digest; when the fetch returns what it already holds, nothing changes and nothing is emitted. Registries that subscribe to each other therefore converge without a hop list, and maintenance repeats do not propagate.
- **Deletes are hints.** A consumer confirms withdrawal at the authority and keeps the entry when the confirming fetch fails, so a delete cannot be timed to an outage.
- **Optional, with `501`**, as for Explore; a registry operated as an upstream for other registries SHOULD implement it. Subscribing to a feed is an operator decision, never automatic.

### Why identifiers and not entries

A peer's copy of an entry would need conflict resolution, a digest that survives the normalization registries apply on ingest (#87, #88), rules for which deletes to believe, a hop list, and a re-verification step that has nothing to check for the unsigned entries the specification allows. Carrying identifiers only leaves the authority as the sole source of content, keeps the trust rules identical to crawling (§4.5.1, §4.5.2), and makes a mesh of registries converge on set semantics.

### Alternatives considered

- **Query-time `auto` and `referrals` (today).** Kept unchanged; the feed composes with them, and `federation: none` keeps its meaning.
- **List with `updatedAfter` (Appendix A).** The closest existing mechanism, but it has no tombstones, its cursor is a publisher timestamp subject to clock skew, its payload is a peer's copy of the entry, and it was mostly unimplemented in the #88 sample.
- **A feed of full entries.** Rejected for the reasons above.
- **Push transports (WebSub, SSE, webhooks).** Deferred; each is a layer over the pull feed and adds callback or connection state that no implementer has yet asked for.
- **A shared transparency log or a DHT.** A governance problem or a stack requirement for ARD as a whole, though either is a valid producer behind this interface.

Prior art: DNS NOTIFY and IXFR (RFC 1996, RFC 1995), where a notification is a hint confirmed with and transferred from the primary; CouchDB `_changes`; sitemap pings.

### Deliberately excluded from this revision

Inline entries, `digest`, `origin`, a hop path, `reason`, server-side filters, push transports, publisher-served feeds, and a DNS record for the feed. Each returns only when a named implementer needs it. Identifier forms whose authority is not a publisher domain (content-addressed records, transparency-log registrations) are discussed in #96 and depend on the publisher-authority alignment definition tracked in #94; they are left to a follow-up.

## Consequences

- A registry can build one index from many upstreams and answer locally, which also gives Explore federation-wide coverage as a by-product of having one index.
- Producers need an append-only table of changes and tombstones with a retention policy. Consumers need a cursor store per upstream and a confirm-at-authority step, which reuses the §5.2 crawler.
- Appendix B gains `410 CURSOR_EXPIRED` and names `501 NOT_IMPLEMENTED`; the OpenAPI definition gains `/changes`; `spec/schemas/ard-change.schema.json` defines the page and change objects and `ard.cddl` restates them.
- Conformance tooling for producers and consumers is a separate follow-up PR.
- Open on the issue thread: the retention floor (the text proposes SHOULD `P7D`), and how long an entry outlives an authority that stays unreachable, which §5.2 does not answer for crawled entries either.
