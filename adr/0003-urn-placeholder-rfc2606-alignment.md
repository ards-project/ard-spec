# ADR-0003: URN Placeholder Naming Alignment with RFC 2606

## Status
Accepted

## Context
The Agent Finder Naming Guide (`spec/urn-naming-guide.md`) mandates that discovery identifiers use a domain-anchored URN namespace format:
`urn:ai:<publisher>:<namespace>:<agent-name>`

To support local development and private sandboxes, developers require placeholder publisher values when they do not own a registered FQDN or cloud namespace. 

Prior versions of the guide informally recommended placeholders like:
* `urn:ai:local.dev:...`
* `urn:ai:local.internal:...`

However:
1. **gTLD Conflict**: The `.dev` suffix is a live, fully resolvable public generic Top-Level Domain (gTLD) owned by Google. Using `.dev` as a private, non-resolvable placeholder violates DNS specifications and can cause name resolution conflicts if validation middleware tries to verify the authority root.
2. **Standards track non-compliance**: Informally invented TLDs (like `.internal` or `.dev` placeholders) violate standard standards-track rules (like IETF RFC 2606 and RFC 6761), which formally reserve specific domains and TLDs for documentation and testing.

## Decision
We aligned all local-development placeholder recommendations in `spec/urn-naming-guide.md` with strictly compliant **RFC 2606** reserved names:

1. **`example.com`** (RFC 2606 §3): The standard reserved domain for documentation and static examples.
   * *Compliant URN*: `urn:ai:example.com:<namespace>:<agent-name>`
2. **`.localhost`** (RFC 2606 §2): A reserved TLD guaranteed to map natively to the loopback address. 
   * *Compliant URN*: `urn:ai:agent.localhost:<namespace>:<agent-name>`
   * *Role*: The primary placeholder for **human developer local sandboxes** (Scenario A & B), ensuring instant local-only resolution without editing `/etc/hosts`.
3. **`.test`** (RFC 2606 §2): A reserved TLD specifically intended for testing namespaces.
   * *Compliant URN*: `urn:ai:agent.test:<namespace>:<agent-name>`
   * *Role*: Reserved strictly for **automated testing suites, CI/CD pipelines, and conformance verification test runs** (like our `conformance-test` suite), where the environment needs to simulate mock external nodes and federated routing without triggering loopback behavior.

## Local Workload Verification vs. Syntax-Only Validation

This placeholder architecture establishes a clear security boundary based on the development lifecycle phase:

* **Syntax-Only Validation (Scenario A & B — Default)**: For standard local development, there is **no active cryptographic identity verification** happening. The placeholder domains (`*.localhost`, `example.com`) are enforced strictly to satisfy standard syntax validation rules and maintain architectural consistency with production files.
* **Workload Verification (Scenario C — Advanced Enterprise)**: If an enterprise developer is testing their production zero-trust security mesh (like SPIFFE/SPIRE or mTLS) inside a local Kubernetes/Istio cluster on their laptop, they use their **real domain** (e.g., `example.com`) as the URN publisher. This allows their local zero-trust mesh to actively validate their test certificates against the URN namespace before pushing to production.

This two-tier approach keeps local testing extremely lightweight and zero-friction, while providing a seamless path for heavy-duty enterprise security integration.

## Consequences
* **DNS Safety**: Guarantees that local test manifests will never conflict with live public DNS hosts or real domain ownership.
* **Compliance**: Fully complies with IETF DNS standards (RFC 2606), paving a smooth path for formal standards-track review under the IETF/AAIF.
* **Uniformity**: Simplifies local conformance validation checking (which can now statically white-list these RFC 2606 roots).
* **Operational Separation**: Establishes a clean boundary between human developer loopbacks (`.localhost`), automated testing/CI/CD environments (`.test`), and verified production bindings (real domains).
