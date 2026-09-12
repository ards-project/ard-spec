# Agentic Resource Discovery Specification

**Federated Discovery and Search for Agentic Resources**

**Version**: v0.91
**Status**: Proposal
**Date**: August 26, 2026

**Authors**:

- Junjie Bu — Google
- R.V.Guha
- Shaun Smith — Hugging Face

## 1. Overview

LLMs increasingly rely on external capabilities — MCP tools, A2A agents, skills, and other callable services — to extend their functionality. In this document, we refer to these generically as agentic resources.

The **Agentic Resource Discovery Specification (ARD)** defines how agentic resources are described, discovered, and searched across federated networks.

This version (v0.91) restates the description layer in terms of JSON-LD and namespaces. An entry is a JSON-LD node whose terms come from a default namespace unless it declares otherwise. This is a repositioning, not a redefinition: existing manifests remain valid entries unchanged. What it adds is a `@context` seam, so an entry MAY draw terms from additional namespaces, and those terms become available to discovery without any change to this specification. Which namespaces beyond the default are recognized is left open and expected to grow over time; that evolution does not affect entries written today.

## 2. Motivation

The prevailing model requires users or developers to explicitly "install" or hardcode each agent before use. As the ecosystem scales to thousands or millions of agents, we need a model where LLMs can discover and invoke agents dynamically, similar to how search engines discover web pages.

Agent descriptions tend to be generic, and most LLMs currently select tools by including all descriptions in the context window — which does not scale. ARD addresses this by moving discovery outside the LLM into a dedicated search service, where richer signals (representative queries, publisher identity, compliance metadata, usage patterns) can be leveraged without consuming context window tokens.

Grounding the description layer in JSON-LD extends the same reasoning. A resource is described once, on its own domain; a discovery service indexes the terms it recognizes and preserves the rest; and a publisher can enrich an entry with domain-specific vocabulary without waiting for a revision of this specification.

## 3. Core Design Principles

ARD is guided by the following core design principles to ensure scalability, interoperability, and ease of adoption:

### 3.1 Search-First Discovery

Rather than requiring users or systems to pre-install agents (analogous to the mobile app store paradigm), ARD promotes a model where agents are discovered dynamically through search. Registries maintain a shared, continuously updated index, making capabilities discoverable the moment they are published.

### 3.2 Scalability Beyond Context Windows

Traditional tool selection relies on injecting all descriptions into the LLM's context window, which does not scale. ARD moves the selection problem outside the LLM into a dedicated search service, leveraging information retrieval techniques to scale to thousands or millions of capabilities without consuming context window tokens.

### 3.3 Artifact-Agnostic Envelope

The specification does not define or constrain the internal schema of specific agent types (MCP, A2A, etc.). Instead, it acts as a clean envelope that uses a `type` term (formatted as an IANA Media Type) to identify what an artifact is, delegating the definition of artifact-specific metadata to the respective protocol specifications.

> **[!NOTE] IANA Registration Status**: The types `application/a2a-agent-card+json` and `application/mcp-server-card+json` used in this specification are de-facto community standards tracking towards formal registration. Implementers should note that while well-known path directories (like `/.well-known/agent-card.json`) are officially registered permanent entries, full type registrations are pending working group joint submission and the format may change. In the meantime, omit strict verification of these types by intermediaries.

### 3.4 JSON-LD Entries and Namespaces

An entry is a JSON-LD node. Terms written plainly, without a prefix, belong to the default namespace — the same terms a manifest uses today, interpreted the same way. Through the entry's `@context`, a publisher MAY additionally draw terms from other namespaces to describe the resource. A consumer processes the terms it recognizes and preserves the others (§5.3.1). This keeps a single entry model while making the vocabulary open at the edges rather than closed.

### 3.5 Universal Baseline for Federation

To guarantee that any system can participate in discovery regardless of its execution stack, an Agent Registry **MUST** expose a standard HTTP REST search interface. While specialized protocols may be used for execution, discovery requires a universal baseline that any HTTP client can access.

### 3.6 Separation of Concerns

To maintain a clean and implementable standard, the protocol delegates operational details:

* **Authentication is Delegated**: Agent authentication is handled by the specific artifact protocol, not the discovery layer.
* **Distribution is Infrastructure**: Mechanisms for physical delivery (OCI, npm, etc.) are left to backend implementation and are not part of the discovery record.

## 4. The ARD Entry

The unit ARD describes, indexes, and returns is the **ARD entry** — the description of a single agentic resource in a form that can be found by search. ARD is defined over ARD entries; the container an entry travels in (a hosted manifest, a web page, an API response) is a transport concern, addressed in §5.

**This specification defines the ARD entry.** An ARD entry is not the same object as a catalog entry, and the two should not be conflated. A catalog entry is a publisher's listing of a resource: its obligation is to accommodate whatever the publisher wishes to describe, so it commits to as little as possible. An ARD entry is a description carrying the signals a search service requires in order to make resources comparable across publishers who have never coordinated: its obligation is to guarantee that those signals are present and uniformly addressable.

