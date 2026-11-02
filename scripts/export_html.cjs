#!/usr/bin/env node
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const {createRequire} = require('node:module');
const {localImage} = require('./render_knowledge.cjs');
const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function exportHtml({source, output}) {
  source = fs.realpathSync(source);
  if (path.extname(source).toLowerCase() !== '.md') throw new Error('Input must be a Markdown .md file');
  output = path.resolve(output || source.slice(0, -3) + '.html');
  if (path.extname(output).toLowerCase() !== '.html') throw new Error('Output must be an .html file');
  if (fs.existsSync(output)) throw new Error(`Existing file preserved: ${output}; choose a new output path`);
  // Use the Markdown parser belonging to the existing pinned PDF dependency.
  const {marked} = createRequire(require.resolve('md-to-pdf/package.json'))('marked');
  const markdown = fs.readFileSync(source, 'utf8').replace(/^\uFEFF/, '').replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, '');
  const toc = [];
  let headingIndex = 0, title = path.basename(source, '.md'), imageCount = 0, mathEngine;
  function math(token) {
    if (!mathEngine) {
      const {mathjax} = require('mathjax-full/js/mathjax.js');
      const {TeX} = require('mathjax-full/js/input/tex.js');
      const {SVG} = require('mathjax-full/js/output/svg.js');
      const {liteAdaptor} = require('mathjax-full/js/adaptors/liteAdaptor.js');
      const {RegisterHTMLHandler} = require('mathjax-full/js/handlers/html.js');
      const {AllPackages} = require('mathjax-full/js/input/tex/AllPackages.js');
      const adaptor = liteAdaptor();
      RegisterHTMLHandler(adaptor);
      mathEngine = {adaptor, document: mathjax.document('', {InputJax:new TeX({packages:AllPackages}), OutputJax:new SVG({fontCache:'none'})})};
    }
    const display = token.type === 'displayMath';
    const html = mathEngine.adaptor.outerHTML(mathEngine.document.convert(token.text, {display}));
    if (html.includes('data-mml-node="merror"')) throw new Error(`Invalid math: ${token.text.slice(0, 120)}`);
    return `<${display ? 'div class="equation"' : 'span class="inline-equation"'}>${html}</${display ? 'div' : 'span'}>`;
  }
  const renderer = new marked.Renderer();
  renderer.html = text => escape(text);
  renderer.heading = (text, level, raw, slugger) => {
    const id = slugger ? slugger.slug(raw) : `section-${++headingIndex}`;
    if (level === 1) title = raw;
    if (level === 2 || level === 3) toc.push({id, level, text});
    return `<h${level} id="${escape(id)}">${text}</h${level}>\n`;
  };
  renderer.image = (href, imageTitle, alt) => {
    const img = localImage(source, href);
    imageCount++;
    return `<span class="figure"><span class="figure-scroll" tabindex="0"><img src="${img.dataURI}" alt="${escape(alt)}"></span><span class="caption">${escape(alt)}</span><button class="enlarge" type="button" hidden>放大查看 ↗</button></span>`;
  };
  renderer.link = (href, linkTitle, text) => /^(?:https?:|mailto:|#)/i.test(href || '') || !/^[a-z][a-z0-9+.-]*:/i.test(href || '')
    ? `<a href="${escape(href || '')}">${text}</a>` : text;
  const codeRenderer = renderer.code.bind(renderer);
  renderer.code = (code, language, escaped) => {
    if ((language || '').trim() === 'mermaid') throw new Error('Render Mermaid to a local SVG and reference it as a Markdown image before HTML export');
    return codeRenderer(code, language, escaped);
  };
  const tableRenderer = renderer.table.bind(renderer);
  renderer.table = (...args) => `<div class="table-scroll">${tableRenderer(...args)}</div>`;
  const body = marked.parse(markdown, {renderer, headerIds:true, mangle:false, extensions: {
    block: [function(text) {const m=/^\$\$[ \t]*\n?([\s\S]+?)\n?\$\$(?:[ \t]*\n|$)/.exec(text); if(m)return {type:'displayMath',raw:m[0],text:m[1].trim()};}],
    inline: [function(text) {const m=/^\$((?:\\.|[^$\n])+?)\$(?!\$)/.exec(text); if(m)return {type:'inlineMath',raw:m[0],text:m[1]};}],
    startBlock:[text=>text.indexOf('$$')], startInline:[text=>text.indexOf('$')],
    renderers:{displayMath:math, inlineMath:math}
  }});
  const css = fs.readFileSync(path.join(__dirname, '../assets/report-html.css'), 'utf8');
  const js = fs.readFileSync(path.join(__dirname, '../assets/report-html.js'), 'utf8');
  const html = `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(title)}</title><style>${css}</style></head><body><a class="skip" href="#main">跳到正文</a><div class="layout"><aside><div class="brand">woYao.</div><details class="toc" open><summary>阅读目录</summary><nav aria-label="阅读目录">${toc.map(t=>`<a class="level-${t.level}" href="#${escape(t.id)}">${t.text}</a>`).join('')}</nav></details></aside><main id="main">${body}</main></div><dialog aria-label="放大图解"><button type="button" autofocus>关闭 ×</button><div class="zoom"></div></dialog><script>${js}</script></body></html>`;
  // Finish all parsing and resource checks before creating a success artifact.
  fs.mkdirSync(path.dirname(output), {recursive:true});
  fs.writeFileSync(output, html, {flag:'wx'});
  return {html:output, markdown:source, images:imageCount};
}

if (require.main === module) {
  try {
    const args = process.argv.slice(2);
    if (args.length !== 1 && !(args.length === 3 && args[1] === '--output')) throw new Error('Usage: node export_html.cjs report.md [--output NEW_FILE.html]');
    console.log(JSON.stringify(exportHtml({source:args[0], output:args[2]})));
  } catch (error) {console.error(error.message); process.exitCode=1;}
}
module.exports = {exportHtml};
