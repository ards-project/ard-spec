# ADR-0012: Entry Versions

## Status
Proposed

## Context
ARD lists `version` among an entry's descriptive terms (§4.2) and names it as a core filter key (§5.3.1), and says
nothing else about it. Nothing says whether two entries may share an identifier, which version a search returns, or how
List treats several versions. §4.2 calls `identifier` a "Globally unique discovery handle", which read literally allows
one entry per identifier and so no version history at all. ARD's bundled `ai-catalog.schema.json` describes `version`
as a "Semantic version of the capability" while `ard-entry.schema.json` calls it the "Version of the artifact" with no
format.

AI Catalog has settled most of this in the v0.9 release candidate
([`specification/ai-catalog.md`](https://github.com/Agent-Card/ai-catalog/blob/19208af/specification/ai-catalog.md) at
19208af):

- **Multi-Version Entries.** A catalog MAY list several entries with the same `identifier` and different `version`
  values. `(identifier, version)` MUST be unique within the catalog, and when `version` is absent `identifier` alone
  MUST be unique. A client that wants the latest sorts by `version` when it parses as a semantic version, otherwise by
  `updatedAt`.
- **Resolving an Artifact's Version.** The version is the entry's `version`, then the referenced artifact's own version,
  then none. The entry's `version` wins when the two disagree. A registry resolves it once at ingestion and does not
  fetch artifacts at render time to do it.

An ARD registry ingests AI Catalog documents ([ADR-0010](0010-ard-and-ai-catalog-loose-coupling.md): an ARD entry is
the AI Catalog entry core plus namespaced terms), so a multi-version AI Catalog document either passes through ARD with
the same meaning or ARD has to invent one. What AI Catalog leaves to the client, picking the latest, ARD has to decide
on the registry side, because Search returns a ranked page and a client can't sort versions it was never sent.

This is gap G9 in [issue 117](https://github.com/ards-project/ard-spec/issues/117).

## Decision
ARD adopts AI Catalog's version rules and adds the registry-side selection AI Catalog leaves open. The rules are in a new
§4.6.

1. **Uniqueness.** Within one document, `(identifier, version)` is unique, and an entry without `version` is the only
   entry with its identifier. `identifier` SHOULD stay the same across versions. Both compare as exact strings, so
   `1.0` and `1.0.0` are two versions. §4.2 stops calling `identifier` globally unique and says it names one entry
   together with `version`.
2. **Resolution.** A registry resolves each entry's version at ingestion in AI Catalog's order, and the entry's
   `version` wins a disagreement with the artifact's.
3. **Latest.** A registry orders the versions of an identifier over every entry it holds for it, and the latest in
   any subset, such as the entries a query's `filter` keeps, is the highest in that order. If every entry the registry
   holds for the identifier has a resolved version that is a valid Semantic Versioning 2.0.0 string, the order is SemVer
   precedence, so build metadata is ignored and a pre-release
   precedes its release. Otherwise the order is `updatedAt`, which decides only if every entry has an RFC 3339
   date-time with a UTC offset. Where neither decides, for example `1.0.0+a` and `1.0.0+b` or two equal instants, the
   registry picks one and SHOULD pick the same one each time.
4. **Search.** Unless `filter` has a `version` key, the registry applies `filter`, keeps the latest version of each
   identifier among the entries that satisfy it, and then applies `text` and relevance. A `version` filter matches the
   resolved version and puts every matching version in the set. A result MUST carry its resolved `version` when it has
   one, and `updatedAt` when the entry has one. In `auto` federation, unless `filter` has a
   `version` key, the merging registry applies the same selection to its own results and the results it received
   together, and under a `version` filter it keeps one result per `(identifier, version)`.
5. **Explore.** Facets count Search's matched set, so each identifier once unless `filter` has a `version` key.
6. **List.** List returns one item per version and selects no latest, `total` counts versions, and an item MUST carry
   its resolved `version` when it has one.
7. **Schemas and tooling.** The `version` descriptions in `ard-entry.schema.json` and `ai-catalog.schema.json` say the
   same thing and point at §4.6. The conformance tool reports a duplicate `(identifier, version)` or a versionless
   identifier that appears twice as an error, and versions of one identifier that can't be ordered, ties included, as a
   warning.

The selection in item 3 is one reading of AI Catalog's "by `version` (when parseable as a semantic version) or by
`updatedAt`". AI Catalog doesn't say what happens when only some versions of an identifier parse. Ordering by SemVer only
when all of them parse keeps one comparison per identifier, because SemVer precedence and `updatedAt` can't be compared
with each other. Choosing the comparison over the identifier's full set, before any `filter`, keeps a query from
changing which of two versions is later, and lets a registry compute the order for an identifier when one of its entries is ingested, not per query.

### Alternatives considered
- **Latest per `(identifier, type)`.** Issue 117 phrased the ask this way. It differs from per-identifier selection
  whenever one identifier carries entries of more than one `type`, for example an A2A card at `2.0.0` and an MCP card
  at `1.4.2`, which AI Catalog's uniqueness rule allows. Per-identifier selection returns only the A2A card unless the
  query filters on `type`, and per-`(identifier, type)` returns both. Per-identifier matches AI Catalog's client rule,
  which sorts every entry sharing an identifier whatever its `type`, and because `filter` applies before selection a
  `type` filter still finds the MCP card. Whether the entry key should include `type` is a separate gap that 117
  doesn't list, and this rule changes with it if it lands.
- **Select the latest before applying `filter`.** A query filtering on `type` or `capabilities` would then miss an
  identifier whose latest version doesn't satisfy the filter while an earlier one does, so a client asking for the MCP
  card above would get nothing.
- **Rank every version and return the best match.** Search would return whichever version matched `text` best, which
  can be an old one, and the client would have to ask again to find the current version. Selecting first means a
  client gets the version it would call.
- **Return every version from Search and let the client sort.** This is AI Catalog's client-side rule. A page of ten
  results could hold four versions of one agent, and a client can't sort versions that fell on another page.
- **Select a latest in List.** List is ARD's enumeration, and returning every version is the one place a client can see
  version history without knowing the versions in advance.

## Consequences
- **Same version validity as AI Catalog.** ARD's version rules accept every multi-version layout AI Catalog accepts,
  and a document AI Catalog rejects for a duplicate `(identifier, version)` also fails ARD's conformance tool. When only some versions of an
  identifier are SemVer, AI Catalog doesn't define the latest, and ARD's `updatedAt` order can pick a different entry
  than a client that sorts the parseable versions.
- **One agent, several protocols.** A publisher listing an A2A card and an MCP card under one identifier and one version
  now fails conformance. Until the entry-key gap is settled it gives each card its own identifier. Giving the cards
  different versions passes conformance but hides the lower-versioned card from any Search that doesn't filter on
  `type` or `version`.
- **Results carry `version` and `updatedAt`.** A Search result MUST now carry the resolved `version` and the entry's
  `updatedAt` when they exist, where before only `identifier` was required, so a merging registry can order what it
  receives.
- **Federated selection is per response.** A merging registry runs the selection over the results its upstreams
  returned together with its own selected results, and chooses SemVer or `updatedAt` from that combined set, so its order can differ from an upstream's. An
  upstream's later version that fell below that upstream's relevance cutoff, or sat on a page it didn't fetch, is not
  considered, so a merged response can return an earlier version than the latest an upstream holds.
- **Explore counts the default view.** A facet bucket counts each identifier's latest version, so it can be lower than
  the results Search returns when `filter` adds that bucket's value. An identifier with an A2A card at `2.0.0` and an
  MCP card at `1.4.2` adds nothing to the MCP `type` bucket, and a `type` filter on MCP still finds the `1.4.2` card.
- **Search result counts change.** A registry that indexed several versions under one identifier and returned all of
  them now returns one per identifier, so page contents and Explore counts drop by the number of earlier versions.
- **Pre-releases can be latest.** Under SemVer precedence `3.0.0-rc.1` is later than `2.1.0`. A publisher that doesn't
  want a pre-release returned by default leaves it out of its published documents until release. ARD defines no
  stable-only selection.
- **One non-SemVer version changes the order for all.** A single entry whose version isn't SemVer moves its identifier
  from SemVer precedence to `updatedAt`, which can change the latest version Search returns, for example a `1.0.1`
  backport published after `2.0.0` becomes the latest, and leaves every version unordered when any entry lacks
  `updatedAt`. Within one manifest the conformance tool warns when some versions of an identifier are SemVer and some
  aren't, and when the order is undecided.
- **Cross-document duplicates are unresolved.** Uniqueness holds within one document. A registry that ingests the same
  `(identifier, version)`, or a versionless entry and versioned ones, from different documents, for example a
  publisher's `ard.json` and an AI Catalog document that re-lists it, holds entries the pair can't tell apart, and ARD
  leaves reconciling them to the registry (§4.6). Search under a `version` filter and List return one entry per pair.
- **Resolution depends on ingestion.** Whether an entry without `version` has a resolved version depends on whether
  the registry fetched its artifact, so two registries can disagree on a `version` filter and on the order for its
  identifier.
- **Unordered versions are registry-defined.** Two versions that SemVer can't order, or entries without `updatedAt`,
  leave the choice to the registry, and two registries can return different entries for the same query.