The two are related but distinct. ARD adopts the core terms of the default namespace (§4.2) and layers on the terms discovery depends on — chiefly `representativeQueries`, which an ARD entry is expected to carry. It follows that **every ARD entry is a well-formed catalog entry, but not every catalog entry is an ARD entry** — a listing that omits the discovery terms remains a perfectly valid catalog entry and is simply not discoverable through ARD. ARD keeps this expectation soft at the schema level: a missing or under-populated `representativeQueries` is flagged by conformance tooling as a warning, not a hard validation failure, so entries emitted by existing tooling still validate (§4.2).

Because the definitions are separate, each specification's conformance is self-contained: a change to what a catalog entry requires does not change what an ARD entry requires, and vice versa.

Within this specification, "entry" means "ARD entry" unless stated otherwise.

### 4.1 An ARD Entry Is a JSON-LD Node

An entry is a JSON-LD node describing an agentic resource. Its terms acquire meaning through the **ARD base context**, published at `https://agenticresourcediscovery.org/context/v1`, which maps the core terms to IRIs under the default namespace (`https://agenticresourcediscovery.org/ns#`).

A conforming consumer MUST expand an entry with the ARD base context as the initial expansion context (the JSON-LD `expandContext` option). An entry's own `@context`, when present, is applied after the base context: it MAY add or override namespaces but does not remove the base. Under this rule the core terms resolve to their IRIs and namespaced terms (e.g. `okf:taxonomy`) resolve through the prefixes the entry declares.

Carrying `@context` in the entry itself is OPTIONAL. An entry that omits it — including every entry published against the predecessor format — is interpreted by any consumer that applies the base context, and needs no changes. An entry SHOULD include `"@context": "https://agenticresourcediscovery.org/context/v1"` (optionally as the first element of an array whose later elements add local namespaces) when it may be read by generic JSON-LD tooling that has not been told to apply the base context — most importantly when embedded as in-page markup. The consequence is deliberate: an entry with no `@context` is interpretable only by a consumer that knows it is an ARD entry and applies the base context. That is the trade for terse authoring and backward compatibility.

### 4.2 Entry Terms

The default namespace supplies definitions for the terms below; ARD determines which of them an entry is required to carry. An ARD entry MUST carry:

| Term | Requirement | Notes |
| :--- | :--- | :--- |
| identifier | MUST | Globally unique discovery handle. Domain-anchored URN form (`urn:air:<publisher>:<namespace>:<agent-name>`); see Appendix C. The JSON-LD `@id` MAY mirror it. |
| displayName | MUST | Human-readable name. |
| type | MUST | Artifact type as an IANA Media Type (§3.3). |
| url _or_ data | MUST (exactly one) | Value-or-reference (§4.3). |

An ARD entry SHOULD additionally carry `representativeQueries`, and `capabilities` is recommended where it applies; these are the discovery signals, so they are described in full here rather than by reference.

| Term | Requirement | Description |
| :--- | :--- | :--- |
| representativeQueries | SHOULD | Sample natural-language queries a user might issue that this resource can serve — the signal a registry builds its semantic index from. An entry without it cannot be found by search, which is what distinguishes an ARD entry from a bare catalog entry. SHOULD contain 2–5 examples. It is not hard-required: the schema does not reject an entry that omits it or supplies a different count — the conformance tester flags those as warnings (§D.2), so output from existing tooling still validates. |
| capabilities | MAY | Short skill or tool tokens (e.g. `["WeatherTool"]`) enabling fast structured filtering without fetching the full artifact. |

The remaining terms are optional and descriptive.

| Term | Description |
| :--- | :--- |
| description, tags, version, updatedAt, metadata, trustManifest | Descriptive terms. `trustManifest` is discussed in §4.5; ARD does not constrain its internal schema beyond `identity`, but registries are expected to inspect and verify it. |

Terms from any additional namespace declared in the entry's `@context` MAY also appear and become available as filter dimensions (§5.3.1) with no change to this specification.

### 4.3 Value or Reference

An entry's artifact content is delivered by exactly one of two mutually exclusive terms — `url` (a reference to the artifact document) or `data` (the document inline). An entry MUST NOT carry both.

### 4.4 Examples

A plain entry — no `@context`, so its terms resolve to the default namespace:

```json
{
  "identifier": "urn:air:acme.com:server:weather",
  "displayName": "Weather Data Node",
  "type": "application/mcp-server-card+json",
  "url": "https://api.acme.com/mcp/weather.json",
  "capabilities": ["WeatherTool", "ForecastTool"],
  "description": "Enterprise weather MCP server for live telemetry.",
  "representativeQueries": [
    "what is the current wind speed in Chicago",
    "get the 5-day forecast for Seattle"
  ]
}
```

