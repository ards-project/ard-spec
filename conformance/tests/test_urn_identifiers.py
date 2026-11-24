#!/usr/bin/env python3
"""The identifier grammar of Appendix C, urn:air:<publisher>:<name>[:<kind>] (ADR-0011)."""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFORMANCE_TOOL = REPO_ROOT / "conformance" / "bin" / "conformance-test"
SCHEMAS = REPO_ROOT / "spec" / "schemas"

VALID = (
    ("urn:air:example.com:weather-server", "example.com", "weather-server", None),
    ("urn:air:example.com:engineering/code-review", "example.com", "engineering/code-review", None),
    ("urn:air:example.com:engineering/code-review:skill", "example.com", "engineering/code-review", "skill"),
    ("urn:air:example.com:engineering.code-review:skill", "example.com", "engineering.code-review", "skill"),
    ("urn:air:example.com:finance/trading/trader", "example.com", "finance/trading/trader", None),
    ("urn:air:agents.example.com:tax_agent", "agents.example.com", "tax_agent", None),
    ("urn:air:example.com:caf%C3%A9", "example.com", "caf%C3%A9", None),
)

INVALID = (
    "urn:air:example.com",
    "urn:air:example.com:",
    "urn:air:example.com:finance:trading:trader",
    "urn:air:example.com:code-review::future-value",
    "urn:air:example.com:code review",
    "urn:air:example.com:code-review#skill",
    "urn:air:example.com:code-review?=x",
    "urn:air:exa_mple.com:code-review",
    "urn:ai:example.com:code-review",
)


def _run(identifiers):
    manifest = {
        "entries": [
            {
                "identifier": identifier,
                "displayName": f"Identifier fixture {index}",
                "type": "application/mcp-server-card+json",
                "url": f"https://example.com/artifacts/{index}",
                "representativeQueries": ["find an identifier fixture", "locate a test artifact"],
            }
            for index, identifier in enumerate(identifiers, start=1)
        ]
    }
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "ard.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-S", str(CONFORMANCE_TOOL), "manifest", str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )


def _schema_pattern(name):
    schema = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
    found = []

    def walk(node):
        if isinstance(node, dict):
            identifier = node.get("properties", {}).get("identifier")
            if isinstance(identifier, dict) and "pattern" in identifier:
                found.append(identifier["pattern"])
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(schema)
    return found


class UrnIdentifierTest(unittest.TestCase):
    def test_valid_identifiers_report_publisher_name_and_kind(self):
        result = _run([identifier for identifier, _, _, _ in VALID])
        self.assertNotIn("does not match the URN pattern", result.stdout)
        for identifier, publisher, name, kind in VALID:
            expected = f"Publisher: '{publisher}', Name: '{name}'"
            expected += f", Kind: '{kind}'." if kind else "."
            self.assertIn(expected, result.stdout, identifier)

    def test_invalid_identifiers_are_rejected(self):
        for identifier in INVALID:
            with self.subTest(identifier=identifier):
                result = _run([identifier])
                self.assertIn(f"Identifier '{identifier}' does not match the URN pattern", result.stdout)

    def test_schemas_use_the_same_grammar(self):
        # ECMA-262 and Python agree on this pattern's syntax, so the schema's own regex is checked directly.
        for name in ("ard-entry.schema.json", "ai-catalog.schema.json"):
            patterns = _schema_pattern(name)
            self.assertTrue(patterns, name)
            for pattern in patterns:
                regex = re.compile(pattern)
                for identifier, _, _, _ in VALID:
                    self.assertRegex(identifier, regex, f"{name}: {identifier}")
                for identifier in INVALID:
                    self.assertIsNone(regex.match(identifier), f"{name}: {identifier}")


if __name__ == "__main__":
    unittest.main()
