# Scan Attestation vs. Compliance Attestation

A worked example for `trustManifest.attestations` in `spec/ard.md` (§4.5). The entry carries both an organizational compliance attestation and an artifact security scan attestation side by side to illustrate their distinct scopes.

## Files

| File | What it is |
| :--- | :--- |
| `ard.json` | The ARD manifest. One entry with two attestations. |
| `invoice-reader.scan.sarif` | The scan attestation document referenced by the entry. |

The scanned artifact itself is not vendored here — in a deployment it is served by the publisher at the entry's `url`, and the attestation refers to it by digest rather than by copy.

## What each attestation claims

`SOC2-Type2` is an **organizational compliance attestation**. It attests that the publisher operates an audited control environment. It does not make a claim about the `invoice-reader` artifact itself — the same certificate could appear unchanged across every entry the publisher lists.

The `agent-threat-scan` entry is an **artifact scan attestation** (one of several artifact-scoped attestation categories alongside build provenance such as SLSA/in-toto, transparency-log receipts, and runtime evaluations). It attests that the artifact at the entry's `url` was analyzed for tool-poisoning and hidden-capability content, bounded by the ruleset named in the referenced SARIF document.

## Following the binding

The entry's `digest` covers the **attestation document**, per `spec/schemas/ard-entry.schema.json`:

```sh
shasum -a 256 invoice-reader.scan.sarif
# cdbd706458d30031292cb80c697357257e2fcb739917dc68d67c7b8925d3bee3
```

That hash is recomputable from `invoice-reader.scan.sarif`.

The binding to the **scanned artifact** lives inside the SARIF document under `runs[].artifacts[].hashes`. If the artifact changes, that hash no longer matches, preventing a scan result from being silently reattached to a modified artifact.

The SARIF document also records `tool.driver.name`, `version`, `rules[]`, and `invocations[].properties` (`rulesetName`, `rulesetVersion`) so a consumer can evaluate the scope of the scan rather than treating the presence of an attestation as a blanket safety verdict.

## Notes

- **The `type` token is illustrative.** `trustManifest.attestations[].type` is an open string in ARD (§4.5); `agent-threat-scan` is an example value, not a closed spec enum.
- **A scan attestation is bounded by its ruleset and scanner.** Verifying `digest` confirms the integrity of the attestation document; verifying who ran the scan relies on the cryptographic signature over the trust manifest (`§4.5.2`) or an envelope such as an in-toto DSSE statement.

## Validate

```sh
./conformance/bin/conformance-test manifest conformance/examples/scan-attestation/ard.json
```
