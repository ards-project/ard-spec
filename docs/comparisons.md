# Comparisons

Agent Finder is designed as a **superset** of existing agent and tool discovery approaches. It is not a replacement for other registries; rather, it acts as a federated overlay that unites them.

**Q. Why not X?**  
**A. Why not both?**  

*   **Universal Envelope**: Anything can get an AI Catalog "card". It supports an MCP server, a skill, an ACP agent, an A2A agent, a traditional REST API, or whatever comes next.
*   **Federated Indexing**: Once a card is published, it can be indexed by any Agent Finder registry. You don't have to choose between registries; Agent Finder can consume all of them or you can curate your own subset.

---

## What about...

### What about MCP Registry

The entire list of public MCP servers can be indexed natively. The official MCP Registry (`registry.modelcontextprotocol.io`) can remain exactly as it is today, while also acting as a federated source of truth that is crawled and made queryable via Agent Finder search endpoints.

`TODO(Guha): please fill in`

---

### What about ACP Agent Registry

The list of ACP Agents in [ACP's Agent Registry](https://agentclientprotocol.com/get-started/registry) is already structurally close to the AI Catalog specification. ACP registries can easily export their directory manifests as standard `ai-catalog.json` feeds, enabling instant web-scale discovery for editor-context tools.

`TODO(Guha): please fill in`

---

### What about Open Plugins

A plugin under the [Open Plugins](https://open-plugins.com/) standard is essentially a bundle of MCP servers, Skills, or other tools. By describing these bundles inside the standard AI Catalog specification, Open Plugins can leverage Agent Finder's federated infrastructure for instant decentralized deployment, crawling, and semantic indexing.

`TODO(Guha): please fill in`
