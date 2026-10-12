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

The specification does not define or constrain the internal schema of specific agent types (MCP, A2A, etc.). Instead, it acts as a clean envelope that uses a `type` term (formatted as an RFC 6838 / IANA Media Type) to identify what an artifact is, delegating the definition of artifact-specific metadata to the respective protocol specifications.

The `type` term is an open media-type string: any syntactically valid media type is accepted. For common agentic resources and discovery services, the standard recognized types are:

* `application/mcp-server-card+json` — MCP Server Card
* `application/a2a-agent-card+json` — A2A Agent Card
* `application/agent-card+json` — generic Agent Card
* `application/agent-skills+json` — Agent Skill metadata descriptor (JSON)
* `application/agent-skills+md` — Agent Skill defined in Markdown (or `text/markdown; profile="urn:air:agent-skills"`)
* `application/agent-skills+zip` / `application/agent-skills+gzip` — packaged Agent Skill archive
* `application/agent-plugins+zip` / `application/agent-plugins+gzip` — packaged Agent Plugin archive
* `application/ai-registry+json` (or `application/ai-registry`) — ARD Registry search service (§5.3)
* `application/ai-catalog+json` — nested manifest / catalog of entries

> **[!NOTE] IANA Registration Status**: The types above (such as `application/a2a-agent-card+json`, `application/mcp-server-card+json`, and the `agent-skills` / `agent-plugins` types) are de-facto community standards tracking towards formal registration. Implementers should note that while well-known path directories (like `/.well-known/agent-card.json`) are officially registered permanent entries, full type registrations are pending working group joint submission and the format may change. In the meantime, omit strict verification of these types by intermediaries.

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
| identifier | MUST | Globally unique discovery handle. Domain-anchored URN form (`urn:air:<publisher>:[<namespace>:]<agent-name>`, where `<namespace>` is optional and MAY span several segments); see Appendix C. The JSON-LD `@id` MAY mirror it. |
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
  "type": "application/agent-skills+md",
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

