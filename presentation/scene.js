import * as T from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const W = 1920, H = 1080, PR = 2;
const renderer = new T.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(PR); renderer.setSize(W, H);
renderer.toneMapping = T.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.15;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = T.PCFSoftShadowMap;
const env = new T.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;

let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;

const M = {
  gold: new T.MeshStandardMaterial({ color: 0xe0ac4a, metalness: 1, roughness: 0.2, side: T.DoubleSide }),
  goldSoft: new T.MeshStandardMaterial({ color: 0xd09a3c, metalness: 1, roughness: 0.38 }),
  marble: new T.MeshPhysicalMaterial({ color: 0xf1e8d8, roughness: 0.42, clearcoat: 0.5, clearcoatRoughness: 0.3 }),
  dark: new T.MeshPhysicalMaterial({ color: 0x0d070c, roughness: 0.55, metalness: 0, clearcoat: 0.3 }),
  velvet: new T.MeshStandardMaterial({ color: 0x4d0816, roughness: 0.9, side: T.DoubleSide }),
  fur: new T.MeshStandardMaterial({ color: 0xf6f0e6, roughness: 1 }),
  pearl: new T.MeshPhysicalMaterial({ color: 0xfff7ea, roughness: 0.15, clearcoat: 1 }),
  black: new T.MeshStandardMaterial({ color: 0x15101a, roughness: 0.6 }),
};
const gem = c => new T.MeshPhysicalMaterial({ color: c, roughness: 0.05, metalness: 0.2, clearcoat: 1, flatShading: true });
const GEMS = [gem(0xc0112f), gem(0x1746b8), gem(0x0f8a55)];

const mesh = (g, m, x = 0, y = 0, z = 0) => { const o = new T.Mesh(g, m); o.position.set(x, y, z); o.castShadow = true; o.receiveShadow = true; return o; };

function crown() {
  const g = new T.Group();
  g.add(mesh(new T.CylinderGeometry(1, 1, 0.44, 96, 1, true), M.gold, 0, 0.22, 0));
  for (const y of [0.02, 0.44]) { const t = mesh(new T.TorusGeometry(1, 0.06, 20, 96), M.gold, 0, y, 0); t.rotation.x = Math.PI / 2; g.add(t); }
  const fur = mesh(new T.TorusGeometry(1.03, 0.17, 24, 96), M.fur, 0, -0.13, 0); fur.rotation.x = Math.PI / 2; g.add(fur);
  for (let i = 0; i < 16; i++) { const a = i / 16 * Math.PI * 2 + 0.2; g.add(mesh(new T.SphereGeometry(0.05, 12, 12), M.black, Math.cos(a) * 1.19, -0.13 + (i % 2 ? .04 : -.04), Math.sin(a) * 1.19)); }
  for (let i = 0; i < 8; i++) {
    const a = i / 8 * Math.PI * 2 + Math.PI / 8;
    const j = mesh(new T.OctahedronGeometry(0.105, 0), GEMS[i % 3], Math.cos(a) * 1.03, 0.23, Math.sin(a) * 1.03); j.scale.y = 1.25; g.add(j);
    const h = 0.42;
    g.add(mesh(new T.ConeGeometry(0.13, h, 4), M.gold, Math.cos(a) * 1, 0.46 + h / 2, Math.sin(a) * 1));
    g.add(mesh(new T.SphereGeometry(0.07, 20, 20), M.pearl, Math.cos(a) * 1, 0.5 + h, Math.sin(a) * 1));
  }
  for (let i = 0; i < 4; i++) {
    const arch = mesh(new T.TorusGeometry(1, 0.05, 16, 80, Math.PI), M.gold, 0, 0.44, 0); arch.rotation.y = i * Math.PI / 4; g.add(arch);
    for (let k = 1; k < 12; k++) { if (k === 6) continue; const t = k / 12 * Math.PI, r = 1.0;
      const p = new T.Vector3(Math.cos(t) * r, Math.sin(t) * r, 0).applyAxisAngle(new T.Vector3(0, 1, 0), i * Math.PI / 4);
      const out = p.clone().normalize().multiplyScalar(0.07); g.add(mesh(new T.SphereGeometry(0.045, 14, 14), M.pearl, p.x + out.x, p.y + 0.44 + out.y, p.z + out.z)); }
  }
  const cap = mesh(new T.SphereGeometry(0.94, 64, 32, 0, Math.PI * 2, 0, Math.PI / 2), M.velvet, 0, 0.42, 0); cap.scale.y = 0.96; g.add(cap);
  g.add(mesh(new T.SphereGeometry(0.17, 32, 32), M.gold, 0, 1.56, 0));
  g.add(mesh(new RoundedBoxGeometry(0.075, 0.5, 0.075, 3, 0.02), M.gold, 0, 1.93, 0));
  g.add(mesh(new RoundedBoxGeometry(0.3, 0.075, 0.075, 3, 0.02), M.gold, 0, 2.0, 0));
  return g;
}

