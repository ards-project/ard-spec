# Agentic Resource Discovery Conformance Testing Tool

> **Automated compliance checking CLI to validate capability manifests and Registry REST API implementations.**

This directory contains the official, zero-dependency **Conformance Testing CLI Tool** designed to verify that catalogs and discovery registries conform strictly to the **Agentic Resource Discovery** and **ai-catalog** specifications.

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
This script validates a mock spec-compliant `ai-catalog.json` manifest, starts a lightweight mock registry API server in the background, executes live conformance probes against it, and automatically cleans up on completion.

### 3. Run Manual CLI Checks
You can also run the tester directly without arguments to view its manual commands:
```bash
./bin/conformance-test
```

---

## 📖 Usage Instructions

The tool operates in two distinct verification modes:

### A. Manifest Validation Mode
Validates a local file or a remote live HTTP URL pointing to an `ai-catalog.json` capability manifest.

```bash
# Validate a local catalog manifest file
./bin/conformance-test manifest examples/ai-catalog.json

# Validate a remote well-known catalog manifest hosted on a web server
./bin/conformance-test manifest https://example.com/.well-known/ai-catalog.json
```

### B. Registry API Validation Mode
Probes and validates a live running Agent Registry REST API server.

```bash
./bin/conformance-test registry http://localhost:9010/api
```

---

## 🔍 What It Validates

### 1. Manifest Validation Mode
When checking a capability manifest (`ai-catalog.json`), the tool executes the following validations:

* **JSON Structural Integrity**: Parses the manifest payload to ensure it is valid, uncorrupted JSON.
* **JSON Schema Draft 2020-12 Conformance**: If the Python `jsonschema` library is installed (`pip install jsonschema`), the tool automatically runs a strict schema-level validation using the official [ai-catalog.schema.json](../spec/schemas/ai-catalog.schema.json) file.
* **Strict URN Pattern Matching**: Enforces that each entry's `identifier` adheres strictly to the domain-anchored URN namespace format defined in the spec:
  `urn:ai:<publisher>:<namespace>:<agent-name>` (RFC 8141).
* **Value-or-Reference Delivery**: Enforces the mutual exclusivity constraint of the specification. Each entry **MUST** contain precisely one of either `"url"` (remote reference) or `"data"` (embedded payload), and will fail if both or neither are provided.
* **Ecosystem Attributes Validation**:
  * Checks that `"representativeQueries"` contains between **2 to 5** natural-language queries to ensure high-performance semantic vector embeddings.
  * Verifies that standard properties (`specVersion`, `entries`, `displayName`, `type`) are correctly typed.
* **Deprecated Field Detection**: Ensures the catalog does **NOT** use the deprecated `"collections"` root property (removed under **ADR-0003** in favor of recursive catalog `entries` using `type: application/ai-catalog+json`).

---

### 2. Registry API Validation Mode
When checking a live Agent Registry server, the tool executes the following probes:

* **GET `/agents` (Optional Listing Probe)**:
  * Contacts the GET endpoint to check if the registry supports deterministic browsing.
  * If supported (returns `200 OK`), it validates that the response contains the paginated `"items"` structure.
  * If not supported (returns `404` or `501`), it marks this as compliant since deterministic listing is optional.
* **POST `/search` (Mandated Search Probe)**:
  * Probes the search route which is required for dynamic semantic capability discovery.
  * Sends a mock natural-language query payload with required `query` string and optional `filter` / `limit` parameters.
  * Verifies a `200 OK` response structure containing a `"results"` array.
  * Validates that the nested payload structure is a valid `CatalogEntry` (contains `identifier`, `displayName`, `type`, and `url` or `data`).
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
