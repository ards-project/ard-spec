# ADR-0007: URN Naming Pattern Flexibility and Underscore Support

## Status
Accepted

## Context
The Agent Finder Naming Guide (`spec/urn-naming-guide.md`) and schema configurations enforce a domain-anchored URN namespace format:
`urn:ai:<publisher>:<namespace>:<agent-name>`

In the initial versions of the specification, the validation pattern for this URN format was defined as:
`^urn:ai:[a-zA-Z0-9.-]+:[a-zA-Z0-9.-:]+:[a-zA-Z0-9.-]+$`

However, feedback from developers and deployment testing revealed three major issues:
1. **Unsafe Character Range**: The bracket syntax `.-:` used inside character classes included an unsafe range (ASCII 46 to 58) which unintentionally matched illegal characters like `/` (ASCII 47) and was prone to pattern compilation errors in Python and standard regex parsers.
2. **Rigid Namespace Structure**: The pattern required exactly three segments after `urn:ai:`. This made it impossible to declare an agent with **no namespace at all** (e.g., `urn:ai:acme.com:assistant`) or with a **multi-segment hierarchy** (e.g., `urn:ai:acme.com:finance:trading:trader`).
3. **Lack of Underscore (`_`) Support**: Many developers and systems use underscores in naming agents or organizing sub-namespaces (e.g., `urn:ai:acme.com:finance:tax_agent`). Forcing standard hyphens created friction with legacy setups.

## Decision
We refined the URN pattern definition to be fully RFC 8141-compliant, highly flexible, and developer-friendly:

1. **Decoupled Namespace Segments**:
   * The pattern was refactored to require a minimum of one publisher domain segment and one terminal agent name segment, allowing intermediate namespace segments to be optional and recursive:
     `^urn:ai:[a-zA-Z0-9.-]+(:[a-zA-Z0-9._-]+)+$`
2. **Support Underscores (`_`) in Namespace and Agent Name**:
   * Added underscore support to all non-domain segments.
3. **Strict FQDN Constraints for Publisher Domain**:
   * Kept the `<publisher>` domain segment strictly constrained to `[a-zA-Z0-9.-]` (alphanumeric, dots, and hyphens). Under standard DNS rules (RFC 1123 / RFC 952), public FQDNs do not permit underscores. This maintains strict network-level DNS safety.
4. **Python Conformance Adjustment**:
   * Updated the official python conformance checking tool `conformance-test` regex class to safely handle the python regex compiler character ranges (moving the literal dash `-` to the end of character classes):
     `r"^urn:ai:([a-zA-Z0-9.-]+)(?::([a-zA-Z0-9._:-]+))?:([a-zA-Z0-9._-]+)$"`

## Consequences
* **Ergonomics**: Developers can use natural naming styles containing underscores (e.g., `travel_concierge`).
* **Flexibility**: The specification supports URN namespaces of any hierarchical depth (e.g., `urn:ai:acme.com:department:team:service:agent`) or simple non-namespaced entries (e.g., `urn:ai:acme.com:agent`).
* **Security**: Ensures that URN `<publisher>` segments match legitimate resolved domains, preserving the decentralized zero-trust mesh and domain authority matching invariants.
* **Compliance**: Maintains strict compliance with standard URN rules defined in IETF RFC 8141.
