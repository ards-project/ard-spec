# Implementations

Discover active implementations, dynamic search sandbox endpoints, and platform catalogs.

---

## Active Deployments

### 1. Mindpower Agent Finder
An example client-side implementation indexing, listing, and running search discovery for multiple registered agents and tools.
* **Live URL**: [https://mindpower.github.io/agent-finder/](https://mindpower.github.io/agent-finder/)
* **Type**: Registry Directory UI
* **Status**: Active

### 2. HuggingFace EvalState Search API
An example dynamic search endpoint built according to the Agent Finder specification. Demonstrates direct `POST /search` capabilities.
* **API Documentation**: [https://evalstate-hf-agentfinder.hf.space/docs#/](https://evalstate-hf-agentfinder.hf.space/docs#/)
* **Type**: Dynamic Search Registry (`POST /search`)
* **Status**: Active

---

## Upcoming Enterprise Support

We are partnering with top enterprise platforms to roll out native discovery endpoints and standard `.well-known/ai-catalog.json` support.

<div class="upcoming-cards">
  <div class="upcoming-card">
    <span class="upcoming-badge">Coming Soon</span>
    <h3>Google Workspace Agent Catalog</h3>
    <p>Native discovery feeds and SPIFFE-attested search endpoints for Gemini Enterprise Agent Platform integrations.</p>
  </div>
  <div class="upcoming-card">
    <span class="upcoming-badge">Coming Soon</span>
    <h3>Microsoft Copilot Registry</h3>
    <p>Auto-discovery and tenant-isolated dynamic routing search engines matching Entra ID authorization profiles.</p>
  </div>
</div>

---

## Joining the Ecosystem

Exposing your agents to Agent Finder registries is simple:

1. Create an [ai-catalog.json](ai_catalog_spec.md) at your domain root (e.g., `https://yourdomain.com/.well-known/ai-catalog.json`).
2. Add standard `entries` with their `identifier`, `displayName`, `type`, and `url` or inline `data`.
3. Provide 2-5 `representativeQueries` to enable high-fidelity vector embeddings.
4. Submit your FQDN to federated indices or let global crawlers discover your endpoint automatically!
