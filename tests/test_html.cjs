'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {exportHtml} = require('../scripts/html/export.cjs');
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
assert.ok(!html.includes('data-woyao-mermaid'));
assert.match(html, /@page\{size:A4;margin:20mm\}/);
assert.throws(() => exportHtml({source}), /Existing file preserved/);
assert.equal(fs.readFileSync(result.html, 'utf8'), html);
for (const [name, body, pattern] of [
  ['missing', '![图](missing.svg)', /ENOENT/],
  ['remote', '![图](https://example.com/a.png)', /local relative/],
  ['escape', '![图](../outside.svg)', /escapes|ENOENT/],
  ['mermaid-config', '```mermaid\n%%{init: {"securityLevel":"loose"}}%%\ngraph TD; A-->B\n```', /configuration directives/],
  ['mermaid-frontmatter', '```mermaid\n---\nconfig: {}\n---\ngraph TD; A-->B\n```', /front matter/],
  ['math', '$$\n\\frac{\n$$', /Invalid math/],
]) {
  const input = path.join(root, name + '.md');
  fs.writeFileSync(input, body);
  assert.throws(() => exportHtml({source:input}), pattern);
  assert.equal(fs.existsSync(path.join(root, name + '.html')), false);
}
const diagram = path.join(root, 'diagram.md');
fs.writeFileSync(diagram, '# 图\n\n```mermaid\nflowchart LR\n A[输入] --> B[结果]\n```\n\n<details><summary>答案要点</summary>\n\n隐藏答案。\n\n</details>\n\n<!-- calc: demo -->\n');
const diagramResult = exportHtml({source:diagram});
const diagramHtml = fs.readFileSync(diagramResult.html, 'utf8');
assert.equal(diagramResult.diagrams, 1);
assert.match(diagramHtml, /<pre class="mermaid">/);
assert.match(diagramHtml, /<script data-woyao-mermaid>/);
assert.match(diagramHtml, /securityLevel:'strict'/);
assert.ok(diagramHtml.includes('<details><summary>答案要点</summary>'));
assert.ok(!diagramHtml.includes('<!-- calc: demo -->'));
assert.ok(diagramHtml.includes('A[输入] --&gt; B[结果]'));
const hostile = path.join(root, 'hostile.md');
fs.writeFileSync(hostile, '# 安全\n\n<details onclick="alert(1)"><summary onmouseover="alert(2)">x</summary></details>\n\n[x](javascript:alert%281%29)\n\n```mermaid\nflowchart LR\n A["</script><script>window.bad=1</script>"] --> B[结果]\n```\n');
const hostileHtml = fs.readFileSync(exportHtml({source:hostile}).html, 'utf8');
assert.ok(!hostileHtml.includes('<details onclick='));
assert.ok(!hostileHtml.includes('<summary onmouseover='));
assert.ok(!hostileHtml.includes('href="javascript:'));
assert.ok(!hostileHtml.includes('<script>window.bad=1</script>'));
const repeat = path.join(root, 'repeat.md');
fs.writeFileSync(repeat, '# Repeat\n\n## Section\n\n$x^2$\n');
const first = fs.readFileSync(exportHtml({source:repeat}).html, 'utf8');
const second = fs.readFileSync(exportHtml({source:repeat, output:path.join(root, 'repeat-2.html')}).html, 'utf8');
assert.equal(first, second);
assert.ok(!first.includes('data-woyao-mermaid'));
console.log('HTML checks passed: Markdown, math, images, tables, escaping, protected output, failure without artifact, offline Mermaid, details, print CSS and repeated calls.');
console.log('Fixtures retained: ' + root);
