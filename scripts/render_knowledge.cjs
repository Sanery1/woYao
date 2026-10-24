#!/usr/bin/env node
'use strict';
// Local candidate builder. Publishing is a separate, hash-checked operation.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
const escape = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function options(argv) {
  const result = { source: argv.shift(), relaxed: false };
  while (argv.length) {
    const arg = argv.shift();
    if (arg === '--relaxed') result.relaxed = true;
    else if (arg === '--work' && argv.length) result.work = argv.shift();
    else throw new Error(`Unknown or incomplete option: ${arg}`);
  }
  if (!result.source || !result.work) throw new Error('Usage: node render_knowledge.cjs source.md --work NEW_BUILD_DIR [--relaxed]');
  return result;
}

function localImage(source, uri) {
  if (/^(?:[a-z][a-z0-9+.-]*:|[\\/])/i.test(uri)) throw new Error(`Image must be a local relative path: ${uri}`);
  const rel = decodeURIComponent(uri);
  const root = fs.realpathSync(path.dirname(source));
  const target = fs.realpathSync(path.resolve(root, rel));
  const relative = path.relative(root, target);
  if (relative.startsWith('..' + path.sep) || relative === '..' || path.isAbsolute(relative)) throw new Error(`Image escapes document directory: ${uri}`);
  const mime = {'.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.gif':'image/gif'}[path.extname(target).toLowerCase()];
  if (!mime || !fs.statSync(target).isFile()) throw new Error(`Unsupported image: ${uri}`);
  const data = fs.readFileSync(target);
  return { relative, sha256: hash(data), dataURI: `data:${mime};base64,${data.toString('base64')}` };
}

