# URN Naming and Publisher Guide

This guide provides architectural best practices and implementation guidance for structuring Uniform Resource Names (URNs) under the Agentic Resource Discovery specification, focusing on local development, solo developers, and trust verification.

---

## 1. The Core Principle: Identity vs. Location

Every agent or capability in the discovery catalog is uniquely identified by a domain-anchored URN namespace (as defined in RFC 8141):

```text
urn:air:<publisher>:<namespace>:<agent-name>
```

The absolute foundational principle of this identifier is the separation of **logical identity** from **physical location**:
* **Identity (The "Noun")**: The URN represents the permanent, abstract logical identity of the agent, establishing a stable primary key for search indexes and clients. It does *not* change based on where the agent is running or deployed.
* **Location (The "Where")**: The physical transport binding (e.g., an HTTP URL, mTLS endpoint, or stdio connection detail) is defined separately in the catalog entry’s `url` or `data` properties.

---

## 2. Why `localhost` is an Anti-Pattern in URNs

When running and testing agents locally, developers may be tempted to structure URNs like:
`urn:air:localhost:agent:assistant`

Using `'localhost'` as the URN publisher is not allowed for the following reasons:

1. **Decentralized Trust and Verification**: Under the Agentic Resource Discovery identity model, the `<publisher>` segment of a URN must be a Fully Qualified Domain Name (FQDN). Registries and orchestrators extract this domain (e.g., `acme.com`) and cross-reference it against cryptographic attestations (like SPIFFE SVIDs or DIDs) within the `trustManifest` to verify authority. Since `localhost` is not a publicly resolvable, cryptographically verifiable domain, it breaks the decentralized trust model.
2. **Namespace Collisions**: In a federated registry system, namespaces must be globally unique to avoid collisions. If multiple developers register their local agents using the `localhost` publisher, naming conflicts will occur as soon as those catalogs are merged or indexed.
3. **Nomenclature Instability**: The fact that an agent is currently running on localhost is a transient deployment detail. The URN represents the permanent contract; physical endpoint addresses belong in the operational transport configurations.

---

## 3. Guidelines for Solo Developers and Local Development

The specification provides clear, flexible pathways for developers to construct valid URNs without needing expensive enterprise infrastructure.

### Scenario A: Purely Local / Private Development
If you are building and testing an agent that will **only run locally** and will never be published to a shared or public discovery registry, you can use a **placeholder FQDN** to satisfy syntax validators:

* **Recommended Placeholders** (Using RFC 2606 reserved testing domains):
  * `urn:air:agent.localhost:<namespace>:<agent-name>` (Recommended for local sandboxes — reserved TLD mapping natively to loopback, avoiding `/etc/hosts` changes)
  * `urn:air:example.com:<namespace>:<agent-name>` (Reserved domain for documentation and static examples)

#### Example Manifest (`ai-catalog.json`):
```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Local Test Environment"
  },
  "entries": [
    {
      "identifier": "urn:air:agent.localhost:weather:telemetry",
      "displayName": "Local Weather Node",
      "type": "application/mcp-server-card+json",
      "url": "http://localhost:8080/mcp",
      "description": "Local test instance of the weather capability."
    }
  ]
}
```
*This catalog will successfully pass syntax compliance checks (such as the `conformance-test` suite), while keeping the physical execution targeted to localhost. For the formal architectural and standards-compliance rationale behind these placeholder choices, see [ADR-0003](../adr/0003-urn-placeholder-rfc2606-alignment.md).*

---

### Scenario B: Solo Developers without a Custom Domain
If you are a solo developer who wants to **publicly share** or distribute your capability, but you do not own a custom FQDN (e.g., `myname.com`) or use GitHub/Hugging Face, you can anchor your URN to any registered web presence or namespace you control. 

Since domain names are already globally unique via the DNS root, anchoring your URN to subdomains or public registries prevents collisions:

1. **Alternative Code Hosts / Package Registries**:
   If you distribute via other code hosting or packaging platforms, use their domain combined with your user namespace:
   * GitLab: `urn:air:gitlab.com:your-username:my-agent`
   * npm: `urn:air:npmjs.com:your-username:my-agent`
   * PyPI: `urn:air:pypi.org:your-username:my-agent`

2. **Free Subdomains**:
   If you host a portfolio, documentation, or personal page using a free hosting provider, use your allocated subdomain:
   * Vercel: `urn:air:your-app.vercel.app:my-agent`
   * Netlify: `urn:air:your-site.netlify.app:my-agent`
   * GitHub Pages: `urn:air:your-username.github.io:my-agent`
---

### Scenario C: Enterprise Developers or Developers with a Verified Domain
For developers inside an enterprise or those who own a custom domain (e.g., `acme.com`), they should use their real FQDN as the URN publisher even when developing and running locally. 

This ensures that the URN remains completely identical between their local development, staging, and production catalogs, avoiding the need to rewrite downstream orchestration rules or client references.

* **Guidance**:
  * **URN (Identity)**: Use the real FQDN (e.g., `urn:air:acme.com:finance:tax-agent`).
  * **Physical Endpoint**: Point to `localhost` in the local development manifest, and to the production gateway or API host in the production manifest.

#### Local Manifest Example (`ai-catalog-local.json`):
```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Finance Local Dev",
    "identifier": "did:web:dev.acme.com"
  },
  "entries": [
    {
      "identifier": "urn:air:acme.com:finance:tax-agent",
      "displayName": "Corporate Tax Assistant",
      "type": "application/a2a-agent-card+json",
      "url": "http://localhost:8000/agents/tax-assistant",
      "description": "Local development build of Corporate Tax Assistant."
    }
  ]
}
```

#### Production Manifest Example (`ai-catalog.json` hosted at `https://acme.com/.well-known/ai-catalog.json`):
```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Corporation",
    "identifier": "did:web:acme.com"
  },
  "entries": [
    {
      "identifier": "urn:air:acme.com:finance:tax-agent",
      "displayName": "Corporate Tax Assistant",
      "type": "application/a2a-agent-card+json",
      "url": "https://api.acme.com/finance/tax-assistant",
      "description": "Official Corporate Tax Assistant with production identity verification.",
      "trustManifest": {
        "identity": "spiffe://acme.com/finance/tax-agent",
        "identityType": "spiffe",
        "attestations": [
          {
            "type": "SOC2-Type2",
            "uri": "https://trust.acme.com/soc2.pdf"
          }
        ]
      }
    }
  ]
}
```

---

## 4. Summary Reference Table


| Deployment Context | Publisher FQDN | URN Example | Physical URL (Endpoint) | Trust Manifest Capability |
| :--- | :--- | :--- | :--- | :--- |
| **Enterprise Production** | Fully verified corporate domain | `urn:air:aws.amazon.com:finance:trader` | `https://api.aws.amazon.com/agents/trader` | Fully supported (SPIFFE/mTLS/DID) |
| **Solo Developer (Public)** | Registered user namespace / free subdomain | `urn:air:gitlab.com:johndoe:weather-tool` | `https://gitlab.com/johndoe/weather-tool` | Basic signatures / web DID |
| **Local / Private Dev** | Non-resolvable placeholder domain | `urn:air:agent.localhost:testing:analyzer` | `http://localhost:8080/analyzer` | None (Syntax verification only) |
