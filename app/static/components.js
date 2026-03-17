// loads header and footer into html files

async function loadComponent(id, file) {
  const res = await fetch(file);
  const html = await res.text();
  document.getElementById(id).innerHTML = html;
}

loadComponent('header-placeholder', '/static/header.html');
loadComponent('footer-placeholder', '/static/footer.html');

function openPanel() {
    document.getElementById('accountPanel').classList.add('open');
    document.getElementById('overlay').classList.add('open');
}

function closePanel() {
    document.getElementById('accountPanel').classList.remove('open');
    document.getElementById('overlay').classList.remove('open');
    document.getElementById('accountBtn').focus();
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closePanel();
});