Entries in `trustManifest.attestations` can carry verifiable claims across distinct scopes — including **organizational compliance** (e.g., `SOC2-Type2`, `HIPAA-Audit`), **artifact security scans** (e.g., SARIF analysis of the artifact's content), **build provenance and SBOMs** (e.g., SLSA, in-toto DSSE), **transparency-log receipts** (e.g., SCITT/ANS registrations), and **runtime evaluations**. Consumers and registries should interpret each attestation according to its scope: an organizational compliance attestation applies to the publisher's control environment rather than the safety of a specific artifact, whereas artifact-scoped attestations (such as security scans or build provenance) should identify the evaluated artifact by cryptographic digest inside the referenced attestation document so the claim cannot be reattached to a modified artifact. Note that the `digest` field on the attestation item covers the referenced attestation document itself.

A relevance score returned by Search (§5.3.2) reflects semantic relevance only and MUST NOT be interpreted as a trust, compliance, or safety judgment; trust evaluation is fully decoupled.

## 5. Discovery

Discovery is what ARD is fundamentally about, and it spans this entire section: how entries are published and ingested (§5.1–5.2), how a client searches the resulting index (the search API, §5.3), how registries compose across a federation (§5.4), and how a registry learns ahead of a query what other registries hold (§5.5). It operates in two layers:

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
* **Change-Feed Subscription (Optional)**: Consuming other registries' change feeds (§5.5) to learn which identifiers to ingest and when they changed. The feed supplies the frontier and the change signal a crawler lacks; the entries themselves are still fetched from their publishers through web ingestion.

### 5.3 The Search API

The search API is the dynamic half of discovery. An Agent Registry **MUST** expose a standard HTTP REST search interface to guarantee universal federation. The operational base URL for these endpoints is discovered dynamically by identifying entries whose `type` is `application/ai-registry+json`. The `url` of such a well-known entry is the registry's **base URL**, and a client appends the endpoint path (for example `/search`). The `url` of a `RegistryReferral` in a search response's `referrals[]` is instead the referred registry's **search endpoint**, already complete, and a client MUST NOT append `/search` to it.

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

In a response, an entry MUST carry `identifier`; every other term is at the registry's discretion. A registry returns what is useful for selecting among results and MAY omit the rest — `representativeQueries` in particular serve indexing rather than presentation and are normally omitted. A result is therefore not necessarily a complete ARD entry (§4.2); its `identifier` names the authoritative one. Note that `url`, where present, addresses the artifact (an Agent Card, Server Card, and so on) — not the ARD entry that describes it. A normative operation for retrieving a complete entry by `identifier` is out of scope for this draft; a client that needs the full entry obtains it from the source that published it.

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

#### 5.3.4 List (GET /agents) — Optional

Deterministic browsing, designed for developer portals. Highly cacheable, relies on strict database filtering, and does not support relevance-based sorting.

**Parameters:**

| Parameter | Type | Description |
| :--- | :--- | :--- |
| filter | String | EBNF filter expression. |
| orderBy | String | Sorting fields (e.g. name, created_at DESC). |
| pageSize | Integer | Max results (default: 20, max: 100). |
| pageToken | String | Pagination token. |

#### 5.3.5 Protocol Wrappers (Optional)

While the REST API is mandated as the floor for interoperability, a Registry **MAY** additionally expose its search capability natively via an MCP Tool or an A2A Skill to preserve native orchestrator flows.

The return response from these protocol-specific wrappers **MUST** follow the same entry model as defined in this specification. However, the request format for these wrappers may differ slightly to accommodate protocol-specific conventions and is pending further definition.

### 5.4 Federation

Because the REST API is mandated, Registry-to-Registry routing (federation) becomes a simple HTTP operation. The client controls federation through the federation query parameter:

* **auto**: The Registry queries upstream registries automatically, merges their results with its own, and returns a unified response. The client gets a single merged result set.
* **referrals**: The Registry returns its results plus entries for other Registries the client may query. The client decides which to follow.
* **none**: The Registry searches only its own index.

This gives the client full control over the federation topology without requiring complex protocol translation layers.

These modes federate at query time: the work happens on every query, and the answer waits on every upstream. A registry MAY instead, or in addition, federate at index time by consuming other registries' change feeds (§5.5): it learns which identifiers they hold and when they change, fetches each entry from its publisher as §5.2 ingestion does, and answers from one index. The two compose. `federation: none` still means no query-time fan-out, whatever the registry's index was built from.

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

### 5.5 Change Feed (GET /changes) — Optional

The federation modes of §5.4 do their work at query time. The change feed is the index-time counterpart: it lets a registry learn, ahead of any query, which identifiers another registry holds and which of them changed, so that it can fetch those entries from their publishers through ordinary web ingestion (§5.2) and answer from one index.

`GET /changes` returns an ordered, cursor-driven, replayable feed of the identifiers a registry added, updated, or removed — and nothing else. It carries no entry content and no judgment about any entry. A consumer that learns an identifier from a feed fetches the entry from the identifier's **authority** — for the domain-anchored identifier of Appendix C, the `<publisher>` domain, resolved as §5.1 directs — and confirms every delete there. The feed says what exists and what changed; the authority says what the entry says. The feed can point a consumer only at entries reachable from their publisher domain (§5.1); an entry published only through a source the consumer cannot reach from the domain — in-page markup on a page it does not know, for example — is indexed, if at all, by crawling as today.

Implementing the feed is OPTIONAL. A registry that does not implement it returns a `501 Not Implemented` HTTP status code, as for Explore (§5.3.3). A registry operated as an upstream for other registries (§5.4) SHOULD implement it. The feed is served at `{base}/changes`, where `{base}` is the registry's base URL (§5.3).

#### 5.5.1 Request

```http
GET {base}/changes?cursor=0192f3a1-7c4e-7d21-9f0a-1b2c3d4e5f60&limit=500
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| cursor | String | Optional. An opaque position returned by a previous response from this registry (§5.5.4). Absent, the feed is read from the start of the retention window (§5.5.5), which yields every identifier the registry currently holds. |
| limit | Integer | Optional. Maximum number of changes per page (1–1000, default: 500). A registry MAY return fewer. |

The feed takes no filters: a change is small, and a consumer filters on its own side. A registry that needs scoped feeds publishes them at distinct base URLs.

#### 5.5.2 Response

**Response Schema:**

```json
{
  "changes": [
    {
      "cursor": "0192f3a1-7c50-7d21-9f0a-1b2c3d4e5f61",
      "op": "upsert",
      "time": "2026-09-11T14:02:12Z",
      "identifier": "urn:air:acme.com:server:weather"
    },
    {
      "cursor": "0192f3a1-7c52-7e10-8a3b-4c5d6e7f8091",
      "op": "delete",
      "time": "2026-09-11T14:02:13Z",
      "identifier": "urn:air:example.com:weather-server"
    }
  ],
  "cursor": "0192f3a1-7c52-7e10-8a3b-4c5d6e7f8091",
  "more": false,
  "retention": "P30D"
}
```

| Field | Type | Description |
| :--- | :--- | :--- |
| changes | Array | Required. Change objects (§5.5.3), ordered oldest to newest. MAY be empty. |
| cursor | String | Required, even when `changes` is empty. The position up to which the registry had examined its log when it built this page, at or after the last change returned. The consumer stores it and passes it back as the `cursor` parameter. |
| more | Boolean | Required. `true` when further changes were available when the page was built. `false` means the consumer has reached the tail and waits for its poll interval (§5.5.7). |
| retention | String | ISO 8601 duration of the retention window (§5.5.5). Required unless the registry retains every change indefinitely and therefore never answers `410`, in which case it is omitted. |

#### 5.5.3 The Change Object

| Field | Type | Description |
| :--- | :--- | :--- |
| cursor | String | Required. This change's position in the registry's log, later than the position of every earlier change (§5.5.4). |
| op | String | Required. `upsert` — the registry admitted the entry, or the entry's content changed — or `delete` — the registry removed it. A consumer MUST skip a change whose `op` it does not recognize and still advance its cursor. A resource's lifecycle state (deprecation, for example) is entry data at the authority and surfaces as an `upsert`. |
| time | String | Required. ISO 8601 timestamp at which this registry recorded the change, from its own clock. Informational; ordering is by `cursor`. |
| identifier | String | Required. The entry's `identifier` (Appendix C). Its `<publisher>` names the authority the consumer fetches the entry from. |

A change carries no entry content, no digest, no origin, no hop list, and no reason. Each of those would create a trust or correctness rule that exists only because a peer's copy of an entry was on the wire; the identifier alone lets the consumer obtain the entry from its authority (§5.5.7).

#### 5.5.4 Cursors and Delivery

* A cursor is an opaque string of 1 to 256 characters drawn from the unreserved characters of RFC 3986 (letters, digits, `-`, `.`, `_`, `~`). Consumers MUST NOT parse or construct cursors and MUST NOT assume any ordering between them; comparing two cursors for equality is permitted. A cursor is meaningful only at the registry that issued it, so a consumer keeps one cursor per upstream.
* **Delivery.** Replaying from a cursor yields, for every identifier changed after that position, at least its latest change as of read time, in cursor order. Delivery is at-least-once: a consumer applies changes idempotently, and a `delete` for an identifier it does not hold is a no-op. A registry MAY elide a change that a later change for the same identifier supersedes, so re-reading a cursor need not return identical content.
* **Continuation is always valid.** A registry MUST NOT issue a cursor it would reject. Every cursor it returns — including every page of a replay from an absent cursor — MUST be accepted for as long as the retention window (§5.5.5) is honoured.
* A registry MUST answer `400 INVALID_ARGUMENT` for a malformed cursor. A well-formed cursor the registry cannot place in its log receives `410 CURSOR_EXPIRED` when it predates the retention window (§5.5.5) and `400 INVALID_ARGUMENT` when the registry can determine that it never issued it; a registry that cannot tell the two apart answers `410`.
* A time-ordered unique identifier (UUIDv7, ULID), a monotonic sequence number, or an append-only log position all satisfy these rules, provided a change becomes visible to readers only after every change with an earlier position is visible (informative).

#### 5.5.5 The Retention Window

* `retention` names a sliding window ending at the time of the response. Within the window the registry MUST retain every `delete` it recorded that no later change for the same identifier supersedes, and at least one change for every identifier it currently holds.
* A registry keeps every held identifier inside the window in one of two ways. Either it retains changes indefinitely, never answers `410`, and omits `retention`; or, before the newest change for an identifier would age out of the window, it re-emits that identifier's latest change under a new cursor. Such a **maintenance repeat** reflects no change to the index and requires no fetch by the registry (§5.5.6). The window SHOULD be at least seven days (`P7D`).
* **Bootstrap.** Because the window contains every held identifier, a replay from an absent cursor meets every current identifier and reaches the tail without a `410`. No snapshot endpoint is needed.
* **Expiry.** A request whose `cursor` predates the window receives `410 CURSOR_EXPIRED`. The consumer then replays from an absent cursor into a staging set, after a randomized delay. When the replay reaches `more: false`, an identifier the consumer learned only from this upstream and that the staging set lacks becomes a `delete` hint (§5.5.7). A `410` never empties the live index.
* **Convergence.** Two complete replays taken while the registry is quiescent yield the same set of (`identifier`, latest `op`) pairs, and the identifiers whose latest `op` is `upsert` are exactly the identifiers the registry holds — where the registry implements List (`GET /agents`), the identifiers List enumerates.

#### 5.5.6 Producer Rules

* A registry emits an `upsert` for an identifier only when its own index changed because it ingested the entry through a pipeline §5.2 permits — a crawl, a fetch induced by a feed (§5.5.7), or another pipeline it operates — and admitted it, including a change to an entry it already held. It emits a `delete` only when it removed the entry: after confirming withdrawal at the authority, or because its own admission policy rejected the entry.
* Learning an identifier from another registry's feed is not, by itself, a reason to emit it; fetching the entry from its authority and admitting it is. Because every emitted change describes a first-party ingestion, registries that subscribe to each other converge without a hop list: when A learns X from B, fetches X from its authority, admits it, and emits it, B receives X, fetches it in turn, finds the entry it already holds, changes nothing, and emits nothing.
* A maintenance repeat (§5.5.5) carries the identifier's existing `op` under a new cursor. A change carries no digest, so a consumer cannot tell a repeat from a content change and treats every `upsert` alike: it fetches from the authority (a conditional request suffices), and when the fetch returns the entry it already holds, its index does not change and it emits nothing. That is why repeats do not propagate.
* A registry never rewrites an entry's `identifier` on ingestion or emission.

#### 5.5.7 Consumer Rules

* **Entries come from authorities, not peers.** On the strength of a feed, a consumer MUST NOT index or emit an entry it has not itself obtained from the identifier's authority. For a domain-anchored identifier it resolves the `<publisher>` domain as §5.1 directs, selects from the entry sources so reached the entry whose `identifier` matches, and admits it exactly as it would from a crawl: publisher-authority binding (§4.5.1) where a trust manifest exists, verification per the manifest's declared framework (§4.5.2), and the consumer's own admission policy. An identifier whose entry is not reachable from its publisher domain is not indexed on the strength of the feed; the consumer MAY retry it under its ingestion schedule.
* **Deletes are hints.** A consumer MUST NOT remove an entry on the strength of a `delete` alone; it confirms withdrawal at the authority. Absence from the manifest alone is not withdrawal, since §5.1 permits sources the manifest does not list: withdrawal is confirmed when the manifest and every source the consumer recorded for the entry, requested with the same credentials the consumer used to obtain the entry, either answer successfully without the entry or answer `404` or `410`. Any other outcome — a timeout, a connection or TLS failure, a `401`, a `5xx` — is a failed confirmation; the consumer then keeps the entry and retries with back-off, so a `delete` cannot be timed to an outage of the authority. How long an entry outlives an authority that stays unreachable is the question §5.2 leaves to the registry for crawled entries; the feed inherits that answer.
* **Fetch policy.** Fetches induced by the feed SHOULD follow the same outbound policy as crawling: `https` only; private, loopback, link-local, and cloud-metadata address ranges refused at connect time; redirects bounded, with no cross-origin redirect carrying credentials; per-authority rate limits with negative caching; request timeouts; response size caps. Consumers SHOULD batch confirmations by authority — one manifest fetch settles every pending hint for the identifiers found in that manifest.
* **Polling.** When `more` is `false`, the consumer waits at least its poll interval — 30 seconds or more, with randomized jitter — before polling again; when `more` is `true`, it continues immediately. `Retry-After` is honoured on `429` and `503`, with a ceiling (guidance: one hour). A page that is not valid JSON, exceeds the consumer's size cap (guidance: 1 MiB), or returns the request cursor unchanged while `more` is `true` is malformed; a page is not malformed because an `op` is unrecognized or a later revision added a member. After repeated malformed pages (guidance: three) the consumer stops polling that upstream, raises an alert, and leaves its cursor unchanged. Repeated `404` or `501` responses (same guidance) from a previously working feed mean the upstream withdrew it; the consumer keeps its index and stops polling.
* **Subscribing is an operator decision.** A registry MUST NOT begin polling a feed solely because it learned of a registry — for example from an `application/ai-registry+json` entry. Removing a subscription changes nothing in the index: the entries were fetched from their authorities and remain subject to the consumer's normal re-crawl schedule.
* **No authority conferred.** A change is discovery metadata. Nothing in a feed authorizes anyone to contact or invoke the resource an identifier names.

**Security.** No field of a change participates in a trust, precedence, or removal decision. A hostile upstream can make a consumer fetch an authority; it cannot make the consumer index anything the authority does not serve, and it cannot remove an entry the authority still serves. A public feed exposes identifiers only. Amplification toward a producer is bounded by the `limit` ceiling, `429` with `Retry-After`, the minimum poll interval, and cursor validation before storage access; reflected load toward authorities is bounded by the consumer's fetch policy.

#### 5.5.8 Errors

| HTTP Code | Error Code | When |
| :--- | :--- | :--- |
| 400 | INVALID_ARGUMENT | Malformed `cursor`, or one the registry can determine it never issued; `limit` out of range. |
| 401 | UNAUTHENTICATED | Credentials missing or rejected, where the deployment requires them. |
| 410 | CURSOR_EXPIRED | The `cursor` predates the retention window (§5.5.5). |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests; SHOULD carry `Retry-After`. |
| 501 | NOT_IMPLEMENTED | The registry does not offer a change feed. |

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
| 410 | CURSOR_EXPIRED | Change-feed cursor predates the retention window (§5.5). |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests. |
| 500 | INTERNAL_ERROR | Internal server failure. |
| 501 | NOT_IMPLEMENTED | Optional endpoint not offered by this registry (§5.3.3, §5.5). |

## Appendix C: Agent Naming URN Format {#appendix-c:-agent-naming-urn-format}

The discovery identifier uses a domain-anchored URN form, `urn:air:<publisher>:[<namespace>:]<agent-name>`, where `<publisher>` is a fully qualified domain name. `<namespace>` is optional and MAY contain more than one colon-separated segment, so `urn:air:example.com:weather-server` and `urn:air:example.com:finance:trading:trader` are both valid; only `<publisher>` and the terminal `<agent-name>` are required (ADR-0007). Restricting the discovery identifier to this form, rather than allowing arbitrary URIs, provides fundamental architectural benefits for federated discovery:

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

The HTTP interfaces (`POST /search`, `POST /explore`, `GET /agents`, and `GET /changes`) exposed by compliant Agent Registries are formally defined using the **OpenAPI 3.1.0 Specification** in YAML.

* **Authoritative Specification File**: [`spec/schemas/ard.openapi.yaml`](schemas/ard.openapi.yaml)

### D.4 Official Conformance Testing Tool

To simplify development and guarantee compliance, this repository provides an official, zero-dependency **Conformance Testing CLI Tool**. It allows publishers to test their entries and registry developers to validate their REST API servers.

* **Testing Tool Executable**: [`conformance/bin/conformance-test`](../conformance/bin/conformance-test)

#### Features:
* **Manifest validation mode**: Parses a JSON manifest, validates it against `ArdManifest` and each of its entries against `ArdEntry` (§D.1), and executes ARD's discovery constraints (§D.2) — URN formatting, value-or-reference enforcement, `representativeQueries` presence and sizing.
* **Publisher resolution mode**: Given a domain, performs the resolution of §5.1 — fetches `/.well-known/ard.json`, falls back to the predecessor path with a warning that consumers are not required to consult it, and validates whatever it resolves.
* **Registry validation mode**: Probes live endpoints (`POST /search` and `GET /agents`), sends spec-compliant search requests, and validates status codes, pagination envelopes, relevance scores, and returned entries (§5.3.2).

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
