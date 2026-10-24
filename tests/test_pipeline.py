"""Behavior tests for file preservation, build provenance and resource boundaries."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_document import prose_and_headings, resource_path, sha256, validate
from publish_document import publish


VERSION = (Path(__file__).resolve().parents[1] / "VERSION").read_text(encoding="utf-8").strip()
META = f"- **Skill 版本：** woYao v{VERSION}\n\n"


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.candidate = self.root / "candidate"
        self.candidate.mkdir()
        self.source = self.candidate / "topic.md"
        self.source.write_text(META + "# Topic\n\n## Mechanism\n\nCandidate text.\n", encoding="utf-8")
        self.image = self.candidate / "assets" / "figure.svg"
        self.image.parent.mkdir()
        self.image.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        self.build = self.root / "build"
        self.build.mkdir()
        (self.build / "document.pdf").write_bytes(b"%PDF-1.7\nCandidate fixture")
        self.output = self.root / "output"
        self.refresh_manifest()

    def refresh_manifest(self):
        self.info = {"skill_version": VERSION, "source": self.source.name, "source_sha256": sha256(self.source),
                     "headings": prose_and_headings(self.source.read_text(encoding="utf-8"))[1],
                     "images": [{"source": "assets/figure.svg", "sha256": sha256(self.image)}],
                     "pdf": {"file": "document.pdf", "sha256": sha256(self.build / "document.pdf")},
                     "structure_relaxed": True}
        (self.build / "build-manifest.json").write_text(json.dumps(self.info), encoding="utf-8")

    def test_publishes_pair_and_images(self):
        result = publish(self.source, self.build, self.output)
        self.assertEqual(result["status"], "PUBLISHED")
        self.assertEqual((self.output / "topic.md").read_bytes(), self.source.read_bytes())
        self.assertEqual((self.output / "topic.pdf").read_bytes(), (self.build / "document.pdf").read_bytes())
        self.assertEqual((self.output / "assets/figure.svg").read_bytes(), self.image.read_bytes())

    def test_conflict_preserves_existing_file(self):
        self.output.mkdir()
        (self.output / "topic.md").write_bytes(b"User work")
        with self.assertRaises(FileExistsError):
            publish(self.source, self.build, self.output)
        self.assertEqual((self.output / "topic.md").read_bytes(), b"User work")
        self.assertFalse((self.output / "topic.pdf").exists())

    def test_source_image_and_pdf_changes_rejected(self):
        for target in [self.source, self.image, self.build / "document.pdf"]:
            with self.subTest(target=target.name):
                original = target.read_bytes()
                target.write_bytes(original + b" changed")
                with self.assertRaises(ValueError):
                    publish(self.source, self.build, self.output, True)
                self.assertFalse((self.output / "topic.md").exists())
                target.write_bytes(original)

    def test_failed_second_replace_restores_original_pair(self):
        self.output.mkdir()
        (self.output / "topic.md").write_bytes(b"Old markdown")
        (self.output / "topic.pdf").write_bytes(b"Old PDF")
        real_replace = os.replace
        def fail_pdf_once(src, dst):
            if Path(src).name == "new-1":
                raise OSError("Simulated PDF write failure")
            return real_replace(src, dst)
        with patch("publish_document.os.replace", side_effect=fail_pdf_once):
            with self.assertRaises(OSError):
                publish(self.source, self.build, self.output, True)
        self.assertEqual((self.output / "topic.md").read_bytes(), b"Old markdown")
        self.assertEqual((self.output / "topic.pdf").read_bytes(), b"Old PDF")

    def test_update_preserves_unrelated_files(self):
        publish(self.source, self.build, self.output)
        unrelated = self.output / "my-notes.txt"
        unrelated.write_bytes(b"Keep")
        self.source.write_text(META + "# Topic\n\nRevised document\n", encoding="utf-8")
        self.refresh_manifest()
        publish(self.source, self.build, self.output, True)
        self.assertEqual(unrelated.read_bytes(), b"Keep")
        self.assertEqual((self.output / "topic.md").read_bytes(), self.source.read_bytes())

    def test_image_paths_cannot_escape(self):
        outside = self.root / "outside.svg"
        outside.write_text("outside", encoding="utf-8")
        for uri in ["../outside.svg", "%2e%2e/outside.svg", "https://example.org/a.svg", "file:///a.svg", "C:\\a.svg"]:
            with self.subTest(uri=uri), self.assertRaises((ValueError, OSError)):
                resource_path(self.candidate, uri)

    def test_code_headings_are_not_document_headings(self):
        prose, headings = prose_and_headings("# Title\n```md\n## Fake\n```\n## Real\n")
        self.assertEqual([h["text"] for h in headings], ["Title", "Real"])
        self.assertNotIn("Fake", prose)
        with self.assertRaises(ValueError):
            prose_and_headings("```python\nprint('incomplete')")

    def test_report_version_is_required_even_for_relaxed_structure(self):
        self.source.write_text("# No version\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Skill 版本"):
            validate(self.source, relaxed=True)

    def test_report_version_must_match_build(self):
        self.info["skill_version"] = "0.0.0"
        (self.build / "build-manifest.json").write_text(json.dumps(self.info), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "version differs"):
            publish(self.source, self.build, self.output)
        self.assertFalse(self.output.exists())

    def test_historical_build_uses_recorded_version(self):
        self.source.write_text(self.source.read_text(encoding="utf-8").replace(VERSION, "0.15.0"), encoding="utf-8")
        self.refresh_manifest()
        self.info["skill_version"] = "0.15.0"
        manifest = self.build / "build-manifest.json"
        manifest.write_text(json.dumps(self.info), encoding="utf-8")
        self.assertEqual(validate(self.source, manifest, relaxed=True)["status"], "PASS")
        with self.assertRaisesRegex(ValueError, "installed Skill"):
            validate(self.source, relaxed=True)

    def test_default_contract_is_enforced(self):
        with self.assertRaises(ValueError):
            validate(self.source)


if __name__ == "__main__":
    unittest.main()