async function build(args) {
  let marked, chromium, mathjax, TeX, SVG, liteAdaptor, RegisterHTMLHandler, AllPackages, mermaidBundle;
  try {
    ({ Marked: marked } = require('marked'));
    ({ chromium } = require('playwright'));
    ({ mathjax } = require('mathjax-full/js/mathjax.js'));
    ({ TeX } = require('mathjax-full/js/input/tex.js'));
    ({ SVG } = require('mathjax-full/js/output/svg.js'));
    ({ liteAdaptor } = require('mathjax-full/js/adaptors/liteAdaptor.js'));
    ({ RegisterHTMLHandler } = require('mathjax-full/js/handlers/html.js'));
    ({ AllPackages } = require('mathjax-full/js/input/tex/AllPackages.js'));
    mermaidBundle = path.join(path.dirname(require.resolve('mermaid')), 'mermaid.min.js');
    if (!fs.existsSync(mermaidBundle)) throw new Error('Mermaid browser bundle not found');
  } catch (error) {
    throw new Error(`Renderer dependency unavailable: ${error.message}. See references/visuals-and-pdf.md`);
  }
  const source = fs.realpathSync(args.source);
  const work = path.resolve(args.work);
  if (fs.existsSync(work) && fs.readdirSync(work).length) throw new Error('Build directory must be new or empty; existing files are preserved.');
  fs.mkdirSync(work, { recursive: true });
  const raw = fs.readFileSync(source);
  const markdown = raw.toString('utf8').replace(/^\uFEFF/, '');
  const skillVersion = fs.readFileSync(path.join(__dirname, '..', 'VERSION'), 'utf8').trim();
  const reportVersions = [...markdown.split(/^## /m)[0].matchAll(/^- \*\*Skill 版本[：:]\*\* woYao v([^\s]+)\s*$/gm)];
  if (reportVersions.length !== 1 || reportVersions[0][1] !== skillVersion) throw new Error(`Report must declare Skill 版本: woYao v${skillVersion} before its first H2`);
  const body = markdown.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, '');
  const diagrams = [], equations = [], images = [], headings = [];
  const adaptor = liteAdaptor();
  RegisterHTMLHandler(adaptor);
  const mathDocument = mathjax.document('', {InputJax: new TeX({packages: AllPackages}), OutputJax: new SVG({fontCache:'none'})});
  function math(tex, display) {
    const container = mathDocument.convert(tex, {display});
    const markup = adaptor.outerHTML(container);
    if (/data-mml-node="merror"/.test(markup)) throw new Error(`Invalid math: ${tex.slice(0, 120)}`);
    // Serialize the outer node: stretchy delimiters can contain nested SVGs.
    const svgNode = adaptor.childNodes(container).find(node => adaptor.kind(node) === 'svg');
    if (!svgNode) throw new Error('MathJax did not produce an outer SVG');
    const svg = adaptor.outerHTML(svgNode);
    const file = `equation-${equations.length + 1}.svg`;
    fs.writeFileSync(path.join(work, file), svg);
    equations.push({source_sha256: hash(tex), kind: display ? 'display' : 'inline', output: file});
    return `<${display ? 'div' : 'span'} class="${display ? 'equation' : 'inline-equation'}">${svg}</${display ? 'div' : 'span'}>`;
  }
  const parser = new marked({ gfm: true, breaks: false });
  parser.use({
    extensions: [
      {name:'displayMath', level:'block', start: text => text.indexOf('$$'),
        tokenizer(text) {const m = /^\$\$[ \t]*\n?([\s\S]+?)\n?\$\$(?:[ \t]*\n|$)/.exec(text); if (m) return {type:'displayMath', raw:m[0], text:m[1].trim()};},
        renderer: token => math(token.text, true)},
      {name:'inlineMath', level:'inline', start: text => text.indexOf('$'),
        tokenizer(text) {const m = /^\$((?:\\.|[^$\n])+?)\$(?!\$)/.exec(text); if (m) return {type:'inlineMath',raw:m[0],text:m[1]};},
        renderer: token => math(token.text, false)}
    ],
    walkTokens(token) {if (token.type === 'heading') headings.push({level:token.depth,text:token.text});},
    renderer: {
      html(token) {return /^<!--\s*\/?woyao:metadata\s*-->\s*$/.test(token.text.trim()) ? token.text : escape(token.text);},
      code(token) {
        if ((token.lang || '').trim() === 'mermaid') {
          const index = diagrams.length + 1;
          diagrams.push({index, source:token.text,source_sha256:hash(token.text),output:`figure-${index}.svg`});
          return `<div class="figure" data-diagram="${index}"></div>`;
        }
        return `<pre><code>${escape(token.text)}</code></pre>`;
      },
      image(token) {
        const image = localImage(source, token.href);
        images.push({source: image.relative.replaceAll(path.sep, '/'),sha256:image.sha256});
        return `<img src="${image.dataURI}" alt="${escape(token.text)}">`;
      },
      link(token) {
        const href = token.href || '';
        const text = this.parser.parseInline(token.tokens);
        if (/^(?:javascript|data|file):/i.test(href)) return text;
        return `<a href="${escape(href)}">${text}</a>`;
      }
    }
  });
  let html = parser.parse(body);
  const h2 = headings.filter(h => h.level === 2).map(h => h.text);
  if (!args.relaxed && JSON.stringify(h2.slice(-2)) !== JSON.stringify(['oOO!', '参考资料与证据级别'])) throw new Error('Last H2 chapters must be oOO! and 参考资料与证据级别');
  html = html.replace(/<!-- woyao:metadata -->\s*<ul>([\s\S]*?)<\/ul>\s*<!-- \/woyao:metadata -->/, '<ul class="doc-meta">$1</ul>');
  if (html.includes('<!-- woyao:metadata -->')) throw new Error('Metadata must be a closed ordinary Markdown list');
  html = html.replace(/(<(?:div class="figure"[^>]*><\/div>|p><img[^>]+><\/p>))\s*(<p><em>图[\s\S]*?<\/em><\/p>)/g, '<section class="figure-wrap">$1$2</section>');
  const css = fs.readFileSync(path.join(__dirname, '..', 'assets', 'notes-light.css'), 'utf8');
  const title = headings.find(h => h.level === 1)?.text;
  if (!title) throw new Error('Document requires a title');
  const browserOptions = process.env.WOYAO_BROWSER_PATH
    ? {executablePath:process.env.WOYAO_BROWSER_PATH}
    : fs.existsSync(chromium.executablePath()) ? {executablePath:chromium.executablePath()} : {channel:'chrome'};
  const browser = await chromium.launch({headless: true, ...browserOptions});
  let pdfInfo;
  try {
    const page = await browser.newPage({viewport:{width:900,height:1000}});
    await page.route('**/*', route => route.abort());
    await page.setContent(`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>${escape(title)}</title><style>${css}</style></head><body><main>${html}</main></body></html>`);
    if (diagrams.length) {
      await page.addScriptTag({content:fs.readFileSync(mermaidBundle, 'utf8')});
      const rendered = await page.evaluate(async sources => {
        mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'base',fontFamily:'Microsoft YaHei, Noto Sans CJK SC, sans-serif',flowchart:{htmlLabels:false},themeVariables:{primaryColor:'#f4f7fb',primaryBorderColor:'#b5c6d8',primaryTextColor:'#243448',lineColor:'#738399',fontSize:'16px'}});
        const result = [];
        for (let i = 0; i < sources.length; i++) {
          const {svg} = await mermaid.render(`woyaoFigure${i+1}`, sources[i]);
          document.querySelector(`[data-diagram="${i+1}"]`).innerHTML = svg;
          result.push(svg);
        }
        return result;
      }, diagrams.map(d => d.source));
      for (let i = 0; i < rendered.length; i++) fs.writeFileSync(path.join(work, diagrams[i].output), rendered[i]);
    }
    await page.evaluate(async () => {await document.fonts.ready; await Promise.all([...document.images].map(img => img.decode()));});
    const layout = await page.evaluate(() => [...document.querySelectorAll('.figure svg')].map(svg => {
      const box = svg.getBoundingClientRect();
      const view = svg.viewBox.baseVal;
      const scale = Math.min(box.width / view.width, box.height / view.height);
      const fonts = [...svg.querySelectorAll('.nodeLabel, text')].filter(el => el.textContent.trim()).map(el => parseFloat(getComputedStyle(el).fontSize) * scale * 0.75);
      return {min_label_pt: fonts.length ? Math.round(Math.min(...fonts) * 10) / 10 : null};
    }));
    for (let i = 0; i < diagrams.length; i++) Object.assign(diagrams[i], layout[i]);
    const overflow = await page.evaluate(() => [...document.querySelectorAll('pre,table,.figure,.equation')].filter(el => el.scrollWidth > el.clientWidth + 3).map(el => el.textContent.slice(0,100)));
    if (overflow.length) throw new Error(`Content exceeds page width; split wide diagrams/formulas/tables: ${JSON.stringify(overflow)}`);
    fs.writeFileSync(path.join(work, 'rendered.html'), await page.content());
    const pdf = await page.pdf({format:'A4', printBackground:true, preferCSSPageSize:true, displayHeaderFooter:true, margin:{top:'19mm',bottom:'19mm',left:'20mm',right:'20mm'}, headerTemplate:`<div style="font-size:8px;color:#738399;width:100%;margin:0 20mm">woYao · ${escape(title)}</div>`, footerTemplate:'<div style="font-size:9px;color:#738399;width:100%;text-align:right;margin:0 20mm"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'});
    fs.writeFileSync(path.join(work, 'document.pdf'), pdf);
    pdfInfo = {file:'document.pdf',sha256:hash(pdf),size_bytes:pdf.length};
  } finally {await browser.close();}
  const manifest = {schema_version:2,skill_version:skillVersion,source: path.basename(source),source_sha256:hash(raw),title,headings,diagrams:diagrams.map(({source,...rest})=>rest),equations,images,pdf:pdfInfo,renderer:'Marked / Mermaid / MathJax SVG / Chromium',structure_relaxed:args.relaxed,verification:{external_claims:false,visual_review:false,cross_host:false}};
  fs.writeFileSync(path.join(work,'build-manifest.json'), JSON.stringify(manifest,null,2));
  return {build:work,diagrams:diagrams.length,equations:equations.length,pdf_bytes:pdfInfo.size_bytes};
}

if (require.main === module) build(options(process.argv.slice(2))).then(result => console.log(JSON.stringify(result))).catch(error => {console.error(error.message);process.exitCode=1;});
module.exports = {localImage};
