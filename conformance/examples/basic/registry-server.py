#!/usr/bin/env python3
"""
Mock Agent Registry REST API Server
Implements standard Agentic Resource Discovery REST endpoints:
  - POST /search
  - GET /agents
  - GET /agents/{identifier}
Zero dependencies, uses Python standard library.
"""

import hashlib
import sys
import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import unquote, urlparse

PORT = 9010
URN_REGEX = re.compile(r"^urn:air:[a-zA-Z0-9.-]+(:[a-zA-Z0-9._-]+)+$")
INVALID_PERCENT_ENCODING = re.compile(r"%(?![0-9A-Fa-f]{2})")

# Mock catalog database seeded from ./ard.json
MOCK_CATALOG_ENTRIES = [
  {
    "identifier": "urn:air:acme.com:agent:assistant",
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
    "identifier": "urn:air:acme.com:server:weather",
    "displayName": "Weather Data Node",
    "type": "application/mcp-server-card+json",
    "url": "https://api.acme.com/mcp/weather.json",
    "capabilities": ["WeatherTool", "ForecastTool"],
    "description": "Enterprise weather MCP server for live telemetry.",
    "representativeQueries": [
      "what is the current wind speed in Chicago",
      "get the 5-day forecast for Seattle"
    ]
  },
  {
    "identifier": "urn:air:acme.com:catalog:engineering",
    "displayName": "Engineering Sub-Catalog Reference",
    "type": "application/ai-catalog+json",
    "url": "https://acme.com/catalogs/engineering.json",
    "description": "Nested catalog containing CI/CD and internal deployment agents."
  },
  {
    "identifier": "urn:air:acme.com:tool:unit-converter",
    "displayName": "Unit Converter",
    "type": "application/mcp-server-card+json",
    "url": "https://api.acme.com/mcp/unit-converter.json"
  }
]

class MockHTTPServer(HTTPServer):
    def server_bind(self):
        # HTTPServer performs a reverse DNS lookup here, which can stall offline demos.
        TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = host
        self.server_port = port

class MockRegistryHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Print logs to stderr with a custom marker
        sys.stderr.write(f"  [Mock Registry] {format%args}\n")

    def _send_json(self, status, data, headers=None):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
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
        elif parsed_path.path.startswith("/agents/"):
            raw_identifier = parsed_path.path[len("/agents/"):]
            try:
                if not raw_identifier or INVALID_PERCENT_ENCODING.search(raw_identifier):
                    raise ValueError("invalid percent-encoding")
                identifier = unquote(raw_identifier, encoding="utf-8", errors="strict")
            except (UnicodeDecodeError, ValueError):
                error_response = {
                    "errorCode": "INVALID_ARGUMENT",
                    "message": "The identifier path parameter is not valid UTF-8 percent-encoding."
                }
                self._send_json(400, error_response)
                return

            if not URN_REGEX.match(identifier):
                error_response = {
                    "errorCode": "INVALID_ARGUMENT",
                    "message": "The identifier path parameter is not a valid urn:air: identifier."
                }
                self._send_json(400, error_response)
                return

            entry = next(
                (item for item in MOCK_CATALOG_ENTRIES if item["identifier"] == identifier),
                None
            )
            if entry is None:
                error_response = {
                    "errorCode": "NOT_FOUND",
                    "message": f"ARD entry '{identifier}' was not found."
                }
                self._send_json(404, error_response, {"Cache-Control": "no-cache"})
                return

            canonical_entry = json.dumps(entry, sort_keys=True, separators=(",", ":")).encode("utf-8")
            etag = f'"{hashlib.sha256(canonical_entry).hexdigest()}"'
            cache_headers = {
                "Cache-Control": "public, max-age=60",
                "ETag": etag
            }
            if self.headers.get("If-None-Match") == etag:
                self.send_response(304)
                for name, value in cache_headers.items():
                    self.send_header(name, value)
                self.end_headers()
                return

            self._send_json(200, entry, cache_headers)
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
                if query_text in entry["displayName"].lower() or query_text in entry.get("description", "").lower():
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
        elif parsed_path.path == "/explore":
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

            result_type = req.get("resultType", {})
            facets_req = result_type.get("facets", [])

            if not facets_req:
                error = {"errorCode": "INVALID_ARGUMENT", "message": "Missing required 'resultType.facets' parameter."}
                self._send_json(400, error)
                return

            # Compute dynamic facets over mock dataset
            type_counts = {}
            for entry in MOCK_CATALOG_ENTRIES:
                etype = entry.get("type", "unknown")
                type_counts[etype] = type_counts.get(etype, 0) + 1

            facets_response = {
                "resultType": "facets",
                "facets": {
                    "type": {
                        "buckets": [{"value": k, "count": v} for k, v in type_counts.items()],
                        "otherCount": 0
                    }
                }
            }
            self._send_json(200, facets_response)
        else:
            error_response = {
                "errorCode": "NOT_FOUND",
                "message": f"Route POST {parsed_path.path} not found."
            }
            self._send_json(404, error_response)

def run_server():
    server_address = ('127.0.0.1', PORT)
    httpd = MockHTTPServer(server_address, MockRegistryHandler)
    print(f"🚀 [Mock Registry] Running server on http://127.0.0.1:{PORT}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down mock server...")
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    run_server()
