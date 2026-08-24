# Scan attestation vs compliance attestation

A worked example for the two attestation classes described in `spec/ard.md`
§5.2. The entry carries one of each, on purpose: the difference is only visible
when they sit side by side.

## Files

| File | What it is |
| :--- | :--- |
| `ai-catalog.json` | The catalog. One entry, two attestations. |
| `invoice-reader.scan.sarif` | The scan attestation document the entry references. |

The scanned artifact itself is not vendored here — in a real deployment it is
served by the publisher at the entry's `url`, and the attestation refers to it
by digest rather than by copy.

## What each attestation claims

`SOC2-Type2` is a **compliance attestation**. It says the publisher operates an
audited control environment. It says nothing about the invoice reader itself —
the same certificate would appear unchanged on every entry this publisher lists,
including one shipped yesterday and never reviewed.

The scan attestation says the artifact at the entry's `url` was analysed for
tool-poisoning and hidden-capability content. What makes that claim checkable is
not the entry — it is the referenced document.

## Following the binding

The entry's `digest` covers the **attestation document**, per the `digest`
description in `spec/schemas/ai-catalog.schema.json`:

```sh
shasum -a 256 invoice-reader.scan.sarif
# cdbd706458d30031292cb80c697357257e2fcb739917dc68d67c7b8925d3bee3
```

That hash is real and recomputable from the file here.

The binding to the **scanned artifact** lives one level further in, inside that
document, in SARIF's `runs[].artifacts[].hashes`. That value is illustrative,
since the artifact is served by the publisher rather than vendored here — but it
is the load-bearing one: change the artifact and it stops matching, so the scan
result cannot follow an artifact it was not computed over. The SOC 2 attestation
carries no digest because its report is not materialised here; `digest` is
optional.

The document also names what the scan was run under — `tool.driver.name` and
`version`, the `rules[]` it evaluated, and a ruleset name and version — so a
consumer can judge coverage instead of treating the attestation's presence as a
verdict. ARD does not require SARIF; any format that names its standard and
ruleset satisfies the SHOULD in §5.2.

## What this example does not claim

- **The type token is illustrative.** ARD does not define or register
  attestation type names, and `agent-threat-scan` here is a value chosen by a
  fictional publisher, not spec vocabulary.
- **A scan attestation is not a guarantee.** It is bounded by the ruleset named
  in it. A finding-free scan under one ruleset is not a finding-free scan under
  another, and neither is a statement about behaviour at runtime.
- **The digest binds content, not honesty.** It proves the analysed bytes are
  the bytes served. It does not prove the publisher was truthful about which
  scanner ran — that is what verifying the trust manifest's signature is for.

## Validate

```sh
cd conformance
./bin/conformance-test manifest examples/scan-attestation/ai-catalog.json
```
