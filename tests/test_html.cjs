'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {exportHtml} = require('../scripts/export_html.cjs');
const root = fs.mkdtempSync(path.join(os.tmpdir(), 'woyao-html-test-'));
const source = path.join(root, 'plain.md');
fs.writeFileSync(path.join(root, 'figure.svg'), '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 40"><text x="5" y="25">结果</text></svg>');
fs.writeFileSync(source, '# 普通文章\n\n## 核心\n\n正文 $x^2$。\n\n$$\n\\frac{1}{2}\n$$\n\n![结果](figure.svg)\n\n|输入|输出|\n|---|---|\n|1|2|\n\n<script>alert(1)</script>\n');
const result = exportHtml({source});
const html = fs.readFileSync(result.html, 'utf8');
assert.equal(result.images, 1);
assert.match(html, /data:image\/svg\+xml;base64,/);
assert.match(html, /data-mml-node="mfrac"/);
assert.match(html, /class="table-scroll"/);
assert.ok(!html.includes('<script>alert(1)</script>'));
assert.throws(() => exportHtml({source}), /Existing file preserved/);
assert.equal(fs.readFileSync(result.html, 'utf8'), html);
for (const [name, body, pattern] of [
  ['missing', '![图](missing.svg)', /ENOENT/],
  ['remote', '![图](https://example.com/a.png)', /local relative/],
  ['escape', '![图](../outside.svg)', /escapes|ENOENT/],
  ['mermaid', '```mermaid\ngraph TD; A-->B\n```', /local SVG/],
  ['math', '$$\n\\frac{\n$$', /Invalid math/],
]) {
  const input = path.join(root, name + '.md');
  fs.writeFileSync(input, body);
  assert.throws(() => exportHtml({source:input}), pattern);
  assert.equal(fs.existsSync(path.join(root, name + '.html')), false);
}
console.log('HTML checks passed: ordinary Markdown, math, image embedding, tables, raw HTML, overwrite preservation, failure without artifact.');
console.log('Fixtures retained: ' + root);
