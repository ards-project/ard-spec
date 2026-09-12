#!/usr/bin/env python3

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFORMANCE_TOOL = REPO_ROOT / "conformance" / "bin" / "conformance-test"
EXTENSION_FIXTURE = (
    REPO_ROOT
    / "conformance"
    / "tests"
    / "fixtures"
    / "extension-media-types.json"
)

STANDARD_MEDIA_TYPES = (
    "application/ai-catalog+json",
    "application/agent-card+json",
    "application/a2a-agent-card+json",
    "application/mcp-server-card+json",
    "application/agent-skills+zip",
    "application/agent-skills+gzip",
    'text/markdown; profile="urn:air:agent-skills"',
    "application/ai-registry",
    "application/ai-registry+json",
)

EXTENSION_MEDIA_TYPES = (
    "application/vnd.example.tool-manifest+json",
    "application/install-manifest+json",
    "application/okf-bundle+zip",
    "application/x-example-widget",
    "application/pdf",
    "application/ai-skill+md",
    "application/asm+json",
)

NON_APPLICATION_MEDIA_TYPES = (
    "text/plain",
    "image/png",
    "video/mp4",
    "model/gltf+json",
    "example/example-card+json",
)

MALFORMED_MEDIA_TYPES = (
    "application",
    "application/",
    "/json",
    "application//json",
    "application/ json",
    " application/json",
    "application/json ",
    "application/json;",
    "application/json;charset",
    "application/json; =utf-8",
    "application/json charset=utf-8",
    '"application/json"',
    "application/jsøn",
)


def _entry(media_type, index):
    return {
        "identifier": f"urn:air:media-types.test:fixture:entry-{index}",
        "displayName": f"Media type fixture {index}",
        "type": media_type,
        "url": f"https://media-types.test/artifacts/{index}",
        "representativeQueries": [
            f"find media type fixture {index}",
            f"locate extension artifact {index}",
        ],
    }


def _run_manifest_file(path, *, without_site_packages=True, timeout=10):
    command = [sys.executable]
    if without_site_packages:
        command.append("-S")
    command.extend([str(CONFORMANCE_TOOL), "manifest", str(path)])
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def _run_media_types(media_types, *, timeout=10):
    manifest = {
        "entries": [
            _entry(media_type, index)
            for index, media_type in enumerate(media_types, start=1)
        ]
    }
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "ard.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return _run_manifest_file(path, timeout=timeout)


def _summary_counts(stdout):
    match = re.search(
        r"Validated with 0 critical specification errors and "
        r"(\d+) warnings(?: and (\d+) informational messages)?\.",
        stdout,
    )
    if match is None:
        raise AssertionError(f"Conformance summary was not found in output:\n{stdout}")
    warnings = int(match.group(1))
    infos = int(match.group(2)) if match.group(2) is not None else 0
    return warnings, infos


def _line_containing(stdout, value):
    diagnostic = f"Media type '{value}'"
    for line in stdout.splitlines():
        if diagnostic in line:
            return line
    raise AssertionError(f"No output line contains {value!r}:\n{stdout}")


