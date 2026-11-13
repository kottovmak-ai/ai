// Renders index.html slides to JPEG and assembles a PDF.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname, out = path.join(root, 'out');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.woff2': 'font/woff2', '.woff': 'font/woff', '.jpg': 'image/jpeg', '.png': 'image/png', '.json': 'application/json' };

(async () => {
  fs.mkdirSync(out, { recursive: true });
  const srv = http.createServer((q, r) => {
    const f = path.join(root, decodeURIComponent(q.url.split('?')[0]));
    if (!f.startsWith(root) || !fs.existsSync(f)) { r.writeHead(404); return r.end(); }
    r.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r);
  }).listen(0);
  const url = `http://127.0.0.1:${srv.address().port}/`;
  const br = await chromium.launch();
  const pg = await br.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 });
  pg.on('console', m => console.log('[page]', m.text())); pg.on('pageerror', e => console.log('[err]', e.message));
  await pg.goto(url + 'index.html');
  await pg.waitForFunction(() => document.body.dataset.ready === '1', null, { timeout: 300000 });
  const slides = await pg.$$('.slide'); const imgs = [];
  for (let i = 0; i < slides.length; i++) {
    const f = `out/s${String(i + 1).padStart(2, '0')}.jpg`;
    await slides[i].screenshot({ path: path.join(root, f), type: 'jpeg', quality: 93 }); imgs.push(f);
  }
  const html = `<style>@page{size:1920px 1080px;margin:0}body{margin:0}img{display:block;width:1920px;height:1080px;page-break-after:always}</style>` + imgs.map(f => `<img src="${url}${f}">`).join('');
  const p2 = await br.newPage(); await p2.setContent(html, { waitUntil: 'load' });
  await p2.pdf({ path: path.join(root, 'Сословно-представительная монархия.pdf'), width: '1920px', height: '1080px', printBackground: true });
  // contact sheet for review
  const p3 = await br.newPage({ viewport: { width: 1930, height: 1100 } });
  await p3.setContent(`<body style="margin:0;background:#333;display:grid;grid-template-columns:repeat(3,640px);gap:5px">` + imgs.map(f => `<img src="${url}${f}" width="640" height="360">`).join(''), { waitUntil: 'load' });
  await p3.screenshot({ path: path.join(out, 'sheet.png'), fullPage: true });
  await br.close(); srv.close(); console.log('done', imgs.length);
})();
