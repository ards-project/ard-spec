# Ski Limone — ARD Reference Implementation

**Publisher:** [Ski Limone by Afore Travel](https://www.skilimone.com)  
**Domain:** `skilimone.com`  
**Category:** Travel destination guide (ski resort + Piemonte wine country)

## Summary

Ski Limone is a production ARD deployment for a curated Alpine travel guide. It exposes a federated catalog of OpenAPI tools, a destination entity graph, hosted MCP, snow APIs, and agent onboarding documentation.

## Discovery signals

| Signal | URL |
|--------|-----|
| Well-known catalog | https://www.skilimone.com/.well-known/ai-catalog.json |
| OpenAPI 2.1 | https://www.skilimone.com/.well-known/openapi.json |
| MCP manifest | https://www.skilimone.com/.well-known/mcp/skilimone.json |
| Agent onboarding | https://www.skilimone.com/for-agents |
| robots.txt Agentmap | `Agentmap: https://www.skilimone.com/.well-known/ai-catalog.json` |
| HTML link | `<link rel="ai-catalog" href="https://www.skilimone.com/.well-known/ai-catalog.json">` |
| Optional DNS | `_catalog._agents.skilimone.com` TXT → catalog URL |

## Catalog entries (8)

1. OpenAPI agent API surface
2. Destination catalog (`/api/ai/v2`, schema 2.1.0)
3. Hosted MCP server (streamable HTTP)
4. Snow report API
5. Compact conditions API
6. Webcams API
7. LLM guide (`llms-full.txt`)
8. Agent onboarding page

## MCP endpoint

- **Transport:** streamable HTTP  
- **URL:** https://www.skilimone.com/api/mcp/mcp  
- **Tools:** search_content, get_snow_conditions, get_ai_health, get_hotel_details, get_restaurant_details, get_winery_details, get_village_place_details

## Conformance

Validated with the official conformance CLI (exit code 0):

```bash
./conformance/bin/conformance-test manifest https://www.skilimone.com/.well-known/ai-catalog.json
```

## Source

- Site repository: https://github.com/mikeslone/skilimone  
- Strategy doc: https://github.com/mikeslone/skilimone/blob/main/docs/ARD_STRATEGY.md

## Contact

hello@afore.travel