class MediaTypeDiagnosticTests(unittest.TestCase):
    def assert_passed(self, result):
        self.assertEqual(
            result.returncode,
            0,
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

    def test_all_existing_standard_media_types_remain_silent(self):
        result = _run_media_types(STANDARD_MEDIA_TYPES)

        self.assert_passed(result)
        self.assertEqual(_summary_counts(result.stdout), (0, 0))
        self.assertNotIn("informational messages", result.stdout)
        for media_type in STANDARD_MEDIA_TYPES:
            self.assertNotIn(
                f"Media type '{media_type}'",
                result.stdout,
                f"Unexpected diagnostic for standard type {media_type}",
            )

    def test_profiled_standard_type_accepts_equivalent_http_spelling(self):
        equivalent_types = (
            'text/markdown;profile="urn:air:agent-skills"',
            'Text/Markdown; PROFILE="urn:air:agent-skills"',
        )

        result = _run_media_types(equivalent_types)

        self.assert_passed(result)
        self.assertEqual(_summary_counts(result.stdout), (0, 0))

    def test_standard_base_types_with_extra_parameters_warn_clearly(self):
        parameterized_types = (
            "application/agent-skills+zip; anything=go",
            'application/mcp-server-card+json; profile="example"',
        )

        result = _run_media_types(parameterized_types)

        self.assert_passed(result)
        self.assertEqual(_summary_counts(result.stdout), (2, 0))
        for media_type in parameterized_types:
            self.assertIn(
                "is based on standard discovery type",
                _line_containing(result.stdout, media_type),
            )

    def test_profiled_standard_type_with_extra_parameter_warns_clearly(self):
        media_type = (
            'text/markdown; profile="urn:air:agent-skills"; charset=utf-8'
        )

        result = _run_media_types((media_type,))

        self.assert_passed(result)
        self.assertEqual(_summary_counts(result.stdout), (1, 0))
        line = _line_containing(result.stdout, media_type)
        self.assertIn("is based on standard discovery type", line)
        self.assertIn("unrecognized parameters: charset", line)
        self.assertNotIn("unrecognized parameters: charset, profile", line)

    def test_profiled_standard_type_without_profile_reports_missing_parameter(self):
        media_type = "text/markdown"

        result = _run_media_types((media_type,))

        self.assert_passed(result)
        self.assertEqual(_summary_counts(result.stdout), (1, 0))
        line = _line_containing(result.stdout, media_type)
        self.assertIn(
            'missing required parameters: profile="urn:air:agent-skills"',
            line,
        )
        self.assertNotIn("unrecognized parameters", line)

    def test_application_extension_media_types_are_informational(self):
        result = _run_media_types(EXTENSION_MEDIA_TYPES)

        self.assert_passed(result)
        self.assertEqual(_summary_counts(result.stdout), (0, len(EXTENSION_MEDIA_TYPES)))
        for media_type in EXTENSION_MEDIA_TYPES:
            line = _line_containing(result.stdout, media_type)
            self.assertIn("valid application extension media type", line)
            self.assertNotIn("⚠", line)
            self.assertNotIn("not one of standard discovery types", line)

    def test_deprecated_mcp_media_type_warns_with_replacement(self):
        deprecated_types = (
            "application/mcp-server+json",
            "application/mcp-server+json; charset=utf-8",
        )

        result = _run_media_types(deprecated_types)

        self.assert_passed(result)
        self.assertEqual(_summary_counts(result.stdout), (2, 0))
        for media_type in deprecated_types:
            line = _line_containing(result.stdout, media_type)
            self.assertIn("⚠", line)
            self.assertIn("ADR-0008", line)
            self.assertIn("application/mcp-server-card+json", line)

    def test_similar_mcp_extension_types_are_not_marked_deprecated(self):
        similar_types = (
            "application/mcp-server-card+json",
            "application/x-mcp-server+json",
            "application/mcp-server+xml",
        )

        result = _run_media_types(similar_types)

        self.assert_passed(result)
        self.assertEqual(_summary_counts(result.stdout), (0, 2))
        self.assertNotIn("ADR-0008", result.stdout)

    def test_other_top_level_media_types_keep_existing_warning(self):
        result = _run_media_types(NON_APPLICATION_MEDIA_TYPES)

        self.assert_passed(result)
        self.assertEqual(
            _summary_counts(result.stdout),
            (len(NON_APPLICATION_MEDIA_TYPES), 0),
        )
        for media_type in NON_APPLICATION_MEDIA_TYPES:
            line = _line_containing(result.stdout, media_type)
            self.assertIn("⚠", line)
            self.assertIn("is not one of standard discovery types", line)

    def test_application_word_in_wrong_position_is_not_an_extension(self):
        result = _run_media_types(("applicationx/example", "xapplication/example"))

        self.assert_passed(result)
        self.assertEqual(_summary_counts(result.stdout), (2, 0))
        self.assertNotIn("valid application extension media type", result.stdout)

    def test_malformed_media_types_get_syntax_warnings(self):
        result = _run_media_types(MALFORMED_MEDIA_TYPES)

        self.assert_passed(result)
        self.assertEqual(
            _summary_counts(result.stdout),
            (len(MALFORMED_MEDIA_TYPES), 0),
        )
        self.assertEqual(
            result.stdout.count("is not a valid IANA media type"),
            len(MALFORMED_MEDIA_TYPES),
        )
        self.assertNotIn("valid application extension media type", result.stdout)

    def test_trailing_newline_is_not_accepted_by_media_type_parser(self):
        result = _run_media_types(("application/json\n",))

        self.assert_passed(result)
        self.assertEqual(_summary_counts(result.stdout), (1, 0))
        self.assertIn("is not a valid IANA media type", result.stdout)
        self.assertNotIn("valid application extension media type", result.stdout)

    def test_parameterized_application_extension_is_informational(self):
        media_type = 'application/vnd.example.card+json; version="1"; charset=utf-8'

        result = _run_media_types((media_type,))

        self.assert_passed(result)
        self.assertEqual(_summary_counts(result.stdout), (0, 1))
        line = _line_containing(result.stdout, media_type)
        self.assertIn("valid application extension media type", line)
        self.assertNotIn("⚠", line)

    def test_duplicate_parameter_names_are_malformed(self):
        media_type = (
            'text/markdown; profile="urn:air:agent-skills"; '
            'profile="urn:air:agent-skills"'
        )

        result = _run_media_types((media_type,))

        self.assert_passed(result)
        self.assertEqual(_summary_counts(result.stdout), (1, 0))
        self.assertIn(
            "is not a valid IANA media type",
            _line_containing(result.stdout, media_type),
        )

    def test_truthy_non_string_type_does_not_abort_later_entries(self):
        result = _run_media_types((123, "application/vnd.example.card+json"))

        self.assert_passed(result)
        self.assertEqual(_summary_counts(result.stdout), (1, 1))
        self.assertIn("Media type must be a string", result.stdout)
        self.assertIn(
            "valid application extension media type",
            result.stdout,
        )

    def test_long_invalid_type_finishes_without_pathological_backtracking(self):
        result = _run_media_types(
            ("application/" + ("a!" * 5_000) + "é",),
            timeout=2,
        )

        self.assert_passed(result)
        self.assertEqual(_summary_counts(result.stdout), (1, 0))
        self.assertIn("is not a valid IANA media type", result.stdout)

    def test_neutral_fixture_covers_every_diagnostic_class(self):
        result = _run_manifest_file(EXTENSION_FIXTURE)

        self.assert_passed(result)
        self.assertEqual(_summary_counts(result.stdout), (3, 3))
        self.assertIn(
            "application/mcp-server-card+json",
            EXTENSION_FIXTURE.read_text(encoding="utf-8"),
        )
        self.assertIn("application/vnd.example.tool-manifest+json", result.stdout)
        self.assertIn("application/mcp-server+json", result.stdout)
        self.assertIn("text/x-example-notes", result.stdout)
        self.assertIn("application/ example", result.stdout)

    def test_neutral_fixture_with_json_schema_keeps_diagnostic_counts(self):
        result = _run_manifest_file(
            EXTENSION_FIXTURE,
            without_site_packages=False,
        )

        if "Skipping strict JSON Schema check" in result.stdout:
            if os.environ.get("ARD_REQUIRE_JSONSCHEMA") == "1":
                self.fail("ARD_REQUIRE_JSONSCHEMA=1 but jsonschema did not load")
            self.skipTest("jsonschema is not installed")

        self.assert_passed(result)
        self.assertEqual(_summary_counts(result.stdout), (3, 3))
        self.assertIn("Manifest validates against ArdManifest", result.stdout)

    def test_existing_examples_emit_no_extension_info(self):
        example_paths = sorted(
            (REPO_ROOT / "conformance" / "examples").rglob("*.json")
        )
        self.assertTrue(example_paths)

        for path in example_paths:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                result = _run_manifest_file(path)
                self.assert_passed(result)
                _, infos = _summary_counts(result.stdout)
                self.assertEqual(infos, 0)


if __name__ == "__main__":
    unittest.main()
