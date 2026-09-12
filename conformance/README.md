# Agentic Resource Discovery Conformance Testing Tool

> **Automated compliance checking CLI to validate capability manifests and Registry REST API implementations.**

This directory contains the official, zero-dependency **Conformance Testing CLI Tool** designed to verify that manifests, publishers, and discovery registries conform strictly to the **Agentic Resource Discovery** specification.

---

## 🚀 Getting Started

The CLI is written in Python and is **completely zero-dependency**, running out-of-the-box on any machine with standard Python 3.

### 1. Make Executable
Ensure the test and demo runner scripts have execution permissions:
```bash
chmod +x bin/conformance-test bin/run-conformance-demo
```

### 2. Run the Automated One-Click Demo
You can instantly verify both manifest validation and Registry API probing using our pre-bundled mock assets. Run the automated demo:
```bash
./bin/run-conformance-demo
```
This script validates a mock spec-compliant `ard.json` manifest, starts a lightweight mock registry API server in the background, executes live conformance probes against it, and automatically cleans up on completion.

### 3. Run Manual CLI Checks
You can also run the tester directly without arguments to view its manual commands:
```bash
./bin/conformance-test
```

---

## 📖 Usage Instructions

The tool operates in three distinct verification modes:

### A. Manifest Validation Mode
Validates a local file or a remote live HTTP URL pointing to an ARD manifest.

```bash
# Validate a local manifest file
./bin/conformance-test manifest examples/basic/ard.json

# Validate a remote well-known manifest hosted on a web server
./bin/conformance-test manifest https://example.com/.well-known/ard.json
```

### B. Publisher Resolution Mode
Resolves a domain the way a conformant consumer does (§5.1), then validates whatever it finds. A consumer **MUST** fetch `/.well-known/ard.json`; consulting the predecessor `/.well-known/ai-catalog.json` is permitted but **not required**, so a publisher reachable only there is flagged as possibly undiscoverable.

```bash
./bin/conformance-test publisher example.com
```

### C. Registry API Validation Mode
Probes and validates a live running Agent Registry REST API server.

```bash
./bin/conformance-test registry http://localhost:9010/api
```

For private or self-hosted registries that require request headers, pass one or more `--header` options. Headers are applied to all Registry API probes (`GET /agents`, `GET /agents/{identifier}`, `POST /search`, and `POST /explore`):

```bash
ARD_REGISTRY_TOKEN=...
./bin/conformance-test registry https://registry.example.com/api/ard \
  --header "Authorization: Bearer ${ARD_REGISTRY_TOKEN}"
```

This is a conformance tooling option only; it does not require authentication for public registries or define a Registry API security model.

The tester normally obtains an identifier for the successful exact-lookup probe from List or Search. If neither returns an entry, provide a known locally indexed identifier explicitly:

```bash
./bin/conformance-test registry https://registry.example.com/api/ard \
  --lookup-identifier "urn:air:example.com:agent:assistant"
```

---

## 🔍 What It Validates

### 1. Manifest Validation Mode
When checking an ARD manifest (`ard.json`), the tool executes the following validations:

* **JSON Structural Integrity**: Parses the manifest payload to ensure it is valid, uncorrupted JSON.
* **JSON Schema Draft 2020-12 Conformance**: If the Python `jsonschema` library is installed (`pip install jsonschema`), the tool validates the document against `ArdManifest` and then every entry against `ArdEntry`, both from the authoritative [ard-entry.schema.json](../spec/schemas/ard-entry.schema.json).
* **Strict URN Pattern Matching**: Enforces that each entry's `identifier` adheres strictly to the domain-anchored URN namespace format defined in the spec:
  `urn:air:<publisher>:<namespace>:<agent-name>` (RFC 8141).
