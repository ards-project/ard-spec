# How to Build a Search

!!! danger "TODO: Review Search Registry Specifications"
    Guha/Team: Please critically review the ingestion security rules, vector similarity scaling, and federated query relay loop specifications detailed below before final release.

A Search Registry is an active service that crawls static manifests, indexes capabilities semantically, and exposes standard REST search endpoints (`POST /search`) to clients.

Building your own Search Registry is entirely optional. If you only want to publish capabilities, you only need to host a static manifest (see [How to Publish](how_to_publish.md)). To query capabilities, your client can connect to any existing public or private search registry (see [Implementations](implementations.md) for active endpoints).

---

## Step 1: The Ingestion & Crawling Pipeline

The registry populates its database by crawling the web for static `ai-catalog.json` manifests.

1.  **Crawling Loop**: Regularly scan known domains, fetch `https://<domain>/.well-known/ai-catalog.json`, and parse the `entries` array.
2.  **Domain Ownership Security**: Before indexing a tool entry, you MUST verify domain authority to prevent spoofing:
    *   Extract the domain root from the logical URN identifier (e.g., `urn:ai:google.com:tax-agent` ➜ `google.com`).
    *   Verify that the FQDN hosting the manifest matches this domain, OR cryptographically verify the `trustManifest.identity` using `did:web` rules.
    *   **Rule**: If `untrusted.com` publishes a manifest containing an entry for `urn:ai:google.com:tax-agent`, the registry MUST reject it.

---

## Step 2: The Semantic Vector Index

To enable semantic natural language search, the registry must index capabilities using vector embeddings.

```
[ai-catalog.json] ──> [Embed representativeQueries] ──> [Store in Vector DB]
                                                               │
                                                               ▼
[POST /search Query] ──> [Embed Query Text] ──> [Cosine Similarity Search]
```

### 1. Indexing (Write Path):
1.  For each ingested tool entry, extract the `representativeQueries` array and the `description`.
2.  Pass these text strings through a standard embedding model (e.g., `text-embedding-004`) to generate dense vector representations.
3.  Store the resulting vectors in a vector database (such as `pgvector`, `Qdrant`, or `Pinecone`) mapped to the tool's URN `identifier` and endpoint `url`.

### 2. Searching (Read Path):
1.  When a client calls `POST /search` with a natural-language `text` query:
    *   Generate an embedding vector for the incoming query string.
    *   Perform a **cosine similarity search** in the vector database to find the closest matching tool embeddings.
2.  Convert the mathematical similarity distance to the standard **`score` (0–100)**.
3.  Return the ranked results array.

---

## Step 3: Executing Federation (`auto` mode)

If a client requests `federation: auto` in their search query, the registry acts as a federated coordinator:

1.  **Local Query**: Execute the similarity search against the registry's local database.
2.  **Upstream Relay**: In parallel, forward the exact `POST /search` request to alternative registries listed in the local referral index.
3.  **Merge & Re-rank**: 
    *   Collect all result sets.
    *   De-duplicate entries by their primary key URN `identifier` (giving preference to the highest score or verified signature).
    *   Re-sort the merged list by `score` and return the unified results to the client.
