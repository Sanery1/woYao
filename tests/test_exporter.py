"""Exercise the default one-command export, including user-file protection."""
from pathlib import Path
import subprocess
import tempfile
import unittest

EXPORTER = Path(__file__).resolve().parents[1] / 'scripts/export_pdf.cjs'


class ExporterTests(unittest.TestCase):
    def test_plain_markdown_exports_pair_and_image_without_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_dir = root / 'source'
            source_dir.mkdir()
            image = source_dir / 'assets' / 'figure.svg'
            image.parent.mkdir()
            image.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="30"><text x="1" y="20">Local image</text></svg>', encoding='utf-8')
            source = source_dir / 'plain.md'
            original = '---\ndest: forbidden.pdf\n---\n# Plain document\n\n## A useful section\n\n![Local](assets/figure.svg)\n'
            source.write_text(original, encoding='utf-8')
            output = root / 'output'
            command = ['node', str(EXPORTER), str(source), '--output-dir', str(output)]
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=90)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((output / 'plain.md').read_text(encoding='utf-8'), original)
            self.assertEqual((output / 'assets/figure.svg').read_bytes(), image.read_bytes())
            pdf = output / 'plain.pdf'
            self.assertTrue(pdf.read_bytes().startswith(b'%PDF-'))
            self.assertFalse((root / 'forbidden.pdf').exists())
            previous = pdf.read_bytes()
            retry = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=90)
            self.assertNotEqual(retry.returncode, 0)
            self.assertIn('Existing file preserved', retry.stderr)
            self.assertEqual(pdf.read_bytes(), previous)

    def test_failure_keeps_source_and_produces_no_final_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'broken.md'
            source.write_text('# Broken\n\n![Missing](missing.svg)\n', encoding='utf-8')
            output = root / 'output'
            result = subprocess.run(['node', str(EXPORTER), str(source), '--output-dir', str(output)], capture_output=True, text=True, encoding='utf-8', timeout=90)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(source.exists())
            self.assertFalse((output / 'broken.pdf').exists())


if __name__ == '__main__':
    unittest.main()
