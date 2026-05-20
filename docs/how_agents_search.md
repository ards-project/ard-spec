# How Agents Search

!!! danger "TODO: Review Client Search Specifications"
    Guha/Team: Please critically review the payload contracts, score interpretations, and client-side trust verification rules detailed below to ensure absolute alignment with orchestrator runtimes before finalizing this guide.

This guide outlines how AI client orchestrators (such as Claude Code, Gemini, Copilot) dynamically query federated search registries at runtime to find and load tool capabilities.

---

## Step 1: The Search Request (`POST /search`)

When a user asks for a capability that is not pre-installed, the agent orchestrator queries a search registry using the standard `POST /search` contract:

```json
{
  "query": {
    "text": "book me a flight to Tokyo",
    "type": "application/mcp-server+json",
    "federation": "referrals"
  },
  "pageSize": 3
}
```

*   **`text`**: Natural language intent extracted from the user query.
*   **`type`**: Filter by specific proposed media types (e.g., `application/mcp-server+json`).
*   **`federation`**: Set to `auto` (registry merges upstream results) or `referrals` (registry returns alternative registry URLs for the client to follow).

---

## Step 2: The Search Response

The registry returns a ranked list of catalog entries satisfying the semantic criteria:

```json
{
  "results": [
    {
      "identifier": "urn:ai:acme.com:travel:concierge",
      "displayName": "Travel Concierge",
      "type": "application/mcp-server+json",
      "url": "https://api.acme.com/mcp/travel.json",
      "score": 95
    }
  ],
  "referrals": [
    {
      "identifier": "urn:ai:finder.org:registry",
      "type": "application/ai-registry",
      "url": "https://finder.org/search"
    }
  ]
}
```

!!! warning "Important: Score Interpretation"
    The `score` parameter (0-100) is strictly an informational relevance metric computed semantically by the search index. Runtimes MUST NOT interpret this as a cryptographic trust, security compliance, or safety rating. Trust verification must be executed independently.

---

## Step 3: Client-Side Trust Verification

Before connecting to or executing any discovered capability, the client orchestrator MUST verify the publisher's credentials:

1.  **Extract Domain**: Parse the logical FQDN authority domain embedded in the URN identifier (e.g., `urn:ai:acme.com:travel:...` ➜ `acme.com`).
2.  **Verify Identity**: Fetch the manifest and cross-reference the `trustManifest.identity` (e.g., SPIFFE ID or `did:web`) to verify that the publisher controls the claimed FQDN.
3.  **Audit Compliance**: Parse the `attestations` array inside `trustManifest` to verify SOC2, HIPAA, or GDPR PDF/HTML certificate links.
4.  **Verify Signature**: Verify the detached JWS cryptographic signature block computed over the trust metadata to ensure no tampering has occurred in transit.
