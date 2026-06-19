# Agentic Resource Discovery (ARD)

Canonical home of the **Agentic Resource Discovery** specification — a federated,
domain-anchored standard for cataloging, searching, and discovering agentic
resources (MCP servers, A2A agent cards, Skills, APIs, and other callable
services) across networks of discovery services. It builds on the
[ai-catalog](https://github.com/Agent-Card/ai-catalog) standard.

📖 Read the rendered spec at
**[agenticresourcediscovery.org/spec](https://agenticresourcediscovery.org/spec/)**
— the docs site renders [`spec/ard.md`](spec/ard.md) directly from this repo, so
this is the single source of truth.

## Layout

- [`spec/ard.md`](spec/ard.md) — the specification
- [`spec/schemas/`](spec/schemas/) — CDDL, JSON Schema, and OpenAPI definitions
- [`adr/`](adr/) — architecture decision records
- [`conformance/`](conformance/) — conformance test tooling

## Implementations in the wild

Independent, conformance-tested ARD deployments (validated with this repo's `conformance/` CLI):

| Publisher | Domain | Role | Conformance |
|---|---|---|---|
| SnowSure | snowsure.ai | Discovery registry (ski & snow) + publisher | PASS |
| SnowData | snowdata.ai | Discovery registry (ski & snow) + publisher | PASS |
| Afore | afo.re | Discovery registry (editorial travel) + publisher | PASS |
| LUXSKI | lux.ski | Publisher | PASS |
| Ski Limone | skilimone.com | Publisher | PASS |

Five independent `did:web` publishers; three run live ARD `POST /search` registries with cross-federation. Reference registry: `POST https://www.snowsure.ai/search`.

## Status

**v0.9 (Draft).** The specification is open and evolving; feedback and proposals
are welcome via issues and pull requests.

## License

See [`LICENSE`](LICENSE).