function orb() {
  const g = new T.Group();
  g.add(mesh(new T.SphereGeometry(1, 96, 64), M.gold));
  const b = mesh(new T.TorusGeometry(1.0, 0.075, 20, 96), M.goldSoft); b.rotation.x = Math.PI / 2; g.add(b);
  const v = mesh(new T.TorusGeometry(1.0, 0.075, 20, 96, Math.PI), M.goldSoft); g.add(v);
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; const j = mesh(new T.OctahedronGeometry(0.085, 0), GEMS[i % 3], Math.cos(a) * 1.07, 0, Math.sin(a) * 1.07); g.add(j); }
  g.add(mesh(new T.SphereGeometry(0.14, 24, 24), M.pearl, 0, 1.14, 0));
  g.add(mesh(new RoundedBoxGeometry(0.11, 0.8, 0.11, 3, 0.03), M.gold, 0, 1.6, 0));
  g.add(mesh(new RoundedBoxGeometry(0.5, 0.11, 0.11, 3, 0.03), M.gold, 0, 1.72, 0));
  return g;
}

function column(h, mat = M.marble) {
  const g = new T.Group();
  g.add(mesh(new RoundedBoxGeometry(1, 0.16, 1, 3, 0.03), mat, 0, 0.08, 0));
  g.add(mesh(new T.CylinderGeometry(0.42, 0.47, 0.13, 48), mat, 0, 0.225, 0));
  const shaft = new T.CylinderGeometry(0.31, 0.37, h, 24, 1); g.add(mesh(shaft, mat, 0, 0.29 + h / 2, 0));
  for (let i = 0; i < 24; i++) { const a = i / 24 * Math.PI * 2; const f = mesh(new T.CylinderGeometry(0.03, 0.036, h * 0.94, 8), mat, Math.cos(a) * 0.335, 0.29 + h / 2, Math.sin(a) * 0.335); g.add(f); }
  for (const y of [0.3, 0.29 + h]) { const r = mesh(new T.TorusGeometry(y < 1 ? 0.39 : 0.34, 0.04, 16, 64), M.gold, 0, y, 0); r.rotation.x = Math.PI / 2; g.add(r); }
  g.add(mesh(new T.CylinderGeometry(0.46, 0.32, 0.18, 48), mat, 0, 0.38 + h, 0));
  g.add(mesh(new RoundedBoxGeometry(1, 0.14, 1, 3, 0.03), mat, 0, 0.54 + h, 0));
  g.userData.top = 0.61 + h;
  return g;
}

function dust(scene, n, box, c = [0, 0, 0]) {
  for (let i = 0; i < n; i++) {
    const r = 0.03 + rnd() * 0.09;
    scene.add(mesh(new T.SphereGeometry(r, 20, 20), rnd() > .3 ? M.gold : M.pearl, c[0] + (rnd() - .5) * box[0], c[1] + (rnd() - .5) * box[1], c[2] + (rnd() - .5) * box[2]));
  }
}
function ring(r, tube, rot, pos) { const t = mesh(new T.TorusGeometry(r, tube, 24, 160), M.gold, ...pos); t.rotation.set(...rot); return t; }

