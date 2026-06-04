# ADR-0008: Renaming MCP Media Type to application/mcp-server-card+json

## Status
Accepted

## Context
In the Agent Finder and `ai-catalog` specifications, standard IANA Media Types are used inside the `type` field of a catalog entry to identify the structure and protocol of the capability being described (e.g., `application/a2a-agent-card+json` for A2A agents).

Previously, the media type representing Model Context Protocol (MCP) capabilities was defined as:
`application/mcp-server+json`

During standardization reviews, we identified a conceptual mismatch in this naming scheme:
1. **Metadata vs. Protocol Operational Stream**: The URN-based catalog entry is a **metadata discovery envelope**—containing descriptors, capabilities, representative queries, and trust manifests. It is **not** the actual live operational socket, stdio connection stream, or raw MCP protocol transport itself.
2. **Architectural Uniformity**: The A2A protocol uses `application/a2a-agent-card+json` to signify that the file is a descriptor/card about the agent, not the running agent runtime itself. For consistency, the MCP descriptor should use a parallel naming scheme.
3. **IANA Scope Clarification**: Using `application/mcp-server+json` could cause confusion during formal IANA registration, as reviewers might assume the media type governs the active operational stream protocol rather than the discovery card metadata.

## Decision
We decided to rename the standard MCP discovery media type across the entire Agent Finder and `ai-catalog` specifications to:

```text
application/mcp-server-card+json
```

This change clearly indicates that the media type governs the **metadata discovery descriptor card** of the MCP server capability, keeping it conceptually aligned with A2A's naming convention (`*-card+json`).

## Consequences
* **Consistency**: Aligns the A2A and MCP discovery envelopes under a unified, parallel naming convention (`application/a2a-agent-card+json` and `application/mcp-server-card+json`).
* **Clarification of Scope**: Prevents structural confusion during IANA registration by explicitly separating discovery card metadata from future runtime operational protocol stream registrations.
* **Transition Support**: In accordance with the specification's transition rules (§3.3), registries and intermediate servers SHOULD NOT reject discovery entries during this naming migration solely due to parsing differences.
* **Validation Enforcement**: All schema files (JSON Schema, OpenAPI, and CDDL) and conformance tests have been updated to enforce the `application/mcp-server-card+json` media type as the valid standard.
