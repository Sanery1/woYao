#!/usr/bin/env node
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const http = require('node:http');
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
const escape = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function options(argv) {
  const result = {source: argv.shift()};
  while (argv.length) {
    const arg = argv.shift();
    if (arg === '--relaxed') continue;
    if (arg === '--work' && argv.length) result.work = argv.shift();
    else throw new Error(`Unknown or incomplete option: ${arg}`);
  }
  if (!result.source || !result.work) throw new Error('Usage: node render_knowledge.cjs source.md --work NEW_BUILD_DIR');
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


function browserPath(puppeteer) {
  if (process.env.WOYAO_BROWSER_PATH) {
    if (!fs.existsSync(process.env.WOYAO_BROWSER_PATH)) throw new Error('WOYAO_BROWSER_PATH does not exist');
    return process.env.WOYAO_BROWSER_PATH;
  }
  const candidates = [
    process.env.PROGRAMFILES && path.join(process.env.PROGRAMFILES, 'Google/Chrome/Application/chrome.exe'),
    process.env['PROGRAMFILES(X86)'] && path.join(process.env['PROGRAMFILES(X86)'], 'Google/Chrome/Application/chrome.exe'),
    process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, 'Google/Chrome/Application/chrome.exe'),
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser', puppeteer.executablePath()
  ];
  const found = candidates.find(candidate => candidate && fs.existsSync(candidate));
  if (!found) throw new Error('Chrome/Chromium unavailable. Set WOYAO_BROWSER_PATH, or install a Puppeteer Chrome browser once.');
  return found;
}

