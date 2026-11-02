const toc = document.querySelector('.toc');
if (matchMedia('(max-width:820px)').matches) toc.open = false;
const dialog = document.querySelector('dialog');
document.querySelectorAll('.enlarge').forEach(button => {
  button.hidden = false;
  button.addEventListener('click', () => {
    dialog.querySelector('.zoom').replaceChildren(button.closest('.figure').querySelector('img').cloneNode(true));
    dialog.showModal();
  });
});
dialog.querySelector('button').addEventListener('click', () => dialog.close());
