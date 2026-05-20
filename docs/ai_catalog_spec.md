# AI Catalog Standard

**The Foundation for Federated AI Discovery**

Agent Finder is built directly on top of the **[ai-catalog](https://github.com/Agent-Card/ai-catalog)** specification. The `ai-catalog` standard establishes the base artifact-agnostic data model, progressive trust layer, and verification rules that enable dynamic runtime capability discovery.

---

## Standard Manifest Location

A host advertises its capabilities by publishing a well-known static JSON manifest at:

```http
https://<publisher-domain>/.well-known/ai-catalog.json
```

This allows secure, decentralized, and cacheable ingestion by crawlers and search registries worldwide.

---

## Core Envelope Schema

A baseline `ai-catalog.json` manifest includes the following root elements:

* **`specVersion`**: The version of the catalog format (e.g., `"1.0"`).
* **`host`**: Information about the entity operating the catalog (display name, DID/domain identifier).
* **`entries`**: An array of individual capability card definitions.
* **`collections`**: Links to sub-catalogs or related departmental feeds.

### Example Baseline Entry

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Systems",
    "identifier": "acme.com"
  },
  "entries": [
    {
      "identifier": "urn:ai:acme.com:tool:ocr",
      "displayName": "OCR Text Extractor",
      "type": "application/mcp-server+json",
      "url": "https://tools.acme.com/ocr/mcp.json",
      "description": "Extracts plain text and structured tables from scanned PDFs and PNGs."
    }
  ]
}
```

---

## Progressive Trust & Compliance

The `ai-catalog` standard decouples complex security and compliance data from lightweight metadata, utilizing a `trustManifest` object within each entry. This facilitates:

1. **Workload Identity**: Binding capabilities to SPIFFE IDs, decentralized identifiers (DIDs), or standard HTTPS domains.
2. **Compliance Attestations**: Standardizing links to SOC2, HIPAA, GDPR, or ISO audits.
3. **Provenance Links**: Recording lineage such as derived relationships (`derivedFrom`, `publishedFrom`) to enable supply-chain tracking.
4. **Cryptographic Signatures**: Verifiable detached JWS signatures computed over the trust metadata to prevent tampering.
