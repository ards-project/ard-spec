# Reference publisher: Afore — A Travel House

**Vertical:** Travel / editorial / destination intelligence  
**Domain:** [afo.re](https://afo.re)  
**Live catalog:** [/.well-known/ai-catalog.json](https://afo.re/.well-known/ai-catalog.json)  
**Registry issue:** [ards-project/ard-spec#14](https://github.com/ards-project/ard-spec/issues/14)

## Integration stack

| Surface | URL |
|---------|-----|
| MCP (Streamable HTTP) | https://afo.re/api/mcp |
| MCP descriptor | https://afo.re/.well-known/mcp.json |
| ARD catalog | https://afo.re/.well-known/ai-catalog.json |
| agents.json | https://afo.re/agents.json |
| OpenAPI 3.1 | https://afo.re/openapi/afore-public-api.yaml |
| llms.txt | https://afo.re/llms.txt |
| security.txt | https://afo.re/.well-known/security.txt |
| Documentation | https://afo.re/about/for-ai |

## Catalog highlights

- Dynamic `updatedAt` from CMS
- Host `trustManifest` with `did:web:afo.re` and policy attestations
- `representativeQueries` on every entry (2–5 each)
- CI: Node structural validation + official `conformance-test manifest`
- HTML `<link rel="ai-catalog">` on all pages

## Snapshot

See [`afore-ai-catalog.snapshot.json`](./afore-ai-catalog.snapshot.json) for a point-in-time export. The live catalog at `afo.re` is authoritative.

## Representative queries (sample)

- find boutique hotels on the French Riviera with Afore editorial reviews
- hotels Afore has written about on the Côte d'Azur
- GPS coordinates for film locations near Cannes
- what is Afore's AI citation and training policy

---

Maintained by Afore · info@afo.re