The same entry enriched with terms from an additional namespace via `@context`. Unprefixed terms remain in the default namespace; the prefixed terms (here, a publisher's own extension namespace) become filter dimensions:

```json
{
  "@context": {
    "acme": "https://acme.com/vocab#"
  },
  "identifier": "urn:air:acme.com:server:weather",
  "displayName": "Weather Data Node",
  "type": "application/mcp-server-card+json",
  "url": "https://api.acme.com/mcp/weather.json",
  "capabilities": ["WeatherTool", "ForecastTool"],
  "description": "Enterprise weather MCP server for live telemetry.",
  "representativeQueries": [
    "what is the current wind speed in Chicago",
    "get the 5-day forecast for Seattle"
  ],
  "acme:serviceTier": "enterprise",
  "acme:region": ["us-east", "eu-west"]
}
```

A skill entry from a solo developer, no trust ceremony required:

```json
{
  "identifier": "urn:air:github.com:alice-dev:pptx-creator",
  "displayName": "pptx-creator",
  "type": "application/ai-skill+md",
  "url": "https://github.com/alice-dev/pptx-creator",
  "description": "Create professional PowerPoint presentations following brand guidelines.",
  "representativeQueries": [
    "turn these bullet points into a branded slide deck",
    "make a PowerPoint from this outline"
  ]
}
```

### 4.5 Identity and Trust

Identity binding, compliance attestations, provenance, and cryptographic signatures are carried in the optional `trustManifest` term. This keeps the entry lightweight for simple use cases while providing a robust hook for enterprise compliance, separate from the artifact's native operational metadata. ARD requires only `trustManifest.identity`, for the binding rule in §4.5.1, and does not constrain the envelope's internal schema, so a trust manifest defined by any framework — SPIFFE, a DID method, an enterprise PKI — is structurally valid. This is agnosticism about the framework, not indifference to trust: a federated registry is expected to inspect the trust manifest and verify it according to the framework it declares (§4.5.2). Its attestations, provenance, and signature are inputs to verification and to trust-aware filtering and ranking — not a black box to be passed through unread.

#### 4.5.1 Publisher Authority Binding

The cryptographic trust domain asserted in `trustManifest.identity` MUST align with the `<publisher>` domain embedded in the entry's discovery identifier (Appendix C). This is ARD's defense against namespace squatting: an entry claiming `urn:air:google.com:...` is rejected by a verifying registry unless it can produce a verifiable attestation issued by `google.com`. The discovery identifier and the security principal are otherwise decoupled — the former is a stable searchable handle, the latter a dynamic cryptographic credential.

#### 4.5.2 Verification

ARD does not define a signing or verification procedure of its own. The signed payload, its canonicalization, signature processing, and key resolution are defined by the trust framework the manifest declares in `trustManifest.trustSchema` (through its `governanceUri` and `verificationMethods`). ARD mandates only the publisher-authority binding of §4.5.1; two implementations verifying the same manifest defer to the same declared framework. A future ARD profile MAY pin a concrete default scheme, but this specification does not. A federated registry SHOULD run the verification its declared framework specifies and MAY use the outcome in filtering, ranking, and admission decisions; a registry that passes an unverified trust manifest through untouched forfeits the trust the federation depends on.

A relevance score returned by Search (§5.3.2) reflects semantic relevance only and MUST NOT be interpreted as a trust, compliance, or safety judgment; trust evaluation is fully decoupled.

## 5. Discovery

Discovery is what ARD is fundamentally about, and it spans this entire section: how entries are published and ingested (§5.1–5.2), how a client searches the resulting index (the search API, §5.3), and how registries compose across a federation (§5.4). It operates in two layers:

1. **Static Discovery**: A decentralized publishing mechanism where developers and enterprises publish entries as static documents or in-page markup.
2. **Dynamic Discovery**: Active, searchable services (Registries) that index published entries and expose the dynamic search API.

### 5.1 Discovery Mechanisms

Publishers advertise entries via the following mechanisms. Each points a consumer at a source of entries; the entries themselves follow §4 regardless of how they are found.

* **Well-Known URI**: Hosting a manifest of entries at `https://{domain}/.well-known/ard.json`. The manifest is a JSON document with an `entries` array of ARD entries (§4); any other top-level members are transport-defined and ignored by ARD. Its shape is given by the `ardManifest` definition in the entry schema (Appendix D).
* **In-page markup**: Embedding entry JSON-LD in a web page describing the resource, discoverable by ordinary web crawling.
* **Agentmap Directive**: Adding an entry-source directive in `robots.txt` (e.g. `Agentmap: https://example.com/entries.json`).
* **HTML Link Tag**: Including `<link rel="ard" href="...">` in the `<head>` of a document.
* **DNS**: Publishing Service Binding records that point to either a static entry source (e.g. `_entries._agents.example.com`) or a dynamic Agent Registry search endpoint (e.g. `_search._agents.example.com`).

**Consumer resolution (normative).** A consumer resolving a domain's entries MUST fetch `/.well-known/ard.json`, and MUST honour a `rel="ard"` link. ARD's predecessor specified the path `/.well-known/ai-catalog.json` and the link relation `ai-catalog`; a consumer MAY additionally consult these, and a consumer that does treats them as equivalent entry sources. Consulting the predecessor names is a courtesy to resources published before this revision, not a conformance requirement: a consumer that resolves only `ard.json` and `rel="ard"` is fully conformant.

**Publishing (informative).** Publishers publish entries at `/.well-known/ard.json` and emit `rel="ard"`. There is no need to serve the predecessor path or relation as well; ARD defines one path, and a publisher serving it is discoverable by every conformant consumer. A resource that remains only at `/.well-known/ai-catalog.json` may not be found, since consulting that path is optional for consumers — a publisher on the predecessor path SHOULD move to `ard.json`.

### 5.2 Ingestion Pipelines

Agent Registry instances populate their indexes through ingestion pipelines:

* **Web Ingestion (Required)**: Crawling entry sources — hosted manifests and in-page markup — from discovered URIs. All ARD implementations MUST support this.
* **Additional Pipelines (Optional)**: Registries may support scanning git repositories, npm registries, or OCI registries as indicated by their configuration.

### 5.3 The Search API

The Registry API is the dynamic half of discovery. An Agent Registry **MUST** expose the standard HTTP REST Search (§5.3.2) and Retrieve (§5.3.4) interfaces. Search guarantees universal discovery and federation; Retrieve provides deterministic resolution of a known identifier. The operational base URL for these endpoints is discovered dynamically by identifying entries whose `type` is `application/ai-registry+json`.

#### 5.3.1 The Query Model

The `POST /search` and `POST /explore` endpoints accept a common `query` object with three members: `@context`, `text`, and `filter`. Each endpoint defines its own additional parameters alongside `query` (see §5.3.2 and §5.3.3) and its own presence requirements for `text` and `filter`.

```json
{
  "query": {
    "@context": { "okf": "https://openknowledgeformat.org/ns#" },
    "text": "find me a flight booking agent",
    "filter": {
      "type": ["application/a2a-agent-card+json"],
      "tags": ["finance"],
      "okf:taxonomy": ["us-gaap"],
      "trustManifest.attestations.type": ["SOC2-Type2"]
    }
  }
}
```

| Field | Type | Description |
| :--- | :--- | :--- |
| @context | Object/String | Optional. Binds the prefixes used in `filter` keys, exactly as an entry's `@context` binds the terms it carries. Layered on the ARD base context (§4.1); absent, only the base context applies. |
| text | String | Natural-language description of the need. Narrows the result set by semantic relevance. |
| filter | Object | Structured constraints. Keys are term paths; values are arrays (a bare scalar is accepted as a single-element array). |

`text` and `filter` compose: an entry is in the matched set if it satisfies the relevance criteria for `text` (when present) AND every constraint in `filter` (when present).

**Term resolution.** A filter key that names a term is resolved to its IRI through the query's effective context — the ARD base context plus the query's `@context` — and matched against entries by that IRI, not by the literal key string. This is what makes namespaced filtering work across publishers: a client filtering on `okf:taxonomy` matches any entry whose author bound the same namespace, regardless of the prefix that author chose (`okf:`, `openknowledge:`, …), because both sides resolve to the same IRI. Core terms (`type`, `tags`, `capabilities`, `version`, …) resolve through the base context and need no `@context`.

**Path segments into non-expanded members.** ARD does not expand `trustManifest`, `metadata`, or inline `data` into the JSON-LD graph (§4.1); dot-paths *into* them (e.g. `trustManifest.attestations.type`, `metadata.location`) are literal JSON paths on the raw member, not IRI-resolved. The leading segment is still an IRI-resolved term; the remainder is a literal path. (Not expanding a member is a statement about the graph, not about inspection — registries verify `trustManifest` per §4.5.2.)

**Filter Semantics**: When the value at a resolved key or path is an array, a constraint matches if any element satisfies it. Within a single key, values are combined with OR; across keys, with AND.

**Extensibility**: Any term an entry carries MAY be used as a filter key with no specification change — core terms, non-expanded-member paths, and any namespaced term the query binds in `@context`. A registry that indexes a term makes it filterable.

The `publisher` key is derived from the `<publisher>` segment of an entry's URN identifier (Appendix C), not a stored term; registries extract it.

**Registry Support**: Registries SHOULD support filtering on common standard terms; support for `metadata.*` and other extension terms is registry-defined. A registry MAY reject a filter that references an unsupported term path with a 400 error.

#### 5.3.2 Search (POST /search)

Accepts a `query` (§5.3.1) and returns entries ranked by relevance. For Search, `text` is required; `filter` is optional.

**Request Schema:**

```json
{
  "query": {
    "text": "find me a flight booking agent",
    "filter": {
      "type": ["application/a2a-agent-card+json"]
    }
  },
  "federation": "referrals",
  "pageSize": 5
}
```

In addition to the `query` object (§5.3.1), Search accepts:

| Field | Type | Description |
| :--- | :--- | :--- |
| federation | String | Optional. auto (default), referrals, or none. |
| pageSize | Integer | Optional (root-level). Max results to return per page (default: 10, max: 100). |
| pageToken | String | Optional (root-level). Pagination token to retrieve the next page. |

**Response Schema:**

The response returns entries with additional relevance scores, plus optional referrals. The `score` parameter denotes semantic relevance ranking (0–100) computed by the search registry, indicating how well the entry satisfies the natural language query. It is strictly an informational relevance metric and MUST NOT be interpreted by orchestrators as a cryptographic trust, compliance, or safety rating. Trust evaluation is fully decoupled and handled independently via the trust manifest (§4.5).

In a response, an entry MUST carry `identifier`; every other term is at the registry's discretion. A registry returns what is useful for selecting among results and MAY omit the rest — `representativeQueries` in particular serve indexing rather than presentation and are normally omitted. A result is therefore not necessarily a complete ARD entry (§4.2); its `identifier` names the authoritative one. Note that `url`, where present, addresses the artifact (an Agent Card, Server Card, and so on) — not the ARD entry that describes it. A client retrieves the complete entry from the result's `source` registry using `GET /agents/{identifier}` (§5.3.4).

```json
{
  "results": [
    {
      "identifier": "urn:air:acme.com:agent:assistant",
      "displayName": "Corporate Assistant (A2A)",
      "type": "application/a2a-agent-card+json",
      "url": "https://api.acme.com/agents/assistant.json",
      "score": 95,
      "source": "https://registry.acme.com/api/v1/"
    },
    {
      "identifier": "urn:air:example.com:weather-server",
      "displayName": "Global Weather Service",
      "type": "application/mcp-server-card+json",
      "url": "https://weather.example.com/mcp",
      "capabilities": ["WeatherTool"],
      "score": 88,
      "source": "https://finder.external.org/api/"
    }
  ],
  "referrals": [
    {
      "identifier": "urn:air:nlweb.ai:registry:public",
      "displayName": "Public Agent Finder",
      "type": "application/ai-registry+json",
      "url": "https://finder.nlweb.ai/search"
    }
  ],
  "pageToken": "eyJwYWdlIjogMn0="
}
```

##### 5.3.2.1 Query Processing and Resolution (Informative)

While this specification mandates the REST interface for interoperability, implementations may employ advanced techniques to resolve natural language queries to specific agent endpoints. An example flow, drawing from research on Agent Naming Services (ANS) and Federated Registries, involves the following steps:

1. **Semantic Translation & Embedding**:
   * **LLM Query Interpretation**: The Registry uses an LLM to extract specific multi-dimensional requirements from the natural language `text` field, translating it into structured capability attributes (e.g. domain: travel, skill: flight_booking, constraints: meal_preference).
   * **Vector Embeddings**: The Registry may also convert the query description into a dense vector embedding to understand semantic meaning (e.g. matching "foreign exchange" to "forex" or "international money transfer").
2. **Global Discovery via Federated Routing**:
   * Advanced implementations may execute this query against a federated network. For example, using semantic attributes or embedding vectors to perform a search across a Distributed Hash Table (DHT) (e.g. an extended IPFS Kademlia DHT) or by leveraging DNS-AID to discover authoritative registries for specific domains.
   * This maps the semantic capabilities to cryptographic digests or endpoints of agents that possess those skills across the federated network.

#### 5.3.3 Explore (POST /explore) — Optional

Accepts a `query` (§5.3.1) and returns an aggregation over the matched set rather than ranked entries. Explore lets clients introspect a registry — for example, "which artifact types are available?" — and obtain facet breakdowns narrowed by the same `text` and `filter` as Search. For Explore, `text` and `filter` are both optional; when both are absent, the aggregation covers the entire registry.

**Request Schema:**

```json
{
  "query": {
    "text": "currency conversion",
    "filter": {
      "trustManifest.attestations.type": ["SOC2-Type2"]
    }
  },
  "resultType": {
    "facets": [
      { "field": "type" },
      { "field": "publisher", "limit": 50 }
    ]
  }
}
```

In addition to the `query` object (§5.3.1), Explore accepts:

| Field | Type | Description |
| :--- | :--- | :--- |
| resultType | Object | Required. The shape of result to compute. The only defined shape is facets (below); future shapes such as counts or sample extend this field without protocol changes. |

Each element of `resultType.facets`:

| Field | Type | Description |
| :--- | :--- | :--- |
| field | String | Required. Term path to aggregate (same syntax as filter keys, §5.3.1). |
| limit | Integer | Optional. Maximum number of buckets returned. Default: 20. |
| minCount | Integer | Optional. Suppress buckets with counts below this threshold. |

**Response Schema:**

```json
{
  "resultType": "facets",
  "facets": {
    "type": {
      "buckets": [
        { "value": "application/mcp-server-card+json", "count": 1247 },
        { "value": "application/a2a-agent-card+json", "count": 389 }
      ],
      "otherCount": 23
    },
    "publisher": {
      "buckets": [
        { "value": "acme.com", "count": 412 }
      ]
    }
  }
}
```

Each bucket carries `value` and SHOULD carry `count` (the number of matching entries; a registry MAY omit it where counts cannot be computed efficiently). `otherCount` reports the number of matching entries in buckets beyond `limit`.

Facets are computed over the full matched set, not a single page. For semantic text queries, the registry applies a relevance cutoff: entries whose relevance falls below the cutoff are excluded from the matched set. The cutoff is registry-defined, but within a single registry the same cutoff governs both Search results and Explore facets. The cutoff and the relevance score (§5.3.2) reflect relevance only and MUST NOT be interpreted as a trust, compliance, or safety judgment.

Explore does not federate; it is scoped to the registry queried. Federated discovery is the role of Search (§5.3.2), via its federation modes (§5.4). A registry that does not implement Explore returns a `501 Not Implemented` HTTP status code.

#### 5.3.4 Retrieve (GET /agents/{identifier})

Retrieves one complete ARD entry by its globally unique `identifier`. Every Agent Registry **MUST** implement this endpoint. Lookup is an exact, case-sensitive primary-key operation after URL decoding; it does not perform semantic matching or relevance ranking.

The client **MUST** encode the complete identifier as one URL path segment using UTF-8 percent-encoding as defined by RFC 3986. For example:

```http
GET /agents/urn%3Aair%3Aacme.com%3Aagent%3Aassistant
```

The registry **MUST** percent-decode the path parameter exactly once and then validate it against the identifier syntax in Appendix C. Invalid percent-encoding or a decoded value that is not a valid ARD identifier returns `400 Bad Request` with error code `INVALID_ARGUMENT`.

Lookup is scoped to entries in the queried registry's index, including entries that the registry has ingested from external publishers. The registry **MUST NOT** query upstream registries while processing this endpoint. Clients that retain an identifier from a federated Search result **SHOULD** also retain its `source` and send subsequent Retrieve requests to that registry. A matching entry is returned directly as a complete ARD entry (§4), without Search-only fields such as `score` or `source`. If the registry's index does not contain an exact match, it returns `404 Not Found` with error code `NOT_FOUND`.

**Response Schema:**

```json
{
  "identifier": "urn:air:acme.com:agent:assistant",
  "displayName": "Corporate Assistant (A2A)",
  "type": "application/a2a-agent-card+json",
  "url": "https://api.acme.com/agents/assistant.json"
}
```

The endpoint uses the same deployment-defined authentication policy as the other Registry API endpoints. Missing or rejected credentials return `401 Unauthorized` with error code `UNAUTHENTICATED`.

Successful responses are cacheable under standard HTTP caching semantics. Registries **SHOULD** provide explicit freshness information with `Cache-Control` and a validator such as `ETag` or `Last-Modified`; conditional requests and `304 Not Modified` responses follow the HTTP specifications. Responses to authenticated requests **MUST NOT** be stored in a shared cache unless the response explicitly permits it. To avoid stale negative lookups as registry contents change, `404 Not Found` responses **SHOULD** require revalidation or specify a short freshness lifetime.

#### 5.3.5 List (GET /agents) — Optional

Deterministic browsing, designed for developer portals. Highly cacheable, relies on strict database filtering, and does not support relevance-based sorting.

**Parameters:**

| Parameter | Type | Description |
| :--- | :--- | :--- |
| filter | String | EBNF filter expression. |
| orderBy | String | Sorting fields (e.g. name, created_at DESC). |
| pageSize | Integer | Max results (default: 20, max: 100). |
| pageToken | String | Pagination token. |

#### 5.3.6 Protocol Wrappers (Optional)

While the REST API is mandated as the floor for interoperability, a Registry **MAY** additionally expose its search capability natively via an MCP Tool or an A2A Skill to preserve native orchestrator flows.

The return response from these protocol-specific wrappers **MUST** follow the same entry model as defined in this specification. However, the request format for these wrappers may differ slightly to accommodate protocol-specific conventions and is pending further definition.

### 5.4 Federation

Because the REST API is mandated, Registry-to-Registry routing (federation) becomes a simple HTTP operation. The client controls federation through the federation query parameter:

* **auto**: The Registry queries upstream registries automatically, merges their results with its own, and returns a unified response. The client gets a single merged result set.
* **referrals**: The Registry returns its results plus entries for other Registries the client may query. The client decides which to follow.
* **none**: The Registry searches only its own index.

This gives the client full control over the federation topology without requiring complex protocol translation layers.

#### Example: Referrals Mode

**Request:**

```json
{
  "query": {
    "text": "find me a flight booking agent"
  },
  "federation": "referrals"
}
```

**Response:**

```json
{
  "results": [
    {
      "identifier": "urn:air:acme.com:agent:expense",
      "displayName": "Corporate Expenses",
      "type": "application/a2a-agent-card+json",
      "url": "https://internal.corp/agents/expense.json",
      "score": 97,
      "source": "https://finder.internal.corp"
    }
  ],
  "referrals": [
    {
      "identifier": "urn:air:nlweb.ai:registry:public",
      "displayName": "Public Agent Finder",
      "type": "application/ai-registry+json",
      "url": "https://finder.nlweb.ai/search"
    },
    {
      "identifier": "urn:air:example.com:registry:travel",
      "displayName": "Travel Agent Finder",
      "type": "application/ai-registry+json",
      "url": "https://travel.finder.example/search"
    }
  ]
}
```

## 6. Integration Example

A user asks an orchestrator: "Book me a flight to Tokyo and file the travel expense report."

1. The orchestrator queries the enterprise Agent Registry with federation: "referrals".
2. The Registry returns an internal expense agent, plus referrals to other Registries.
3. The orchestrator follows a referral to a public Agent Registry and queries it for flight booking agents.
4. The orchestrator now has both capabilities and can proceed to invoke them using their respective protocols (e.g. A2A for booking, MCP for expense filing).

---

## Appendix A: Filter Expression Syntax

The filter parameter in the List API (GET /agents) uses a simple EBNF-like format for structured constraints.

| Filter Field | Type | Description |
| :--- | :--- | :--- |
| displayName | String | Case-insensitive name filter. |
| type | String | Comma-separated media types (OR logic). |
| publisherId | String | Comma-separated publisher IDs (OR logic). |
| createdAfter | String | ISO 8601 timestamp. |
| updatedAfter | String | ISO 8601 timestamp. |

Logical AND is used across different parameters; OR is used within a single parameter with multiple values (comma-separated).

## Appendix B: Standard Error Codes

| HTTP Code | Error Code | Description |
| :--- | :--- | :--- |
| 400 | INVALID_ARGUMENT | Malformed query or invalid filter syntax. |
| 401 | UNAUTHENTICATED | Invalid or missing credentials. |
| 404 | NOT_FOUND | Non-existent agent or registry. |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests. |
| 500 | INTERNAL_ERROR | Internal server failure. |

## Appendix C: Agent Naming URN Format {#appendix-c:-agent-naming-urn-format}

The discovery identifier uses a domain-anchored URN form, `urn:air:<publisher>:<namespace>:<agent-name>`, where `<publisher>` is a fully qualified domain name. Restricting the discovery identifier to this form, rather than allowing arbitrary URIs, provides fundamental architectural benefits for federated discovery:

1. **Nomenclature Stability (Immutable Noun vs. Mutable Location)**: Arbitrary URIs, particularly HTTP URLs, conflate the logical identity of a capability with its physical network location. The `urn:air:` identifier acts as an abstract, permanent contract; physical distribution and transport bindings are decoupled into the `url` or `data` term, allowing infrastructure to evolve without breaking client discovery, indexing, or orchestration code.
2. **Strict Separation of Concerns**: Federated registries require a stable primary key to index capabilities; zero-trust runtimes require dynamic cryptographic tokens (SPIFFE IDs, DIDs, X.509 certificates) to authenticate workloads. The `urn:air:` form cleanly decouples the searchable discovery handle from the security principal, allowing the discovery index and the security mesh to operate independently.
3. **Decentralized Trust and Authority Binding**: Mandating that `<publisher>` be a valid FQDN establishes a verifiable authority anchor. Registries extract the domain and cross-reference it with the cryptographic claim in `trustManifest.identity` (§4.5.1); a workload that cannot produce a valid attestation issued by that domain is rejected, without a centralized naming committee.
4. **Search and Discovery Ergonomics (The @ Resolution Pattern)**: The structured hierarchy lets registries parse publisher and terminal short name deterministically (e.g. `Assistant@Acme`), enabling high-performance semantic filtering, aggregation, and conflict resolution (e.g. displaying `Assistant` with a verified `Acme` shield).
5. **Cross-Network Uniqueness and Federation Scalability**: Domain-anchored URNs guarantee global uniqueness across federated registries without centralized registration, because domain names are already globally unique via the DNS root — eliminating collision risks when merging catalogs in auto or referrals federation modes.

The JSON-LD `@id` of an entry MAY be set to the same identifier (or to an IRI that resolves to the resource); when both are present they MUST denote the same resource.

## Appendix D: Formal Schema Definitions

To support automated validation, testing, and machine-readable compliance checking, this specification defines its own entry schema.

### D.1 The ARD Entry Schema

The ARD entry — its required terms, the value-or-reference rule, and the `trustManifest` envelope — is formally defined in JSON Schema (Draft 2020-12). Because ARD defines the ARD entry (§4), this schema is authoritative for it and does not derive from any catalog schema; the two evolve independently.

* **Authoritative schema**: [`spec/schemas/ard-entry.schema.json`](schemas/ard-entry.schema.json) — defines `ArdEntry` and `ArdManifest` (the `/.well-known/ard.json` document, §5.1).
* **Base context**: [`spec/schemas/ard.context.jsonld`](schemas/ard.context.jsonld) — the initial expansion context of §4.1, served at `https://agenticresourcediscovery.org/context/v1`.
* **Structural grammar (CDDL, RFC 8610)**: [`spec/schemas/ard.cddl`](schemas/ard.cddl)

Note that the schema sets `additionalProperties: true` by design. Terms drawn from namespaces declared in an entry's `@context` (§4.1) are valid and become filter dimensions; a closed schema would defeat the extension mechanism. The `trustManifest` envelope is likewise open — ARD reads only `identity` (§4.5).

To validate an entry with AJV CLI:
```bash
npx ajv-cli validate -s spec/schemas/ard-entry.schema.json -d path/to/entry.json
```

### D.2 ARD Discovery Constraints

Beyond structural validity, conformance checks the following:

* `representativeQueries` is present and contains 2–5 examples (§4.2) — **warning**, not error: an entry that omits it or supplies a different count still validates structurally, but is flagged, since it will not be found by search.
* The URN publisher domain MUST align with `trustManifest.identity` (§4.5.1).
* `capabilities` are treated as structured filter tokens (§5.3.1).

### D.3 The Registry REST API Specification (OpenAPI)

The HTTP query interfaces (`POST /search`, `POST /explore`, `GET /agents/{identifier}`, and `GET /agents`) exposed by compliant Agent Registries are formally defined using the **OpenAPI 3.1.0 Specification** in YAML.

* **Authoritative Specification File**: [`spec/schemas/ard.openapi.yaml`](schemas/ard.openapi.yaml)

### D.4 Official Conformance Testing Tool

To simplify development and guarantee compliance, this repository provides an official, zero-dependency **Conformance Testing CLI Tool**. It allows publishers to test their entries and registry developers to validate their REST API servers.

* **Testing Tool Executable**: [`conformance/bin/conformance-test`](../conformance/bin/conformance-test)

#### Features:
* **Manifest validation mode**: Parses a JSON manifest, validates it against `ArdManifest` and each of its entries against `ArdEntry` (§D.1), and executes ARD's discovery constraints (§D.2) — URN formatting, value-or-reference enforcement, `representativeQueries` presence and sizing.
* **Publisher resolution mode**: Given a domain, performs the resolution of §5.1 — fetches `/.well-known/ard.json`, falls back to the predecessor path with a warning that consumers are not required to consult it, and validates whatever it resolves.
* **Registry validation mode**: Probes live endpoints (`POST /search`, `POST /explore`, `GET /agents/{identifier}`, and `GET /agents`), sends spec-compliant requests, and validates status codes, exact identifier lookup behavior, pagination envelopes, relevance scores, and returned entries.

#### Usage Examples:

Validate a local or remote `ard.json` manifest:
```bash
# Validate a local manifest
./conformance/bin/conformance-test manifest path/to/ard.json

# Validate a remote well-known catalog manifest
./conformance/bin/conformance-test manifest https://example.com/.well-known/ard.json
```

Validate a running Agent Registry REST API:
```bash
./conformance/bin/conformance-test registry http://localhost:9010/api
```

#### One-Click Conformance Demo

To instantly run a complete end-to-end verification suite utilizing a pre-bundled spec-compliant catalog manifest and a lightweight running mock Registry REST API server, run the automated demo script:
```bash
./conformance/bin/run-conformance-demo
```
This script performs manifest schema validation, launches a mock registry server in the background, executes live search, lookup, exploration, and listing queries against it using the conformance tester, and gracefully terminates the server when finished.

## Acknowledgements

The authors thank the following people for their contributions and feedback, in alphabetical order.

- Amazon Web Services — Jeffrey Damick, Martin Ristov
- Cisco — Guillaume De Saint Marc, Karen Jaworski, Luca Muscariello, Ramiz Polic, Vijoy Pandey
- Databricks — Jonathan Keller, Vinod Marur
- GitHub — Evan Boyle, Jeremy Moseley, Meagan Cojocar, Trent Jones
- GoDaddy — Scott Courtney
- Google — Alan Blount, Antonio Gulli, Ines David, John Murray, Krishna Thota, Natasha Balasubramanian, Polong Lin, Rao Surapaneni, Sam Sharaf, Sampath Kumar Maddula, Srinivas Krishnan, Todd Segal
- Microsoft — Adam Zukor, Chelsea Carter, Dee Templeton, Jennifer Marsman, Kevin Scott, Lindsey Li, Lisa Jaloza, Miesha Baker, Ryan Nadel, Shelby Delano
- Nvidia — Aysen Ilkhabar
- Salesforce — Mariano Gonzales, Vijay Pandiarajan
- Snowflake — Baris Gultekin, Vivek Raghunathan
