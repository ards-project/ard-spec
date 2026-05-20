#!/usr/bin/env python3
"""
Mock Agent Registry REST API Server
Implements standard v0.4 Agent Finder REST endpoints:
  - POST /search
  - GET /agents
Zero dependencies, uses Python standard library.
"""

import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = 9010

# Mock catalog database seeded from spec/examples/ai-catalog.json
MOCK_CATALOG_ENTRIES = [
  {
    "identifier": "urn:ai:acme.com:agent:assistant",
    "displayName": "Corporate Assistant (A2A)",
    "type": "application/a2a-agent-card+json",
    "url": "https://api.acme.com/agents/assistant.json",
    "description": "General-purpose corporate A2A assistant for internal workflows.",
    "representativeQueries": [
      "help me draft an email to the security working group",
      "summarize my unread messages from Todd"
    ]
  },
  {
    "identifier": "urn:ai:acme.com:server:weather",
    "displayName": "Weather Data Node",
    "type": "application/mcp-server+json",
    "url": "https://api.acme.com/mcp/weather.json",
    "capabilities": ["WeatherTool", "ForecastTool"],
    "description": "Enterprise weather MCP server for live telemetry.",
    "representativeQueries": [
      "what is the current wind speed in Chicago",
      "get the 5-day forecast for Seattle"
    ]
  },
  {
    "identifier": "urn:ai:acme.com:catalog:engineering",
    "displayName": "Engineering Sub-Catalog Reference",
    "type": "application/ai-catalog+json",
    "url": "https://acme.com/catalogs/engineering.json",
    "description": "Nested catalog containing CI/CD and internal deployment agents."
  }
]

class MockRegistryHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Print logs to stderr with a custom marker
        sys.stderr.write(f"  [Mock Registry] {format%args}\n")

    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Handle GET /agents (Deterministic listing route)
        if parsed_path.path == "/agents":
            # Handle basic pagination mock
            response = {
                "items": MOCK_CATALOG_ENTRIES,
                "total": len(MOCK_CATALOG_ENTRIES),
                "pageToken": None
            }
            self._send_json(200, response)
        else:
            # Return 404 for other routes
            error_response = {
                "errorCode": "NOT_FOUND",
                "message": f"Route GET {parsed_path.path} not found."
            }
            self._send_json(404, error_response)

    def do_POST(self):
        parsed_path = urlparse(self.path)
        
        # Handle POST /search (Mandatory discovery route)
        if parsed_path.path == "/search":
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                error = {"errorCode": "INVALID_ARGUMENT", "message": "Missing request body."}
                self._send_json(400, error)
                return

            try:
                body_data = self.rfile.read(content_length).decode('utf-8')
                req = json.loads(body_data)
            except Exception as e:
                error = {"errorCode": "INVALID_ARGUMENT", "message": f"Invalid JSON: {e}"}
                self._send_json(400, error)
                return

            query = req.get("query", {})
            query_text = query.get("text", "").lower()
            
            if not query_text:
                error = {"errorCode": "INVALID_ARGUMENT", "message": "Missing 'query.text' parameter."}
                self._send_json(400, error)
                return

            results = []
            # Match entries against the search query text
            for entry in MOCK_CATALOG_ENTRIES:
                score = 50  # Baseline score for any match
                matched = False

                # Match text against keywords in display name, description, or representative queries
                if query_text in entry["displayName"].lower() or query_text in entry["description"].lower():
                    score += 30
                    matched = True
                
                rep_queries = entry.get("representativeQueries", [])
                for rq in rep_queries:
                    if query_text in rq.lower():
                        score += 40
                        matched = True
                        break

                if matched or len(query_text) < 3:  # Empty or tiny query matches all as a fallback
                    score = min(score, 100)
                    results.append({
                        **entry,
                        "score": score,
                        "source": f"http://127.0.0.1:{PORT}/"
                    })

            # Sort results by score descending
            results.sort(key=lambda x: x["score"], reverse=True)

            response = {
                "results": results,
                "referrals": [],
                "pageToken": None
            }
            self._send_json(200, response)
        else:
            error_response = {
                "errorCode": "NOT_FOUND",
                "message": f"Route POST {parsed_path.path} not found."
            }
            self._send_json(404, error_response)

def run_server():
    server_address = ('127.0.0.1', PORT)
    httpd = HTTPServer(server_address, MockRegistryHandler)
    print(f"🚀 [Mock Registry] Running server on http://127.0.0.1:{PORT}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down mock server...")
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    run_server()
