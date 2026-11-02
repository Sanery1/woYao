#!/usr/bin/env node
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const {build} = require('./render_knowledge.cjs');
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const within = (root, target) => {const rel=path.relative(root,target); return rel!== '..'&&!rel.startsWith('..'+path.sep)&&!path.isAbsolute(rel);};

async function exportPdf(args) {
  const source=fs.realpathSync(args.source), output=path.resolve(args.outputDir);
  if(path.extname(source).toLowerCase()!=='.md')throw new Error('Input must be a Markdown .md file');
  const pdfName=path.basename(source,'.md')+'.pdf';
  const pdfTarget=path.join(output,pdfName);
  if(fs.existsSync(pdfTarget))throw new Error(`Existing file preserved: ${pdfTarget}; use a new report directory`);
  const mdTarget=path.join(output,path.basename(source));
  if(fs.existsSync(mdTarget)&&fs.realpathSync(mdTarget)!==source)throw new Error(`Existing file preserved: ${mdTarget}`);
  const temporary=!args.work;
  const work=args.work?path.resolve(args.work):fs.mkdtempSync(path.join(os.tmpdir(),'woyao-pdf-'));
  const copied=[];
  try {
    await build({source,work});
    const info=JSON.parse(fs.readFileSync(path.join(work,'build-manifest.json'),'utf8'));
    const pdf=path.join(work,info.pdf.file);
    if(hash(source)!==info.source_sha256||hash(pdf)!==info.pdf.sha256)throw new Error('Source or PDF changed during export');
    const entries=[{from:source,to:mdTarget,sha:info.source_sha256},{from:pdf,to:pdfTarget,sha:info.pdf.sha256}];
    for(const image of info.images)entries.push({from:path.join(path.dirname(source),image.source),to:path.join(output,image.source),sha:image.sha256});
    const unique=new Map();
    for(const entry of entries){
      const key=process.platform==='win32'?entry.to.toLowerCase():entry.to;
      if(unique.has(key)&&unique.get(key).from!==entry.from)throw new Error(`Output name collision: ${entry.to}`);
      unique.set(key,entry);
    }
    fs.mkdirSync(output,{recursive:true});
    const root=fs.realpathSync(output);
    for(const entry of unique.values()){
      if(hash(entry.from)!==entry.sha)throw new Error(`Resource changed during export: ${entry.from}`);
      if(fs.existsSync(entry.to)){
        if(fs.realpathSync(entry.to)===fs.realpathSync(entry.from))continue;
        throw new Error(`Existing file preserved: ${entry.to}`);
      }
      if(!within(output,path.resolve(entry.to)))throw new Error('Output resource escapes directory');
      fs.mkdirSync(path.dirname(entry.to),{recursive:true});
      if(!within(root,fs.realpathSync(path.dirname(entry.to))))throw new Error('Output resource directory escapes through a link');
    }
    for(const entry of unique.values()){
      if(fs.existsSync(entry.to)&&fs.realpathSync(entry.to)===fs.realpathSync(entry.from))continue;
      fs.copyFileSync(entry.from,entry.to,fs.constants.COPYFILE_EXCL);
      copied.push(entry);
    }
    return {status:'EXPORTED',markdown:mdTarget,pdf:pdfTarget,renderer:info.renderer,diagrams:info.diagrams.length,equations:info.equations.length};
  } catch(error) {
    for(const entry of copied.reverse())if(fs.existsSync(entry.to)&&hash(entry.to)===entry.sha)fs.unlinkSync(entry.to);
    throw error;
  } finally {
    if(temporary){
      const tempRoot=fs.realpathSync(os.tmpdir()), realWork=fs.realpathSync(work);
      if(within(tempRoot,realWork)&&path.basename(realWork).startsWith('woyao-pdf-'))fs.rmSync(realWork,{recursive:true});
    }
  }
}

function options(argv){
  const result={source:argv.shift()};
  while(argv.length){const arg=argv.shift(); if(arg==='--output-dir'&&argv.length)result.outputDir=argv.shift(); else if(arg==='--work'&&argv.length)result.work=argv.shift(); else throw new Error(`Unknown or incomplete option: ${arg}`);}
  if(!result.source||!result.outputDir)throw new Error('Usage: node export_pdf.cjs report.md --output-dir NEW_REPORT_DIR [--work NEW_BUILD_DIR]');
  return result;
}
if(require.main===module)exportPdf(options(process.argv.slice(2))).then(result=>console.log(JSON.stringify(result))).catch(error=>{console.error(error.message);process.exitCode=1;});
module.exports={exportPdf};
