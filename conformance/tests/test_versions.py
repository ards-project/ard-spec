#!/usr/bin/env python3

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFORMANCE_TOOL = REPO_ROOT / "conformance" / "bin" / "conformance-test"
IDENTIFIER = "urn:air:versions.test:fixture:agent"


def _entry(identifier=IDENTIFIER, **members):
    entry = {
        "identifier": identifier,
        "displayName": "Version fixture",
        "type": "application/a2a-agent-card+json",
        "url": "https://versions.test/agent.json",
        "representativeQueries": ["find the version fixture", "locate a versioned agent"],
    }
    entry.update(members)
    return entry


def _run(entries):
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "ard.json"
        path.write_text(json.dumps({"entries": entries}), encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-S", str(CONFORMANCE_TOOL), "manifest", str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )


def _version_lines(stdout):
    return [line for line in stdout.splitlines() if f"[{IDENTIFIER}]" in line]


class VersionTests(unittest.TestCase):
    def assert_passed(self, result):
        self.assertEqual(result.returncode, 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def assert_failed(self, result):
        self.assertNotEqual(result.returncode, 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_single_entry_without_version_is_silent(self):
        result = _run([_entry()])
        self.assert_passed(result)
        self.assertEqual(_version_lines(result.stdout), [])

    def test_semver_versions_are_ordered_by_precedence(self):
        result = _run([_entry(version="2.1.0"), _entry(version="2.0.0-rc.1"), _entry(version="1.0.0+build.7")])
        self.assert_passed(result)
        self.assertIn("3 versions, ordered by Semantic Versioning precedence", result.stdout)

    def test_non_semver_versions_with_updated_at_are_ordered_by_time(self):
        result = _run([
            _entry(version="1.0", updatedAt="2026-03-15T10:00:00Z"),
            _entry(version="2", updatedAt="2026-04-15T10:00:00Z"),
        ])
        self.assert_passed(result)
        self.assertIn("ordered by 'updatedAt'", result.stdout)

    def test_mixed_semver_and_other_versions_warn(self):
        result = _run([
            _entry(version="2.0.0", updatedAt="2026-01-15T10:00:00Z"),
            _entry(version="beta", updatedAt="2026-02-15T10:00:00Z"),
        ])
        self.assert_passed(result)
        self.assertIn("Some versions are Semantic Versioning 2.0.0 strings and some are not", result.stdout)

    def test_unorderable_versions_warn(self):
        result = _run([_entry(version="1.0"), _entry(version="1.1", updatedAt="2026-04-15T10:00:00Z")])
        self.assert_passed(result)
        self.assertIn("cannot be ordered", result.stdout)

    def test_duplicate_version_is_an_error(self):
        result = _run([_entry(version="1.0.0"), _entry(version="1.0.0", type="application/mcp-server-card+json")])
        self.assert_failed(result)
        self.assertIn('Version "1.0.0" is listed 2 times', result.stdout)

    def test_versions_compare_as_exact_strings(self):
        result = _run([
            _entry(version="1.0", updatedAt="2026-03-15T10:00:00Z"),
            _entry(version="1.0.0", updatedAt="2026-04-15T10:00:00Z"),
        ])
        self.assert_passed(result)

    def test_versionless_entry_sharing_identifier_is_an_error(self):
        result = _run([_entry(version="1.0.0"), _entry()])
        self.assert_failed(result)
        self.assertIn("An entry without 'version' MUST be the only entry with its identifier", result.stdout)

    def test_two_versionless_entries_are_an_error(self):
        result = _run([_entry(), _entry()])
        self.assert_failed(result)
        self.assertIn("Listed 2 times", result.stdout)

    def test_distinct_identifiers_are_independent(self):
        result = _run([_entry(), _entry(identifier="urn:air:versions.test:fixture:other")])
        self.assert_passed(result)
        self.assertEqual(_version_lines(result.stdout), [])

    def test_equal_precedence_after_build_metadata_warns(self):
        result = _run([_entry(version="1.0.0+a"), _entry(version="1.0.0+b")])
        self.assert_passed(result)
        self.assertIn("equal Semantic Versioning precedence", result.stdout)

    def test_equal_updated_at_warns(self):
        result = _run([
            _entry(version="1.0", updatedAt="2026-03-15T10:00:00Z"),
            _entry(version="1.1", updatedAt="2026-03-15T11:00:00+01:00"),
        ])
        self.assert_passed(result)
        self.assertIn("same 'updatedAt'", result.stdout)

    def test_updated_at_without_offset_warns(self):
        for value in ("2026-03-15T10:00:00", "2026-03-15", "yesterday", 1773568800):
            with self.subTest(value=value):
                result = _run([
                    _entry(version="1.0", updatedAt="2026-03-15T10:00:00Z"),
                    _entry(version="1.1", updatedAt=value),
                ])
                self.assert_passed(result)
                self.assertIn("no valid 'updatedAt'", result.stdout)

    def test_fractional_seconds_of_any_length_parse(self):
        result = _run([
            _entry(version="1.0", updatedAt="2026-03-15T10:00:00.5Z"),
            _entry(version="1.1", updatedAt="2026-03-15T10:00:00.123456789+00:00"),
        ])
        self.assert_passed(result)
        self.assertIn("ordered by 'updatedAt'", result.stdout)

    def test_instants_differing_past_microseconds_are_distinct(self):
        result = _run([
            _entry(version="1.0", updatedAt="2026-03-15T10:00:00.1234567Z"),
            _entry(version="1.1", updatedAt="2026-03-15T10:00:00.1234568Z"),
        ])
        self.assert_passed(result)
        self.assertIn("ordered by 'updatedAt'", result.stdout)

    def test_trailing_fraction_zeros_are_the_same_instant(self):
        result = _run([
            _entry(version="1.0", updatedAt="2026-03-15T10:00:00.5Z"),
            _entry(version="1.1", updatedAt="2026-03-15T10:00:00.500Z"),
        ])
        self.assert_passed(result)
        self.assertIn("same 'updatedAt'", result.stdout)

    def test_non_string_version_is_an_error(self):
        for value in (None, 1):
            for entries in ([_entry(version=value)], [_entry(version=value), _entry(version="1.0.0")]):
                with self.subTest(value=value, count=len(entries)):
                    result = _run(entries)
                    self.assert_failed(result)
                    self.assertIn("MUST be a string", result.stdout)
                    self.assertNotIn("has no 'version'", result.stdout)

    def test_non_rfc3339_timestamps_warn(self):
        for value in ("20260315T100000Z", "2026-W11-7T10:00:00Z", "2026-13-15T10:00:00Z"):
            with self.subTest(value=value):
                result = _run([
                    _entry(version="1.0", updatedAt="2026-03-15T10:00:00Z"),
                    _entry(version="1.1", updatedAt=value),
                ])
                self.assert_passed(result)
                self.assertIn("no valid 'updatedAt'", result.stdout)

    def test_semver_pattern_rejects_near_misses(self):
        for version in ("01.0.0", "1.0", "1.0.0-", "1.0.0+", "v1.0.0", "1.0.0\n", "１.0.0"):
            with self.subTest(version=version):
                result = _run([_entry(version=version), _entry(version="2.0.0")])
                self.assert_passed(result)
                self.assertIn("cannot be ordered", result.stdout)


if __name__ == "__main__":
    unittest.main()
