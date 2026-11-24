# ADR-0011: Adopt AI Catalog's `urn:air` Grammar

## Status
Proposed

Supersedes the segment structure in [ADR-0007](0007-urn-naming-pattern-flexibility.md). ADR-0007's character and
publisher-FQDN rules stand.

## Context
ARD and AI Catalog both identify resources with `urn:air` URNs, and ARD's discovery identifier is the AI Catalog entry's
`identifier` ([ADR-0010](0010-ard-and-ai-catalog-loose-coupling.md): an ARD entry is the AI Catalog entry core plus
namespaced terms). The two grammars have diverged.

- ARD, Appendix C after ADR-0007: `urn:air:<publisher>:[<namespace>:]<agent-name>`, with any number of
  colon-separated namespace segments and the last component as the agent name.
- AI Catalog, [ADR-0030](https://github.com/Agent-Card/ai-catalog/blob/main/adr/0030-urn-air-name-and-kind.md)
  ([PR 138](https://github.com/Agent-Card/ai-catalog/pull/138), merged 2026-11-18, now in the v0.9 release candidate):
  `urn:air:{publisher}:{name}[:{kind}]`. Colons separate only the publisher, a name with publisher-defined internal
  structure, and an optional single-component kind. A publisher organizes names with `/` or `.`.

The same string therefore means two different things. `urn:air:acme.com:finance:assistant` is namespace `finance` and
agent name `assistant` to ARD, and name `finance` with kind `assistant` to AI Catalog. A registry that ingests AI
Catalog documents, which ARD registries do, cannot follow both. `urn:air:acme.com:engineering/code-review` is valid AI
Catalog and fails ARD's schema pattern, which has no `/`.

This is gap G4 in [issue 117](https://github.com/ards-project/ard-spec/issues/117).

AI Catalog considered `#kind` and `;kind` suffixes in
[ai-catalog issue 59](https://github.com/Agent-Card/ai-catalog/issues/59) and chose the colon. RFC 8141 §3.1 drops the
f-component when comparing URNs, so `#kind` cannot tell two identifiers apart, and `;` is a command separator when an
identifier is pasted unquoted into a shell.

## Decision
ARD's discovery identifier is an AI Catalog `urn:air` identifier: `urn:air:<publisher>:<name>[:<kind>]`.

1. **Components.** `<publisher>` is a fully qualified domain name and is everything between `urn:air:` and the next
   colon. `<name>` has publisher-defined structure. `<kind>` is optional, assigned by the publisher, and ARD defines no
   vocabulary for it; `type` still says how to process the resource. Neither `<name>` nor `<kind>` contains a literal
   colon, and both use RFC 8141 namespace-specific-string characters otherwise.
2. **Comparison.** Identifiers compare as complete strings, case-sensitively and without normalization, kind included,
   matching AI Catalog's Entry Release Coverage comparisons. A registry does not strip or ignore the kind when it
   matches, deduplicates or filters. This is stricter than RFC 8141 §3.1, which ignores the case of `urn`, the NID
   and percent-encoding hex digits, so the canonical spelling is pinned: `urn:air:` lowercase, `<publisher>` lowercase
   (SHOULD), percent-encodings in uppercase hex.
3. **Preservation.** A registry incorporating an entry under a publisher-authorized `urn:air` identifier preserves it
   exactly, as AI Catalog's Catalog Projection requires.
4. **Display name.** A display name derived from the identifier is the entire `<name>`, verbatim, as in AI Catalog.
5. **Schema pattern.** The `identifier` pattern in `ard-entry.schema.json` and `ai-catalog.schema.json` becomes
   `^urn:air:[a-zA-Z0-9.-]+:C(:C)?$`, with `C` one or more of `[a-zA-Z0-9._~!$&'()*+,;=@/-]` or a `%XX` escape. The
   conformance tool uses the same pattern and reports the publisher, name and kind.
6. **Examples.** Every example identifier with a colon-separated namespace moves the namespace into the name with `/`,
   for example `urn:air:github.com:alice-dev:pptx-creator` becomes `urn:air:github.com:alice-dev/pptx-creator`, so
   each keeps the meaning it had. ADRs 0007, 0009 and 0010 and `spec/ard-v0.9.md` are records and are left unchanged.

ARD continues to require a `urn:air` identifier. AI Catalog allows any URI and recommends `urn:air`; whether ARD
should relax to match is a separate question.

## Consequences
- **One grammar.** An identifier read from an AI Catalog document means the same thing to an ARD registry, and every
  AI Catalog `urn:air` identifier with a domain publisher and no RFC 8141 r-, q- or f-component passes ARD's schema.
- **Breaking for colon namespaces.** An existing identifier with a colon-separated namespace now reads as name and
  kind, and one with more than three components after `urn:air:` is invalid. Appendix C tells publishers to move the
  namespace into the name. A registry holding such identifiers keeps them as given, since it must preserve them, and
  they stay distinct strings from the rewritten ones.
- **Kind matters for equality.** `urn:air:acme.com:weather` and `urn:air:acme.com:weather:mcp` are two identifiers. A
  publisher that wants one identifier across several artifact types leaves the kind off.
- **Future components.** ADR-0030 notes that a future revision may add components after an omitted kind
  (`urn:air:acme.com:code-review::future-value`). This pattern rejects an empty component, and would change with it.
