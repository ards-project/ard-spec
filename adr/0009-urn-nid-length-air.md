# ADR 0009: URN Namespace Identifier (NID) Length and Transition to "air"

## Status
Accepted

## Context
The Agentic Resource Discovery (ARD) specification initially utilized the `urn:ai:` prefix for identifying agents and registries (e.g., `urn:ai:<publisher>:<namespace>:<agent-name>`). However, in the formal structure of a Uniform Resource Name as defined by IETF specifications, the URN namespace identifier (`<nid>`) is required to be longer than two characters. Our initial `ai` NID was only two characters long, making it invalid under these constraints.

## Decision
We are changing the primary URN namespace identifier (NID) from `ai` to `air` to ensure the NID is at least three characters long. 

The new pattern will be:
`urn:air:<publisher>:<namespace>:<agent-name>`

This change also aligns with the latest agreed alignments across with ai-catalog.

## Consequences
- All schema references, OpenAPI documents, CDDL specifications, and mock data have been updated to use `urn:air:` instead of `urn:ai:`.
- This ensures full compliance with standard URN parsers and avoids short-identifier constraint issues.
- Implementers must update their identifier schemas to use the `air` NID.
