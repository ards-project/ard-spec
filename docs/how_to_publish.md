# How to Publish

!!! danger "TODO: Review Publishing Specifications"
    Guha/Team: Please critically review the CORS requirements and DNS service bindings detailed below before final release.

Exposing your capabilities (MCP servers, skills, ACP agents, APIs) to the Agent Finder network is a simple three-step procedure.

---

## Step 1: Create the Manifest (`ai-catalog.json`)

Create a static `ai-catalog.json` manifest listing your tools. Below is a copy-pasteable template:

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Dev Tools",
    "identifier": "did:web:acme.com"
  },
  "entries": [
    {
      "identifier": "urn:ai:acme.com:server:weather",
      "displayName": "Acme Weather Telemetry Server",
      "type": "application/mcp-server+json",
      "url": "https://api.acme.com/mcp/weather.json",
      "capabilities": ["WeatherTool", "ForecastTool"],
      "description": "An enterprise weather MCP server providing live telemetry.",
      "representativeQueries": [
        "what is the current wind speed in Chicago",
        "get the 5-day forecast for Seattle"
      ]
    }
  ]
}
```

*   **`identifier`**: Naming must follow the domain-anchored URN standard: `urn:ai:<your-domain>:<tool-name>`.
*   **`representativeQueries`**: Provide **2–5 natural language queries** to enable high-fidelity semantic vector search.

---

## Step 2: Host the Manifest

Upload the manifest to your domain:
```text
https://<your-domain>/.well-known/ai-catalog.json
```

Ensure your web server serves it with:

*   **HTTPS**: Secure connection only.
*   **Content-Type**: `application/json`
*   **CORS Header**: `Access-Control-Allow-Origin: *` (Crucial for crawlers to fetch it).

---

## Step 3: Set up DNS Discovery (Optional)

If you cannot host at the standard `.well-known` path, publish a DNS `TXT` record pointing directly to your raw JSON location (e.g., S3 or GitHub pages):

| Name / Host | Type | Value |
| :--- | :--- | :--- |
| `_catalog._agents.yourdomain.com` | `TXT` | `"url=https://custom-bucket.s3.amazonaws.com/ai-catalog.json"` |

For dynamic search engines (`POST /search`), publish an `SRV` record:

| Name / Service | Type | Port | Target |
| :--- | :--- | :--- | :--- |
| `_search._agents.yourdomain.com` | `SRV` | `443` | `search.yourdomain.com` |