async function build(args) {
  let puppeteer, convertMdToPdf, defaultConfig, mathjax, TeX, SVG, liteAdaptor, RegisterHTMLHandler, AllPackages, mermaidBundle;
  try {
    puppeteer = require('puppeteer');
    // md-to-pdf 5.2.5's public wrapper lacks finally cleanup on render errors.
    // Its pinned conversion entry lets this adapter own browser/server cleanup.
    ({convertMdToPdf} = require('md-to-pdf/dist/lib/md-to-pdf'));
    ({defaultConfig} = require('md-to-pdf/dist/lib/config'));
    ({mathjax} = require('mathjax-full/js/mathjax.js'));
    ({TeX} = require('mathjax-full/js/input/tex.js'));
    ({SVG} = require('mathjax-full/js/output/svg.js'));
    ({liteAdaptor} = require('mathjax-full/js/adaptors/liteAdaptor.js'));
    ({RegisterHTMLHandler} = require('mathjax-full/js/handlers/html.js'));
    ({AllPackages} = require('mathjax-full/js/input/tex/AllPackages.js'));
    mermaidBundle = path.join(path.dirname(require.resolve('mermaid')), 'mermaid.min.js');
  } catch (error) { throw new Error(`PDF dependency unavailable: ${error.message}. Run npm ci --prefix <skill-dir>/scripts --ignore-scripts --no-audit --no-fund`); }
  const source = fs.realpathSync(args.source), work = path.resolve(args.work);
  if (fs.existsSync(work) && fs.readdirSync(work).length) throw new Error('Build directory must be new or empty; existing files are preserved.');
  fs.mkdirSync(work, {recursive: true});
  const raw = fs.readFileSync(source);
  const markdown = raw.toString('utf8').replace(/^\uFEFF/, '');
  const declared = /\*\*Skill 版本[：:]\*\*\s+woYao v([^\s]+)/.exec(markdown);
  // Frontmatter is document data, never authority to replace output paths/config.
  const body = markdown.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, '');
  const equations = [], diagrams = [], images = [], headings = [];
  const adaptor = liteAdaptor(); RegisterHTMLHandler(adaptor);
  const mathDocument = mathjax.document('', {InputJax:new TeX({packages:AllPackages}), OutputJax:new SVG({fontCache:'none'})});
  function math(token) {
    const display = token.type === 'displayMath';
    const node = mathDocument.convert(token.text, {display});
    if (adaptor.outerHTML(node).includes('data-mml-node="merror"')) throw new Error(`Invalid math: ${token.text.slice(0,120)}`);
    const svgNode = adaptor.childNodes(node).find(child => adaptor.kind(child) === 'svg');
    if (!svgNode) throw new Error('MathJax did not produce SVG');
    const svg = adaptor.outerHTML(svgNode), file = `equation-${equations.length+1}.svg`;
    fs.writeFileSync(path.join(work,file),svg);
    equations.push({source_sha256:hash(token.text),kind:display?'display':'inline',output:file});
    return `<${display?'div class="equation"':'span class="inline-equation"'}>${svg}</${display?'div':'span'}>`;
  }
  const extension = {
    extensions: [
      {name:'displayMath',level:'block',start:text=>text.indexOf('$$'),tokenizer(text){const m=/^\$\$[ \t]*\n?([\s\S]+?)\n?\$\$(?:[ \t]*\n|$)/.exec(text); if(m)return{type:'displayMath',raw:m[0],text:m[1].trim()};},renderer:math},
      {name:'inlineMath',level:'inline',start:text=>text.indexOf('$'),tokenizer(text){const m=/^\$((?:\\.|[^$\n])+?)\$(?!\$)/.exec(text); if(m)return{type:'inlineMath',raw:m[0],text:m[1]};},renderer:math}
    ],
    walkTokens(token) {if(token.type==='heading')headings.push({level:token.depth,text:token.text});},
    renderer: {
      html(text) {return /^<!--\s*\/?woyao:metadata\s*-->\s*$/.test(text.trim()) ? text : escape(text);},
      code(code, language) {
        if((language||'').trim()!=='mermaid')return false;
        const index=diagrams.length+1;
        diagrams.push({index,source_sha256:hash(code),output:`figure-${index}.svg`});
        return `<div class="figure" data-diagram="${index}">${escape(code)}</div>`;
      },
      image(href,title,text) {
        const img=localImage(source,href);
        images.push({source:img.relative.replaceAll(path.sep,'/'),sha256:img.sha256});
        return `<img src="${img.dataURI}" alt="${escape(text)}">`;
      },
      link(href,title,text) {return /^(?:javascript|data|file):/i.test(href||'')?text:`<a href="${escape(href||'')}">${text}</a>`;}
    }
  };
  const title = /^#\s+(.+)$/m.exec(body)?.[1] || path.basename(source,'.md');
  const config = {...defaultConfig,basedir:work,port:0,dest:path.join(work,'document.pdf'),
    document_title:title,body_class:['markdown-body'],page_media_type:'print',
    stylesheet:[path.join(__dirname,'../assets/notes-light.css')],marked_extensions:[extension],
    pdf_options:{format:'A4',printBackground:true,preferCSSPageSize:true,displayHeaderFooter:true,
      margin:{top:'19mm',bottom:'19mm',left:'20mm',right:'20mm'},
      headerTemplate:`<div style="font-size:8px;color:#738399;width:100%;margin:0 20mm">woYao · ${escape(title)}</div>`,
      footerTemplate:'<div style="font-size:9px;color:#738399;width:100%;text-align:right;margin:0 20mm"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'},
    script:[{path:mermaidBundle},{type:'module',content:`
      try {
        const meta=[...document.body.childNodes].find(n=>n.nodeType===8 && n.textContent.trim()==='woyao:metadata');
        let list=meta?.nextSibling; while(list && list.nodeType!==1)list=list.nextSibling;
        if(list?.tagName==='UL')list.classList.add('doc-meta');
        mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'base',fontFamily:'Microsoft YaHei, Noto Sans CJK SC, sans-serif',flowchart:{htmlLabels:false},themeVariables:{primaryColor:'#f4f7fb',primaryBorderColor:'#b5c6d8',primaryTextColor:'#243448',lineColor:'#738399',fontSize:'16px'}});
        for(const el of document.querySelectorAll('[data-diagram]')){
          const {svg}=await mermaid.render('woyaoFigure'+el.dataset.diagram,el.textContent); el.innerHTML=svg;
          const drawing=el.querySelector('svg'); drawing.style.width=drawing.viewBox.baseVal.width+'px';
        }
        await document.fonts.ready; await Promise.all([...document.images].map(img=>img.decode()));
        for(const table of document.querySelectorAll('table')){
          if(table.getBoundingClientRect().height<=320)table.style.breakInside='avoid';
        }
        for(const figure of document.querySelectorAll('.figure')){
          const caption=figure.nextElementSibling;
          if(caption?.tagName==='P' && /^图\\s*\\d/.test(caption.textContent.trim())){
            const wrap=document.createElement('div'); wrap.className='figure-wrap';
            figure.before(wrap); wrap.append(figure,caption);
          }
        }
        document.documentElement.dataset.woyaoReady='true';
      } catch(error) {document.documentElement.dataset.woyaoError=String(error);}
    `}]
  };
  let server,browser;
  try {
    // The converter needs a document origin; no workspace files are served.
    server=http.createServer((request,response)=>{response.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});response.end('<!doctype html><html></html>');});
    await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
    config.port=server.address().port;
    browser=await puppeteer.launch({executablePath:browserPath(puppeteer),headless:true});
    const controlledBrowser={newPage:async()=>{
      const page=await browser.newPage();
      await page.setRequestInterception(true);
      page.on('request',req=>{const u=new URL(req.url()); if(['about:','data:','blob:'].includes(u.protocol)||(u.hostname==='localhost'&&u.port===String(config.port)))req.continue(); else req.abort();});
      return new Proxy(page,{get(target,key){
        if(key==='pdf')return async opts=>{
          await page.waitForFunction(()=>document.documentElement.dataset.woyaoReady||document.documentElement.dataset.woyaoError,{timeout:30000});
          const error=await page.evaluate(()=>document.documentElement.dataset.woyaoError);
          if(error)throw new Error(`Diagram/image rendering failed: ${error}`);
          const overflow=await page.evaluate(()=>[...document.querySelectorAll('pre,table,.figure,.equation')].filter(el=>el.scrollWidth>el.clientWidth+3).map(el=>el.textContent.slice(0,100)));
          if(overflow.length)throw new Error(`Content exceeds page width: ${JSON.stringify(overflow)}`);
          const figures=await page.$$eval('[data-diagram]',els=>els.map(el=>el.innerHTML));
          figures.forEach((svg,i)=>fs.writeFileSync(path.join(work,diagrams[i].output),svg));
          fs.writeFileSync(path.join(work,'rendered.html'),await page.content());
          return page.pdf(opts);
        };
        const value=Reflect.get(target,key,target); return typeof value==='function'?value.bind(target):value;
      }});
    }};
    await convertMdToPdf({content:body},config,{browser:controlledBrowser});
  } finally {
    if(browser)await browser.close();
    if(server&&server.listening)await new Promise((resolve,reject)=>server.close(error=>error?reject(error):resolve()));
  }
  const pdf=fs.readFileSync(config.dest);
  const manifest={schema_version:3,skill_version:declared?.[1]||null,source:path.basename(source),source_sha256:hash(raw),title,headings,diagrams,equations,images,
    pdf:{file:'document.pdf',sha256:hash(pdf),size_bytes:pdf.length},renderer:'md-to-pdf / MathJax / Mermaid',structure_relaxed:true,
    verification:{external_claims:false,visual_review:false,cross_host:false}};
  fs.writeFileSync(path.join(work,'build-manifest.json'),JSON.stringify(manifest,null,2));
  return{build:work,diagrams:diagrams.length,equations:equations.length,pdf_bytes:pdf.length};
}

if(require.main===module)build(options(process.argv.slice(2))).then(result=>console.log(JSON.stringify(result))).catch(error=>{console.error(error.message);process.exitCode=1;});
module.exports={localImage,build};
