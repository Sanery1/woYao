"""Run the real optional renderer; needs its Node dependencies and a browser."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

RENDERER = Path(__file__).resolve().parents[1] / "scripts/render_knowledge.cjs"


class RendererTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source.md"
        self.build = self.root / "build"

    def run_renderer(self, markdown):
        version = (RENDERER.parents[1] / "VERSION").read_text(encoding="utf-8").strip()
        markdown = f"- **Skill 版本：** woYao v{version}\n\n" + markdown
        self.source.write_text(markdown, encoding="utf-8")
        return subprocess.run(["node", str(RENDERER), str(self.source), "--work", str(self.build), "--relaxed"], capture_output=True, text=True, encoding="utf-8", timeout=90)

    def test_real_diagrams_math_code_and_literal_html(self):
        result = self.run_renderer('''# 中文渲染验证

Inline $x^2$.

$$
\\frac{a}{b}
$$

```python
value = "$not_math$"
```

```mermaid
flowchart TD
  A[输入] --> B[输出]
```

```mermaid
sequenceDiagram
  A->>B: request
  B-->>A: response
```

```mermaid
stateDiagram-v2
  [*] --> Ready
  Ready --> [*]
```

<script>throw new Error("Source script executed")</script>
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((self.build / "build-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["diagrams"]), 3)
        self.assertEqual(len(manifest["equations"]), 2)
        self.assertEqual(manifest["source_sha256"], hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.assertTrue((self.build / "document.pdf").read_bytes().startswith(b"%PDF-"))
        html = (self.build / "rendered.html").read_text(encoding="utf-8")
        self.assertIn('&lt;script&gt;throw new Error(', html)
        self.assertIn('value = "$not_math$"', html)

    def test_nested_math_svg_is_complete(self):
        result = self.run_renderer(r"""# Math regression

Inline $x^2$.

$$
K(d)=k_1\left(1-b+b\frac{|d|}{\overline L}\right)
$$

$$
\left(\frac{1}{\frac{a}{b}}\right)=z
$$
""")
        self.assertEqual(result.returncode, 0, result.stderr)
        equations = sorted(self.build.glob("equation-*.svg"))
        self.assertEqual(len(equations), 3)
        roots = [ET.parse(svg).getroot() for svg in equations]
        self.assertTrue(all(root.tag.endswith("svg") for root in roots))
        self.assertIn('data-c="29"', equations[1].read_text(encoding="utf-8"))
        self.assertIn('data-c="1D467"', equations[2].read_text(encoding="utf-8"))

    def test_wrong_or_missing_version_stops_build(self):
        for metadata in ["", "- **Skill 版本：** woYao v0.0.0\n\n"]:
            with self.subTest(metadata=metadata):
                self.source.write_text(metadata + "# Version test\n", encoding="utf-8")
                result = subprocess.run(["node", str(RENDERER), str(self.source), "--work", str(self.build), "--relaxed"], capture_output=True, text=True, encoding="utf-8", timeout=90)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Report must declare", result.stderr)
                self.assertFalse((self.build / "document.pdf").exists())

    def test_invalid_mermaid_cannot_produce_success_manifest(self):
        result = self.run_renderer("# Bad diagram\n\n```mermaid\nunknownDiagram\n X Y Z\n```\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.build / "build-manifest.json").exists())
        self.assertFalse((self.build / "document.pdf").exists())

    def test_invalid_math_is_an_error(self):
        result = self.run_renderer("# Bad math\n\n$$\n\\frac{1}{\n$$\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid math", result.stderr)
        self.assertFalse((self.build / "document.pdf").exists())

    def test_missing_image_is_an_error(self):
        result = self.run_renderer("# Missing\n\n![image](assets/missing.svg)\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.build / "document.pdf").exists())

    def test_remote_image_is_not_fetched(self):
        result = self.run_renderer("# Remote\n\n![image](https://example.org/image.svg)\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("local relative", result.stderr)

    def test_existing_build_files_are_preserved(self):
        self.build.mkdir()
        previous = self.build / "document.pdf"
        previous.write_bytes(b"Previous build")
        result = self.run_renderer("# New candidate\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(previous.read_bytes(), b"Previous build")


if __name__ == "__main__":
    unittest.main()