function base(floorY = null) {
  const s = new T.Scene(); s.environment = env;
  const d = new T.DirectionalLight(0xffe6bd, 2.6); d.position.set(5, 9, 7); d.castShadow = true;
  d.shadow.mapSize.set(4096, 4096); Object.assign(d.shadow.camera, { left: -11, right: 11, top: 9, bottom: -9, near: 1, far: 40 }); d.shadow.radius = 9; d.shadow.bias = -0.0005;
  s.add(d);
  const p = new T.PointLight(0xff3458, 30); p.position.set(-5, 2, 3); s.add(p);
  const p2 = new T.PointLight(0x7f9bff, 25); p2.position.set(6, -2, 5); s.add(p2);
  if (floorY !== null) { const f = new T.Mesh(new T.PlaneGeometry(60, 40), new T.ShadowMaterial({ opacity: 0.45 })); f.rotation.x = -Math.PI / 2; f.position.y = floorY; f.receiveShadow = true; s.add(f); }
  const cam = new T.PerspectiveCamera(28, W / H, 0.1, 100); cam.position.set(0, 1.4, 14); cam.lookAt(0, 0, 0);
  return { s, cam };
}

function draw(id, { s, cam }) {
  renderer.render(s, cam);
  const cv = document.querySelector(`#${id} .gl`); cv.width = W * PR; cv.height = H * PR;
  cv.getContext('2d').drawImage(renderer.domElement, 0, 0);
  s.traverse(o => { if (o.geometry) o.geometry.dispose(); });
}
function label(id, cam, v, cls, html, dy = 0) {
  cam.updateMatrixWorld(); const p = new T.Vector3(...v).project(cam);
  const el = document.createElement('div'); el.className = 'lab ' + cls; el.innerHTML = html;
  el.style.left = ((p.x + 1) / 2 * W) + 'px'; el.style.top = ((1 - p.y) / 2 * H + dy) + 'px';
  document.querySelector(`#${id} .labels`).appendChild(el);
}

// 1 — crown
{ const b = base(); const c = crown(); c.scale.setScalar(1.72); c.position.set(3.5, -1.75, 0); c.rotation.set(0.2, 0.5, -0.1); b.s.add(c);
  b.s.add(ring(2.7, 0.02, [1.25, 0.25, 0], [3.5, -0.3, 0])); b.s.add(ring(3.15, 0.012, [1.4, -0.3, 0], [3.5, -0.3, 0]));
  dust(b.s, 30, [6.5, 6.5, 5], [3.4, 0.3, -1]); draw('s1', b); }

// 2 — orb
{ const b = base(-2.45); const o = orb(); o.scale.setScalar(1.55); o.position.set(4.25, -0.75, 0); o.rotation.set(0.1, 0.5, 0.12); b.s.add(o);
  const ped = mesh(new T.CylinderGeometry(1.25, 1.45, 0.3, 64), M.dark, 4.25, -2.3, 0); b.s.add(ped);
  b.s.add(ring(2.6, 0.018, [1.3, 0.3, 0], [4.25, -0.4, 0])); dust(b.s, 22, [5.5, 6, 4], [4.2, 0.3, -1]); draw('s2', b); }

// 3 — decorative
{ const b = base(); b.s.add(ring(1.3, 0.025, [1.15, 0.4, 0], [4.9, 2.7, 0]));
  const c = crown(); c.scale.setScalar(0.5); c.position.set(4.9, 2.15, 0); c.rotation.set(0.25, 0.4, -0.15); b.s.add(c);
  dust(b.s, 10, [3.5, 1.4, 2], [4.4, 2.7, -1]); draw('s3', b); }

