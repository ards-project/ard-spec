# ADR 0010: Loose Coupling Between ARD Entries and AI Catalog Entries

- **Status:** Accepted
- **Date:** 2026-07-09
- **Attendees:** The `ai-catalog` working group and R.V. Guha
- **Reference:** [Issue #61](https://github.com/ards-project/ard-spec/issues/61)

## Summary

We spent most of the July 9th, 2026 meeting on the tension caused by the differing needs of ARD and `ai-catalog`. ARD is a search mechanism which necessarily has to synthesize signals from many sources, whereas `ai-catalog` wants to be the "master" descriptor from the provider of the service. We decided that at least for now, we will only have a loose coupling between ARD entries and `ai-catalog` entries. An ARD entry is the `ai-catalog` core plus flat, namespaced extensions.

## Context (The Tension)

`ai-catalog` wants two things:

1. Entries should carry only data from the resource's provider.
2. The core should hold only fields that apply to every resource type.

ARD needs the opposite on both counts. A discovery service aggregates. It pulls data from many sources (e.g., usage feedback) which can be very useful for the calling LLM. It also needs to describe many kinds of resources, each with its own fields, not just the common core.

So the two pull in opposite directions. Same entry shape, different jobs: `ai-catalog` is a publishing format; ARD is a discovery format.

## Decision

Loose coupling between ARD and `ai-catalog`:

- Entries returned by ARD are ARD entries, or AI Resources (AIR).
- AIR can carry namespaced attributes and values, using `@context` / CURIE.
- All `ai-catalog` fields are used in AIR, with the same meaning.

So an AIR is the `ai-catalog` entry core plus flat, namespaced extensions. Nothing else changes.

## Example

```json
{
  "@context": {
    "ard": "https://.../ard#",
    "okf": "https://openknowledgeformat.org/ns#"
  },
  "identifier": "urn:air:treasury.gov:okf:fiscaldata",
  "type": "text/vnd.okf+markdown",
  "okf:taxonomy": "us-gaap",
  "ard:usageScore": 0.87
}
```
