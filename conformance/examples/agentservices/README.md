# AgentServices — ARD Catalog Example

Real-world [Agentic Resource Discovery](https://github.com/ards-project/ard-spec) catalog from [AgentServices](https://agentservices.to), a paid API platform for AI agents.

## About

AgentServices provides 52 endpoints (12 free, 40 paid) covering:
- Crypto data (prices, indicators, DeFi yields)
- Market intelligence (portfolio analysis, market pulse, DeFi strategy)
- On-chain analytics (whale tracking, exchange flows, stablecoin flows)
- Cross-DEX arbitrage scanning
- Deep research synthesis
- AI inference (multiple LLM models)

All paid endpoints use the [x402 payment protocol](https://x402.org) — agents pay per call in USDC on Base (L2).

## Catalog

The `ai-catalog.json` in this directory is the ARD-compatible version of the catalog served live at:

```
https://agentservices.to/.well-known/ai-catalog.json
```

It declares two entries:
1. **MCP Server** — Remote MCP transport (SSE) at `https://agentservices.to/mcp` with 37+ tools
2. **REST API** — HTTP endpoints with x402 nanopayments at `https://agentservices.to`

## Key Features

- **x402-native**: Every paid endpoint returns HTTP 402 with payment-required metadata. Agents sign EIP-3009 transfers and retry with payment headers.
- **Multi-channel access**: REST API, MCP endpoint, SDK (Python), and plugin (ElizaOS)
- **Agent discovery signals**: Schema.org, llms.txt, OpenAPI spec, robots.txt, x402 manifest, and ARD catalog all served from well-known paths