// 4 — Europe pedestals
{ const b = base(-1.5);
  const data = [['1188', 'Кортесы', 'Леон и Кастилия', 0.7], ['1265', 'Парламент', 'Англия', 0.95], ['1302', 'Генеральные штаты', 'Франция', 1.2], ['1493', 'Вальный сейм', 'Польша', 1.45], ['1549', 'Земский собор', 'Россия', 1.9]];
  b.s.add(mesh(new RoundedBoxGeometry(11.4, 0.16, 2.0, 3, 0.04), M.dark, 0, -1.42, 0));
  data.forEach((d, i) => { const x = -4.6 + i * 2.3, ru = i === 4, h = d[3];
    const col = column(h, ru ? M.gold : M.marble); col.position.set(x, -1.34, 0); col.scale.setScalar(ru ? 1.12 : 1); b.s.add(col);
    let top = -1.34 + col.userData.top * (ru ? 1.12 : 1);
    if (ru) { const c = crown(); c.scale.setScalar(0.42); c.position.set(x, top + 0.1, 0); c.rotation.y = 0.4; b.s.add(c); top += 1.0; }
    else { b.s.add(mesh(new T.SphereGeometry(0.2, 32, 32), M.gold, x, top + 0.2, 0)); top += 0.42; }
    label('s4', b.cam, [x, top, 0], 'year', d[0], -22);
    label('s4', b.cam, [x, -1.5, 1.0], 'txt big', `<b>${d[1]}</b>${d[2]}`, 34); });
  draw('s4', b); }

// 5 — three pillars under the crown
{ const b = base(-2.3); const X = 3.75;
  b.s.add(mesh(new RoundedBoxGeometry(4.5, 0.2, 1.8, 3, 0.04), M.dark, X, -2.2, 0));
  ['I', 'II', 'III'].forEach((n, i) => { const c = column(2.0); c.position.set(X - 1.45 + i * 1.45, -2.1, 0); b.s.add(c); });
  b.s.add(mesh(new RoundedBoxGeometry(4.3, 0.3, 1.4, 3, 0.05), M.marble, X, 0.66, 0));
  b.s.add(mesh(new RoundedBoxGeometry(3.7, 0.14, 1.15, 3, 0.04), M.gold, X, 0.88, 0));
  const c = crown(); c.scale.setScalar(0.68); c.position.set(X, 1.06, 0); c.rotation.y = 0.45; b.s.add(c);
  ['I', 'II', 'III'].forEach((n, i) => label('s5', b.cam, [X - 1.45 + i * 1.45, -2.3, 0.9], 'tag', n, 52));
  label('s5', b.cam, [X, 2.6, 0], 'tag', 'Царь', -14);
  dust(b.s, 12, [4.6, 4.5, 2], [X, 0.6, -1.5]); draw('s5', b); }

// 6 — timeline
{ const b = base(-1.5);
  const ev = [['1549', 'Первый собор', 'Иван IV начинает реформы', 0.9], ['1566', 'Ливонская война', 'Собор решает: продолжать', 1.2], ['1598', 'Борис Годунов', 'Собор избирает царя', 1.6],
    ['1613', 'Михаил Романов', 'Избрание династии — пик влияния соборов', 2.4], ['1649', 'Соборное уложение', 'Свод законов страны', 2.0], ['1653', 'Последний собор', 'Принятие Войска Запорожского в подданство', 1.05], ['далее', 'Угасание', 'Лишь совещания с отдельными сословиями', 0.3]];
  b.s.add(mesh(new RoundedBoxGeometry(11.6, 0.14, 1.9, 3, 0.04), M.dark, 0, -1.43, 0));
  ev.forEach((e, i) => { const x = -4.8 + i * 1.6, h = e[3], last = i === 6;
    const m = mesh(new RoundedBoxGeometry(0.95, h, 0.95, 4, 0.06), last ? M.marble : (i === 3 ? M.gold : M.goldSoft), x, -1.35 + h / 2, 0); if (last) m.rotation.z = 0.05; b.s.add(m);
    if (last) for (let k = 0; k < 7; k++) { const d = mesh(new T.DodecahedronGeometry(0.08 + rnd() * 0.1, 0), M.marble, x + (rnd() - .5) * 1.2, -1.27, 0.4 + rnd() * 0.5); d.rotation.set(rnd() * 3, rnd() * 3, 0); b.s.add(d); }
    label('s6', b.cam, [x, -1.35 + h, 0], 'year', e[0], -22);
    label('s6', b.cam, [x, -1.5, 0.95], 'txt', `<b>${e[1]}</b>${e[2]}`, 30); });
  draw('s6', b); }

