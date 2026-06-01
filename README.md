# Agent Finder

> **Federated Discovery and Search for AI Agents and Capabilities**

Agent Finder is a standardized, domain-anchored discovery specification designed to catalog, search, and discover AI capabilities (including Model Context Protocol (MCP) servers, Agent-to-Agent (A2A) agent cards, skills, and other callable services) across federated networks. It is built on top of the foundational [ai-catalog](https://github.com/Agent-Card/ai-catalog) specification to ensure global federation and strict interoperability.

This repository contains the formal specification and related documentation for **Agent Finder**.

---

## 📖 Table of Contents
- [Overview](#-overview)
- [Core Design Principles](#-core-design-principles)
- [Data Model & Manifest Format](#-data-model--manifest-format)
- [Identity, Trust & Compliance](#-identity-trust--compliance)
- [Federated Discovery & The Search API](#-federated-discovery--the-search-api)
- [Repository Structure](#-repository-structure)
- [Version Status](#-version-status)
- [Ecosystem Alignment & Acknowledgments](#-ecosystem-alignment--acknowledgments)
- [License](#-license)

---

## 🔍 Overview

As the ecosystem of AI capabilities scales to thousands or millions of individual agents and tools, explicitly hardcoding or pre-installing each capability becomes untenable. 

**Agent Finder** introduces a **Search-First Discovery** paradigm where LLMs and orchestrators dynamically discover and select agents via dedicated search services. This approach moves the discovery and filtering burden outside the LLM's context window, leveraging information retrieval techniques and rich semantic signals without consuming valuable tokens.

---

## ⚡ Core Design Principles

1. **Search-First Discovery**: Capabilities are discovered dynamically at runtime through queries, rather than pre-installed or hardcoded (analogous to web search engines indexing the web).
2. **Context-Window Scalability**: Filters and semantic rankings are computed in external discovery indexes, enabling orchestrators to scale to millions of tools.
3. **Artifact-Agnostic Envelope**: Uses standard **IANA Media Types** (e.g., `application/a2a-agent-card+json`, `application/mcp-server+json`) to identify envelope contents, leaving the internal schema to the specific protocol specifications.
4. **Strict Value-or-Reference**: Safe, predictable ingestion using mutually exclusive `url` (remote reference) or `data` (embedded payload) keys.
5. **Universal REST Baseline**: Mandates a standard HTTP REST search interface (`POST /search`) for discovery and federation to ensure maximum interoperability.
6. **Separation of Concerns**: Decouples operational details—authentication is handled by the specific agent execution protocol, and physical delivery is managed by backend distribution networks (e.g., OCI, npm).

---

## 📄 Data Model & Manifest Format

### The Well-Known Manifest (`ai-catalog.json`)
Publishers host their catalog manifest at a well-known location to advertise their available capabilities:
```http
https://<publisher-domain>/.well-known/ai-catalog.json
```

### URN-Based Identification
Every agent in the catalog is uniquely identified by a domain-anchored, RFC 8141-compliant URN namespace:
```text
urn:ai:<publisher>:<namespace>:<agent-name>
```
* **`urn:ai`**: Ecosystem prefix.
* **`<publisher>`**: Verifiable FQDN representing the publisher (e.g., `example.com`), establishing a decentralized trust anchor.
* **`<namespace>`**: Optional hierarchical grouping (e.g., `finance:trading`).
* **`<agent-name>`**: Unique terminal short name (e.g., `assistant`).

---

## 🛡️ Identity, Trust & Compliance

Agent Finder supports a robust, optional `trustManifest` object that sits alongside discovery records. This consolidates:
* **Cryptographic Workload Identity**: decoupled from discovery ID (e.g., SPIFFE ID or DID) matching the domain anchor of the publisher.
* **Attestations**: Verifiable compliance credentials (e.g., SOC2-Type2, HIPAA-Audit, GDPR).
* **Provenance**: Relationship tracking (`derivedFrom`, `publishedFrom`) and digests for integrity.
* **Signatures**: Cryptographic detached JWS signatures over the trust metadata.

---

## 🌐 Federated Discovery & The Search API

### Standard REST Endpoints
An Agent Registry **MUST** expose a REST interface:

#### `POST /search`
Accepts natural-language search queries with optional filters and returns relevant capabilities ranked by semantic relevance scores.
* **Request Payload**:
  ```json
  {
    "query": {
      "text": "find me a flight booking agent",
      "type": "application/a2a-agent-card+json"
    },
    "pageSize": 5
  }
  ```
* **Response Payload**: Returns matched entries, relevance scores (0–100), and external registry referral endpoints if applicable.

#### `GET /agents` (Optional)
Provides deterministic, cacheable, and filterable catalog browsing for developer portals.

### Federation Modes
Registries support three client-controlled federation models:
* **`auto`**: The queried registry automatically queries upstream registries, merges, and ranks results.
* **`referrals`**: The registry returns its own matches plus referrals to external registries that the client can optionally query.
* **`none`**: Search is restricted strictly to the local registry index.

---

## 📂 Repository Structure

* [**`spec/agentfinder.md`**](spec/agentfinder.md): The core Agent Finder discovery and federation specification document.
* [**`adr/`**](adr/): Architectural Decision Records (ADRs) documenting key design, protocol, and validation decisions.
* [**`conformance/`**](conformance/): The official Agent Finder conformance testing suite. Contains CLI validators, mock catalog manifests, mock registry REST API servers, and automated end-to-end demo tools.

---

## 📌 Version Status

* **Specification Version**: `v0.5 (Draft)`
* **Status**: Proposal
* **Latest Revision**: May 28, 2026

---

## 🤝 Ecosystem Alignment & Acknowledgments

Agent Finder is directly based on and extends the [ai-catalog](https://github.com/Agent-Card/ai-catalog) specification. The ai-catalog standard provides the base artifact-agnostic data model, progressive trust layer, and validation rules. Agent Finder builds upon these standards to define dynamic registry search APIs (`POST /search`), federated query routing mechanisms, and domain-anchored naming schemes to enable dynamic runtime capability discovery.

---

## ⚖️ License

This project is licensed under the [Apache License, Version 2.0](LICENSE). See the [LICENSE](LICENSE) file for the full license text.
