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

Independent deployments that pass this repo's conformance CLI
(`conformance/bin/conformance-test manifest <url>`) with zero critical errors:

| Implementation | Role | Catalog | Notes |
|---|---|---|---|
| [ASM — Agent Service Manifest](https://github.com/YE-YI7/asm-spec) | Publisher | [`/.well-known/ai-catalog.json`](https://asm-spec.onrender.com/.well-known/ai-catalog.json) | 30 tool-selection manifests typed `application/asm+json`; `urn:air:` identifiers, flat `asm:*` metadata, artifacts behind `url`. Emits 30 warnings, all of them the media-type recognition tracked in [#66](https://github.com/ards-project/ard-spec/issues/66). Hosted on a free tier that sleeps when idle — the first request after a quiet period may need a retry. |

Running a conformance-tested deployment? Open a pull request adding it here.

## Contributing

We'd love your involvement — contributions and feedback are very welcome. To keep
the standard coherent, we handle two kinds of changes differently:

- **Normative spec changes** (anything that alters the standard itself —
  [`spec/ard.md`](spec/ard.md) and the schemas in [`spec/schemas/`](spec/schemas/)):
  please [open an issue](https://github.com/ards-project/ard-spec/issues/new) to
  discuss the proposal first. Once there's agreement, a maintainer lands the change.
  This keeps the spec consistent and gives every change a clear rationale on record.
- **Everything else** (examples, conformance tooling, reference implementations,
  documentation, typo and link fixes): **pull requests are welcome** — just open one.

Not sure which bucket your idea falls in? Open an issue and we'll figure it out
together.

## Status

**v0.9 (Draft).** The specification is open and evolving; feedback and proposals
are welcome via [issues](https://github.com/ards-project/ard-spec/issues) and,
for non-normative changes, [pull requests](https://github.com/ards-project/ard-spec/pulls).

## License

See [`LICENSE`](LICENSE).