// 7 — broken column
{ const b = base(-2.3); const X = 3.5;
  b.s.add(mesh(new RoundedBoxGeometry(5.4, 0.2, 2.6, 3, 0.04), M.dark, X, -2.2, 0));
  const c = column(1.5); c.position.set(X - 0.9, -2.1, 0);
  c.children.slice(-2).forEach(o => c.remove(o)); c.children.filter(o => o.material === M.gold && o.position.y > 1).forEach(o => c.remove(o)); b.s.add(c);
  const jag = mesh(new T.ConeGeometry(0.33, 0.5, 7), M.marble, X - 0.98, -0.2, 0.03); jag.rotation.z = 0.25; b.s.add(jag);
  const piece = new T.Group(); piece.add(mesh(new T.CylinderGeometry(0.31, 0.33, 1.7, 24), M.marble));
  for (let i = 0; i < 24; i++) { const a = i / 24 * Math.PI * 2; piece.add(mesh(new T.CylinderGeometry(0.03, 0.03, 1.6, 8), M.marble, Math.cos(a) * 0.32, 0, Math.sin(a) * 0.32)); }
  piece.add(mesh(new T.CylinderGeometry(0.46, 0.32, 0.18, 48), M.marble, 0, 0.94, 0)); piece.add(mesh(new RoundedBoxGeometry(1, 0.14, 1, 3, 0.03), M.marble, 0, 1.1, 0));
  piece.rotation.set(0.25, 0.5, -1.4); piece.position.set(X + 0.9, -1.66, 0.5); b.s.add(piece);
  const cr = crown(); cr.scale.setScalar(0.62); cr.position.set(X + 1.5, 0.3, -0.5); cr.rotation.set(0.3, 0.3, -0.45); b.s.add(cr);
  for (let k = 0; k < 14; k++) { const d = mesh(new T.DodecahedronGeometry(0.07 + rnd() * 0.13, 0), M.marble, X - 1.9 + rnd() * 3.6, -2.02, 0.5 + rnd() * 0.7); d.rotation.set(rnd() * 3, rnd() * 3, 0); b.s.add(d); }
  dust(b.s, 14, [5, 3, 2], [X + 0.6, 1.2, -1]); draw('s7', b); }

// 8 — decorative fallen crown
{ const b = base(); const c = crown(); c.scale.setScalar(0.6); c.position.set(5.3, 2.35, 0); c.rotation.set(0.35, 0.4, -0.55); b.s.add(c);
  b.s.add(ring(1.6, 0.02, [1.1, 0.4, 0], [5.3, 2.9, -1])); dust(b.s, 12, [4, 1.6, 2], [4.4, 2.9, -1]); draw('s8', b); }

// 9 — decorative
{ const b = base(); b.s.add(ring(1.5, 0.04, [1.0, 0.5, 0], [5.4, 2.9, -1])); b.s.add(ring(1.0, 0.03, [0.4, 1.1, 0], [5.4, 2.9, -1]));
  const o = orb(); o.scale.setScalar(0.42); o.position.set(5.4, 2.55, -1); o.rotation.set(0.1, 0.5, 0.15); b.s.add(o);
  dust(b.s, 10, [4, 1.6, 2], [4.3, 2.9, -1]); draw('s9', b); }

// 10 — crown finale
{ const b = base(); const c = crown(); c.scale.setScalar(1.5); c.position.set(4.3, -1.3, 0); c.rotation.set(0.24, -0.35, 0.08); b.s.add(c);
  for (let i = 0; i < 3; i++) b.s.add(ring(2.3 + i * 0.4, 0.014, [1.2 + i * 0.12, 0.2 - i * 0.25, 0], [4.3, -0.1, 0]));
  dust(b.s, 26, [5, 6, 4], [4.3, 0.4, -1.5]); draw('s10', b); }

await document.fonts.ready;
document.body.dataset.ready = '1';