* **Value-or-Reference Delivery**: Enforces the mutual exclusivity constraint of the specification. Each entry **MUST** contain precisely one of either `"url"` (remote reference) or `"data"` (embedded payload), and will fail if both or neither are provided.
* **Media Type Diagnostics**:
  * Accepts the standard discovery media types without a diagnostic.
  * Warns clearly when a standard discovery type is missing required parameters or carries unrecognized parameters.
  * Reports well-formed, unrecognized `application/*` extension types as informational. ARD's `type` term is intentionally open, so extension types do not require registration in the conformance tool.
  * Warns when the deprecated `application/mcp-server+json` form from **ADR-0008** is used and names `application/mcp-server-card+json` as its replacement.
  * Gives a distinct syntax warning for malformed media types.
  * Retains the existing warning for well-formed, unrecognized types outside the `application` top-level type.
* **Discovery Constraints (§D.2)**:
  * Warns when `"representativeQueries"` is **absent** — the semantic index is built from it, so such an entry is a valid catalog entry but not a discoverable ARD entry.
  * Warns when it is present but does not contain **2 to 5** natural-language queries.
  * Verifies that standard properties (`entries`, `displayName`, `type`) are correctly typed. ARD requires only `entries` at the top level; other root members are transport-defined, and the tool reports them without failing.
* **Legacy Field Detection**: Warns (does not fail) on a `"collections"` root property, removed under **ADR-0003**. ARD ignores unrecognized top-level members, so its presence does not invalidate the manifest.

---

### 2. Publisher Resolution Mode
Given a domain, the tool performs the §5.1 resolution a conformant consumer performs:

* Fetches `/.well-known/ard.json` — the path a consumer **MUST** try.
* On failure, falls back to `/.well-known/ai-catalog.json` and **warns**: consulting that path is optional for consumers, so a publisher reachable only there may not be discovered.
* Fails only if neither path yields a manifest.
* Validates whatever it resolves using Manifest Validation Mode above.

---

### 3. Registry API Validation Mode
When checking a live Agent Registry server, the tool executes the following probes:

* **GET `/agents` (Optional Listing Probe)**:
  * Contacts the GET endpoint to check if the registry supports deterministic browsing.
  * If supported (returns `200 OK`), it validates that the response contains the paginated `"items"` structure.
  * If not supported (returns `404` or `501`), it marks this as compliant since deterministic listing is optional.
* **GET `/agents/{identifier}` (Mandatory Exact Lookup Probe)**:
  * URL-encodes a known full URN as one path segment and verifies a `200 OK` complete `ArdEntry` response with the exact identifier.
  * Verifies that Search-only fields such as `score` and `source` are absent.
  * Verifies that an unknown valid URN returns the standard `404` / `NOT_FOUND` error envelope.
  * Verifies that a malformed identifier returns the standard `400` / `INVALID_ARGUMENT` error envelope.
* **POST `/search` (Mandated Search Probe)**:
  * Probes the search route which is required for dynamic semantic capability discovery.
  * Sends a mock natural-language query payload with required `query` string and optional `filter` / `limit` parameters.
  * Verifies a `200 OK` response structure containing a `"results"` array.
  * Validates each result per §5.3.2: only `identifier` is required, since a registry MAY return just what selection needs. Omitted terms are reported, not failed.
* **POST `/explore` (Optional Introspection Probe)**:
  * Probes the dynamic introspection route for facet and bucketing generation.
  * Sends a mock request requesting facet counts grouped by `type`.
  * Verifies a `200 OK` response returning a valid `"resultType"` and `"facets"` Object.
  * If unsupported (returns `404` or `501`), it marks this as compliant since explore is optional.

---

## 📌 Exit Codes

The tool outputs standard exit codes, making it ideal for integration into **CI/CD pipelines**, automated git hooks, or test rigs:

* **`0`**: **PASS**. The manifest or registry conforms perfectly to the Agentic Resource Discovery specifications without errors.
* **`1`**: **FAIL**. The target violates one or more specification constraints. Details of the violations are printed in red to `stderr`.

---

## 💡 Tip: Enhanced Validation
For strict schema-level checking, install the Python `jsonschema` validator in your local development workspace:
```bash
pip install jsonschema
```
If present, the tool will automatically activate JSON Schema checking alongside its custom semantic validations.
