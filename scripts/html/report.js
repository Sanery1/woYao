'use strict';
(async () => {
  const page = document.documentElement;
  const toc = document.querySelector('.toc');
  if (toc && matchMedia('(max-width:820px)').matches) toc.open = false;
  const dialog = document.querySelector('dialog');
  document.querySelectorAll('.enlarge').forEach(button => {
    if (!dialog || typeof dialog.showModal !== 'function') return;
    button.hidden = false;
    button.addEventListener('click', () => {
      dialog.querySelector('.zoom').replaceChildren(button.closest('.figure').querySelector('img').cloneNode(true));
      dialog.showModal();
    });
  });
  if (dialog) dialog.querySelector('button').addEventListener('click', () => dialog.close());
  const printDetails = new Map();
  window.addEventListener('beforeprint', () => document.querySelectorAll('main details').forEach(details => {
    if (!printDetails.has(details)) printDetails.set(details, details.open);
    details.open = true;
  }));
  window.addEventListener('afterprint', () => {printDetails.forEach((open, details) => {details.open = open;}); printDetails.clear();});
  let errors = 0;
  const diagrams = [...document.querySelectorAll('pre.mermaid')];
  if (diagrams.length && typeof mermaid !== 'undefined') {
    // Rendering is awaited explicitly so errors remain visible and testable.
    mermaid.initialize({startOnLoad:false, securityLevel:'strict', htmlLabels:false, flowchart:{htmlLabels:false}, secure:['secure','securityLevel','startOnLoad','maxTextSize','maxEdges','suppressErrorRendering','htmlLabels','flowchart'], suppressErrorRendering:true});
  }
  for (const [index, node] of diagrams.entries()) {
    const source = node.textContent;
    try {
      if (typeof mermaid === 'undefined') throw new Error('Mermaid 脚本未加载');
      const result = await mermaid.render(`woyao-diagram-${index}`, source);
      const container = document.createElement('div');
      container.className = 'diagram-rendered';
      container.innerHTML = result.svg;
      node.replaceWith(container);
    } catch (error) {
      errors++;
      node.dataset.woyaoError = 'true';
      const status = node.parentElement.querySelector('.diagram-status');
      if (status) {status.hidden = false; status.textContent = `图解渲染失败，以下保留源码：${error.message || error}`;}
    }
  }
  page.dataset.woyaoReady = errors ? 'error' : 'ready';
  page.dataset.woyaoErrors = String(errors);
  window.woyaoReady = true;
})().catch(error => {
  document.documentElement.dataset.woyaoReady = 'error';
  document.documentElement.dataset.woyaoErrors = '1';
  const message = document.createElement('p');
  message.className = 'diagram-status';
  message.textContent = `交互初始化失败：${error.message || error}`;
  document.querySelector('main').prepend(message);
  window.woyaoReady = true;
});
