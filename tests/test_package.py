import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("package_skill", Path(__file__).resolve().parents[1] / "scripts/package_skill.py")
packager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packager)


class PackageTests(unittest.TestCase):
    def test_self_contained_small_payload_and_preservation(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "woyao"
            total, count = packager.package(output)
            self.assertLess(total, 200_000)
            self.assertGreater(count, 10)
            self.assertTrue((output / "scripts/html/package-lock.json").is_file())
            self.assertFalse((output / "evals").exists())
            self.assertFalse((output / "tests").exists())
            self.assertFalse((output / "scripts/html/node_modules").exists())
            original = (output / "SKILL.md").read_bytes()
            with self.assertRaisesRegex(ValueError, "Existing path preserved"):
                packager.package(output)
            self.assertEqual((output / "SKILL.md").read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
