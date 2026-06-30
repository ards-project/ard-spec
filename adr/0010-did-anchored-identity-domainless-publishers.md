# ADR 0010: DID-Anchored Identity for Domainless Publishers

## Status
Proposed

## Context
The discovery identifier (§4.2.1) and the Trust Manifest authority-alignment
rule (§5.1) both require the `<publisher>` namespace root to be a fully
qualified domain name (FQDN), verifiable against a cryptographic workload
identity (mTLS / SPIFFE SVID) issued by that domain. The rationale is sound for
DNS-anchored publishers (Appendix C): the FQDN is an immediate, decentralized
authority anchor that forecloses namespace-squatting.

However, a growing class of publishers has no controllable domain — agents whose
identity is rooted in a [W3C Decentralized Identifier](https://www.w3.org/TR/did-core/)
(`did:plc`, `did:web`) and a signed personal data store. Today such a publisher
cannot appear in an ARD catalog at all: it can neither form a compliant
`urn:air:` identifier (no FQDN for the `<publisher>` slot) nor satisfy §5.1's
FQDN-aligned attestation requirement. This is a real hole in ARD's identity
story, raised against this spec in
[ards-project/ard-spec#47](https://github.com/ards-project/ard-spec/issues/47).

## Decision
Add a **DID-anchored branch** to the discovery identifier and a normative
resolution path, additively — the FQDN mainline is untouched.

1. **URN branch (§4.2.1).** When the `<publisher>` position carries the literal
   token `did`, the identifier follows
   `urn:air:did:<method>:<method-specific-id>:<namespace>:<agent-name>`. The
   initial registered method set is **`did:plc` and `did:web` only**, with the
   DID constrained to exactly three colon-segments
   (`did:<method>:<method-specific-id>`); path-bearing `did:web` and further DID
   methods are deferred to a later amendment. The existing
   `ai-catalog.json` identifier pattern already admits this form, so no schema
   change is required.
2. **Resolution path (§5.1.1).** A four-step normative procedure: resolve the
   DID Document (`did:plc` → `plc.directory`, `did:web` → `/.well-known/did.json`),
   select the `verificationMethod` (by JWS `kid`, else first compatible), verify
   a detached JWS computed over the **JCS-canonicalized ([RFC 8785](https://www.rfc-editor.org/rfc/rfc8785))**
   content, and reject on failure.
3. **Authority-alignment carve-out (§5.1).** For `identityType: "did"`,
   authority-alignment is satisfied by verified DID control via §5.1.1; FQDN
   alignment is not required. Additive language only — no rewrite of the FQDN
   rule.

Per maintainer guidance on #47, this ships as a single coupled change (URN branch
+ resolution path are interdependent and must merge together), and the
canonicalization choice is pinned to JCS rather than left implementation-defined.

## Consequences
- Domainless `did:plc` / `did:web` publishers can publish ARD catalog entries
  with cryptographically verifiable authority, without DNS or a cloud identity
  provider.
- The five federation properties in Appendix C are preserved by the DID branch
  (see new Appendix C.1); namespace-squatting remains foreclosed via DID control
  instead of FQDN control.
- No change to the `ai-catalog.json` schema, CDDL, or conformance fixtures; the
  existing `^urn:air:...` pattern already validates DID-anchored identifiers.
- A DID-control proof attests *who published*, never compliance or safety
  (§7.2 unchanged).
- The Appendix C.1 wording is written to compose with the transport-side FQDN
  pressure in [#24](https://github.com/ards-project/ard-spec/issues/24); a future
  unified domainless-namespace amendment can subsume both.
- `did:key` / `did:peer` and path-bearing `did:web` remain unsupported until a
  follow-up amendment, once the resolution machinery is validated against the
  initial two-method set.

## Companion work
[drknowhow/install-manifest-spec#37](https://github.com/drknowhow/install-manifest-spec/issues/37)
carries the artifact-side `publisher` block (optional `did` + detached JWS over
canonical manifest bytes) so an install-manifest can hold the publisher identity
binding this resolution path verifies. The same JCS canonicalization constraint
applies on both sides to keep one signing model.
