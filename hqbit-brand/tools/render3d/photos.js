// HQbit showcase photos: a white R36S showing each theme, in different settings.  photo.html?s=<scene>
import { THREE, PURPLE, makeRenderer, environment, composer, keycapGeometry, roundedBox, glowPlane, loadFonts, done } from './common.js';
import { makeR36S } from './r36s.js';

const params = new URLSearchParams(location.search);
const W = +params.get('w') || 1920, H = +params.get('h') || 1200;
const SCR = (p) => `../../showcase/screens/${p}`;

// ---------------------------------------------------------------- helpers
function canvasTex(w, h, draw, repeat = 1) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat, repeat);
  return t;
}
function rand(seed) { let s = seed; return () => (s = (s * 16807) % 2147483647) / 2147483647; }

function woodTexture() {
  return canvasTex(1024, 1024, (g, w, h) => {
    const R = rand(7);
    const planks = 4;
    for (let p = 0; p < planks; p++) {
      const y0 = (p * h) / planks, base = [150 + R() * 25, 98 + R() * 18, 62 + R() * 12];
      g.fillStyle = `rgb(${base.join(',')})`; g.fillRect(0, y0, w, h / planks);
      for (let i = 0; i < 160; i++) {
        const y = y0 + R() * (h / planks), a = 0.04 + R() * 0.08, dark = R() < 0.6;
        g.strokeStyle = dark ? `rgba(70,40,20,${a})` : `rgba(255,220,180,${a})`;
        g.lineWidth = 0.6 + R() * 2.2;
        g.beginPath(); g.moveTo(0, y);
        for (let x = 0; x <= w; x += 32) g.lineTo(x, y + Math.sin(x / (90 + R() * 40) + p) * 3 + (R() - 0.5) * 1.5);
        g.stroke();
      }
      g.fillStyle = 'rgba(40,22,10,0.55)'; g.fillRect(0, y0, w, 2);
    }
  }, 2);
}

function fabricTexture(color, tone) {
  return canvasTex(512, 512, (g, w, h) => {
    g.fillStyle = color; g.fillRect(0, 0, w, h);
    const R = rand(3);
    for (let i = 0; i < 9000; i++) { g.fillStyle = `rgba(${tone},${R() * 0.08})`; g.fillRect(R() * w, R() * h, 2, 2); }
  }, 6);
}

function floor(mat, size = 160) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(size, size), mat);
  m.rotation.x = -Math.PI / 2; m.receiveShadow = true;
  return m;
}

function keyLight(color, intensity, pos, area = 16) {
  const l = new THREE.DirectionalLight(color, intensity);
  l.position.set(...pos); l.castShadow = true;
  l.shadow.mapSize.set(4096, 4096); l.shadow.radius = 8; l.shadow.bias = -0.0003; l.shadow.normalBias = 0.02;
  Object.assign(l.shadow.camera, { left: -area, right: area, top: area, bottom: -area, near: 0.5, far: 120 });
  return l;
}

/** device lying on a surface, face up. yaw rotates it on the table. */
function lay(dev, yaw = 0, x = 0, z = 0) {
  const g = new THREE.Group();
  dev.rotation.set(-Math.PI / 2, 0, 0);
  dev.position.y = 1.0;
  g.add(dev); g.rotation.y = yaw; g.position.set(x, 0, z);
  return g;
}

function mug(color = 0xf3f1f6) {
  const pts = [];
  for (let i = 0; i <= 20; i++) { const t = i / 20; pts.push(new THREE.Vector2(3.4 + 0.2 * Math.sin(t * Math.PI), t * 8.5)); }
  pts.push(new THREE.Vector2(3.1, 8.5), new THREE.Vector2(3.1, 0.6), new THREE.Vector2(0, 0.6));
  const g = new THREE.Group();
  const mat = new THREE.MeshPhysicalMaterial({ color, roughness: 0.25, clearcoat: 1 });
  const body = new THREE.Mesh(new THREE.LatheGeometry(pts, 64), mat); body.castShadow = body.receiveShadow = true;
  const coffee = new THREE.Mesh(new THREE.CircleGeometry(3.1, 48), new THREE.MeshPhysicalMaterial({ color: 0x2b1609, roughness: 0.15, clearcoat: 1 }));
  coffee.rotation.x = -Math.PI / 2; coffee.position.y = 7.4;
  const handle = new THREE.Mesh(new THREE.TorusGeometry(1.9, 0.45, 20, 48, Math.PI * 1.2), mat);
  handle.position.set(3.5, 4.4, 0); handle.rotation.z = -Math.PI * 0.6; handle.castShadow = true;
  g.add(body, coffee, handle);
  return g;
}

function notebook(color) {
  const g = new THREE.Group();
  const cover = new THREE.Mesh(roundedBox(15, 0.7, 21, 0.25, 4), new THREE.MeshPhysicalMaterial({ color, roughness: 0.75, sheen: 0.4 }));
  cover.castShadow = cover.receiveShadow = true;
  const band = new THREE.Mesh(roundedBox(0.5, 0.74, 21.02, 0.05, 2), new THREE.MeshStandardMaterial({ color: 0x15121c, roughness: 0.6 }));
  band.position.x = 5.6;
  g.add(cover, band);
  return g;
}

function vhsTape(label = 'HQBIT · E-180') {
  const g = new THREE.Group();
  const shell = new THREE.Mesh(roundedBox(18.7, 2.5, 10.2, 0.3, 4), new THREE.MeshPhysicalMaterial({ color: 0x141317, roughness: 0.55, clearcoat: 0.3 }));
  shell.castShadow = shell.receiveShadow = true;
  const lbl = new THREE.Mesh(new THREE.PlaneGeometry(12, 4.6), new THREE.MeshStandardMaterial({ roughness: 0.8, map: canvasTex(600, 230, (c, w, h) => {
    c.fillStyle = '#f4f1e6'; c.fillRect(0, 0, w, h);
    c.fillStyle = '#612bfe'; c.fillRect(0, 0, w, 46);
    c.fillStyle = '#fff'; c.font = '700 30px UB'; c.fillText('HQBIT', 18, 34);
    c.fillStyle = '#2a2833'; c.font = '600 40px JB'; c.fillText(label.split(' · ')[1] || '', 18, 130);
    c.strokeStyle = '#c9c4b8'; c.lineWidth = 2; for (let y = 160; y < 220; y += 22) { c.beginPath(); c.moveTo(18, y); c.lineTo(w - 18, y); c.stroke(); }
  }) }));
  lbl.rotation.x = -Math.PI / 2; lbl.position.set(-1.8, 2.52, -1.6);
  const win = new THREE.Mesh(new THREE.PlaneGeometry(6, 2.2), new THREE.MeshPhysicalMaterial({ color: 0x2c2a33, roughness: 0.1, clearcoat: 1 }));
  win.rotation.x = -Math.PI / 2; win.position.set(-1.8, 2.52, 2.6);
  g.add(shell, lbl, win);
  return g;
}

function pencil() {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.38, 15, 6), new THREE.MeshPhysicalMaterial({ color: PURPLE, roughness: 0.45, clearcoat: 0.6 }));
  const tip = new THREE.Mesh(new THREE.ConeGeometry(0.38, 1.6, 6), new THREE.MeshStandardMaterial({ color: 0xe8cfa6, roughness: 0.8 }));
  tip.position.y = -8.3; tip.rotation.x = Math.PI;
  const lead = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.5, 12), new THREE.MeshStandardMaterial({ color: 0x222222 }));
  lead.position.y = -9.05; lead.rotation.x = Math.PI;
  const end = new THREE.Mesh(new THREE.CylinderGeometry(0.39, 0.39, 1.2, 24), new THREE.MeshStandardMaterial({ color: 0xc9c9cf, metalness: 0.8, roughness: 0.3 }));
  end.position.y = 8;
  g.add(body, tip, lead, end);
  g.traverse((o) => { if (o.isMesh) o.castShadow = true; });
  g.rotation.z = Math.PI / 2; g.position.y = 0.4;
  return g;
}

function overlay(html) {
  const d = document.createElement('div');
  d.style.cssText = 'position:absolute;inset:0;pointer-events:none;color:#fff;font-family:IN';
  d.innerHTML = html;
  document.getElementById('stage').appendChild(d);
}

function caption({ name, ver, line, chips, dark = true, x = 'left', file }) {
  const col = dark ? '#fff' : '#160a2e', sub = dark ? 'rgba(255,255,255,.82)' : 'rgba(22,10,46,.78)';
  const logo = dark ? 'hqbit-logo-white.svg' : 'hqbit-logo-black.svg';
  const chipCss = dark ? 'background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.3)' : 'background:rgba(22,10,46,.07);border:1px solid rgba(22,10,46,.2)';
  return `<img src="../../logo/${logo}" style="position:absolute;left:${W * 0.05}px;top:${H * 0.07}px;width:${W * 0.12}px">
  <div style="position:absolute;${x}:${W * 0.05}px;bottom:${H * 0.08}px;max-width:${W * 0.36}px;color:${col}">
   <div style="font:400 ${W * 0.0105}px Silkscreen,monospace;color:${dark ? '#E0FE3B' : '#612BFE'}">${ver}</div>
   <div style="font:800 ${W * 0.05}px/1 UB;letter-spacing:-.02em;margin-top:${W * 0.006}px">${name}</div>
   <div style="font:400 ${W * 0.0125}px/1.45 IN;color:${sub};margin-top:${W * 0.01}px">${line}</div>
   <div style="display:flex;flex-wrap:wrap;gap:${W * 0.005}px;margin-top:${W * 0.012}px">${chips.map((c) => `<span style="font:500 ${W * 0.0085}px JB;${chipCss};padding:${W * 0.004}px ${W * 0.007}px;border-radius:99px">${c}</span>`).join('')}</div>
  </div>
  <div style="position:absolute;right:${W * 0.05}px;top:${H * 0.075}px;font:500 ${W * 0.0085}px JB;letter-spacing:.14em;color:${sub}">R36S &amp; CLONES · ARKOS · dARKOS · EMUELEC</div>`;
}

const bloom = (r, scene, cam, s = 0.18) => composer(r, scene, cam, W, H, { strength: s, radius: 0.5, threshold: 0.97 }).render();

// ---------------------------------------------------------------- 1. Volta: morning desk
async function volta() {
  const r = makeRenderer(W, H); r.toneMappingExposure = 0.95;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x2a1b12);
  scene.environment = environment(r, 0.04); scene.environmentIntensity = 0.55;
  scene.fog = new THREE.Fog(0x2a1b12, 70, 140);
  const cam = new THREE.PerspectiveCamera(28, W / H, 0.1, 300);
  cam.position.set(-3, 29, 27); cam.lookAt(6, 0, -0.5);
  scene.add(floor(new THREE.MeshPhysicalMaterial({ map: woodTexture(), roughness: 0.55, clearcoat: 0.25, clearcoatRoughness: 0.5 })));
  scene.add(lay(await makeR36S(SCR('volta/system-horizontal-dark.png')), -0.42, 9, 1));
  const m = mug(); m.position.set(25, 0, 2); scene.add(m);
  const nb = notebook(0x6d4bd8); nb.position.set(-17, 0.35, 12); nb.rotation.y = 0.5; scene.add(nb);
  scene.add(keyLight(0xffe2c0, 2.6, [-30, 40, -10], 40));
  const fill = new THREE.HemisphereLight(0xfff2e6, 0x3a2414, 0.5); scene.add(fill);
  bloom(r, scene, cam);
  overlay(caption({ name: 'Volta', ver: 'V1.1', line: 'A dark and light dashboard theme with glossy cards, tick-ring gauges and dot-matrix numbers.', chips: ['13 colour schemes', '3 carousel layouts', '163 system logos'] }));
}

// ---------------------------------------------------------------- 2. NeonGlow: night, glossy floor, neon rim light
async function neonglow() {
  const r = makeRenderer(W, H); r.toneMappingExposure = 1.0;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x07040f);
  scene.environment = environment(r, 0.04); scene.environmentIntensity = 0.25;
  const cam = new THREE.PerspectiveCamera(30, W / H, 0.1, 300);
  cam.position.set(-4, 8, 34); cam.lookAt(5, 6, 0);
  scene.fog = new THREE.Fog(0x07040f, 38, 80);
  scene.add(floor(new THREE.MeshPhysicalMaterial({ color: 0x050309, roughness: 0.22, metalness: 0.3, clearcoat: 1, clearcoatRoughness: 0.08 })));
  const dev = await makeR36S(SCR('neonglow/system-vertical.png'), { screenGlow: 1.05 });
  dev.position.set(8, 6.55, 0); dev.rotation.set(-0.12, -0.42, 0);
  scene.add(dev);
  // stand under the device
  const stand = new THREE.Mesh(roundedBox(5, 1.2, 4, 0.3), new THREE.MeshPhysicalMaterial({ color: 0x15121c, roughness: 0.4, clearcoat: 0.5 }));
  stand.position.set(8.2, 0, 1.2); stand.rotation.y = -0.42; stand.castShadow = true; scene.add(stand);
  const pink = new THREE.PointLight(0xff3d9a, 260, 60, 1.6); pink.position.set(22, 12, -10); scene.add(pink);
  const cyan = new THREE.PointLight(0x3dd6ff, 220, 60, 1.6); cyan.position.set(-8, 14, -14); scene.add(cyan);
  const purple = new THREE.PointLight(PURPLE, 200, 50, 1.4); purple.position.set(4, 20, 18); scene.add(purple);
  const k = keyLight(0xd9ccff, 0.8, [-10, 30, 25], 30); scene.add(k);
  // neon tubes in the background, out of focus
  for (const [x, y, z, c, s] of [[-26, 14, -40, '#ff3d9a', 30], [30, 22, -46, '#3dd6ff', 34], [6, 30, -60, '#7a4bff', 46], [-40, 30, -70, '#612bfe', 50]]) {
    const gp = glowPlane(s, c, 0.7); gp.rotation.x = 0; gp.position.set(x, y, z); scene.add(gp);
  }
  bloom(r, scene, cam, 0.4);
  overlay(caption({ name: 'NeonGlow', ver: 'V1.2', line: 'Glass tiles that glow in each system’s own colour, on a deep dark canvas or a clean light one.', chips: ['13 colour schemes', '4 system layouts', '194 systems'] }));
}

// ---------------------------------------------------------------- 3. VCR OSD: coffee table, VHS tapes, TV-blue light
async function vcr() {
  const r = makeRenderer(W, H); r.toneMappingExposure = 1.0;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x060a1c);
  scene.environment = environment(r, 0.04); scene.environmentIntensity = 0.3;
  scene.fog = new THREE.Fog(0x060a1c, 55, 120);
  const cam = new THREE.PerspectiveCamera(30, W / H, 0.1, 300);
  cam.position.set(14, 30, 30); cam.lookAt(6, 0, 0);
  scene.add(floor(new THREE.MeshPhysicalMaterial({ map: fabricTexture('#2b2a3d', '255,255,255'), roughness: 0.95, sheen: 1, sheenColor: 0x6c79ff })));
  scene.add(lay(await makeR36S(SCR('vcr/system-snes.png')), 0.32, 11, 3));
  const t1 = vhsTape('HQBIT · SP 120'); t1.position.set(-6, 0, -15); t1.rotation.y = -0.25; scene.add(t1);
  const t2 = vhsTape('HQBIT · E-180'); t2.position.set(-7.5, 2.5, -15.8); t2.rotation.y = -0.1; scene.add(t2);
  const t3 = vhsTape('HQBIT · LP 240'); t3.position.set(27, 0, -6); t3.rotation.y = 0.75; scene.add(t3);
  const tv = new THREE.RectAreaLight ? null : null; // keep simple: blue light from an off-screen TV
  const blue = new THREE.PointLight(0x2b54ff, 900, 120, 1.6); blue.position.set(-30, 20, -30); scene.add(blue);
  const k = keyLight(0x9fb2ff, 1.6, [-25, 35, -20], 40); scene.add(k);
  const warm = new THREE.PointLight(0xffb36b, 120, 60, 1.6); warm.position.set(30, 18, 25); scene.add(warm);
  bloom(r, scene, cam, 0.3);
  overlay(caption({ name: 'VCR OSD', ver: 'V1', line: 'The blue screen of an old VCR, with full-colour pixel consoles, a custom pixel font and a tape-counter timeline.', chips: ['153 systems', 'Custom pixel font', '3 colour sets', 'CRT scanlines'] }));
}

// ---------------------------------------------------------------- 4. DeskOS: top-down flat lay on paper
async function deskos() {
  const r = makeRenderer(W, H); r.toneMappingExposure = 0.82;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xe9e4f2);
  scene.environment = environment(r, 0.04); scene.environmentIntensity = 0.5;
  const cam = new THREE.PerspectiveCamera(24, W / H, 0.1, 300);
  cam.position.set(6, 50, 7); cam.lookAt(6, 0, 0);
  scene.add(floor(new THREE.MeshPhysicalMaterial({ map: fabricTexture('#ece7f4', '120,100,170'), roughness: 0.95 })));
  scene.add(lay(await makeR36S(SCR('deskos/system-classic.png')), 0.14, 12, 0));
  // keyboard corner (keycaps on a plate) top-left, pencil and a sticky note
  const kb = new THREE.Group();
  const plate = new THREE.Mesh(roundedBox(40, 1.2, 16, 0.8), new THREE.MeshPhysicalMaterial({ color: 0xd8d3e2, roughness: 0.5, metalness: 0.3 }));
  plate.castShadow = plate.receiveShadow = true; kb.add(plate);
  const cap = keycapGeometry(1.75, 0.9, 1.75, { taper: 0.16, dish: 0.02, radius: 0.22 });
  const capMat = new THREE.MeshPhysicalMaterial({ color: 0xf4f1f8, roughness: 0.55 });
  const accent = new THREE.MeshPhysicalMaterial({ color: PURPLE, roughness: 0.55 });
  for (let i = 0; i < 20; i++) for (let j = 0; j < 7; j++) {
    const m = new THREE.Mesh(cap, (i === 17 && j === 2) ? accent : capMat);
    m.position.set(-18 + i * 1.95 + (j % 2) * 0.5, 0.6, -6 + j * 1.95); m.castShadow = m.receiveShadow = true; kb.add(m);
  }
  kb.position.set(-14, 0, -17.5); kb.rotation.y = 0.1; scene.add(kb);
  const pc = pencil(); pc.position.set(23, 0.4, 3); pc.rotation.y = 1.75; scene.add(pc);
  const note = new THREE.Mesh(roundedBox(7.6, 0.06, 7.6, 0.05), new THREE.MeshStandardMaterial({ color: 0xc8b8ff, roughness: 0.9 }));
  note.position.set(26, 0, -9); note.rotation.y = -0.18; note.receiveShadow = note.castShadow = true; scene.add(note);
  scene.add(keyLight(0xffffff, 1.7, [-25, 45, -18], 45));
  scene.add(new THREE.HemisphereLight(0xffffff, 0xd9d2e6, 0.25));
  bloom(r, scene, cam, 0.1);
  overlay(caption({ name: 'DeskOS', ver: 'V2', dark: false, line: 'A retro desktop on your handheld: every system opens as a window with a full-colour pixel console.', chips: ['14 colour schemes', '7 new dark schemes', 'Pixel-perfect consoles'] }));
}

// ---------------------------------------------------------------- 5. collection: four devices fanned on a purple backdrop
async function collection() {
  const r = makeRenderer(W, H); r.toneMappingExposure = 0.85;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x3a16c8);
  scene.environment = environment(r, 0.04); scene.environmentIntensity = 0.6;
  const cam = new THREE.PerspectiveCamera(26, W / H, 0.1, 300);
  cam.position.set(0, 62, 32); cam.lookAt(0, 0, 1.5);
  scene.add(floor(new THREE.MeshPhysicalMaterial({ color: 0x4416d8, roughness: 0.9, sheen: 0.25, sheenColor: 0x9c7bff })));
  const shots = ['volta/system-horizontal-dark.png', 'neonglow/system-vertical.png', 'vcr/system-snes.png', 'deskos/system-classic.png'];
  const pos = [[-18, 4, 0.16], [-6, 1, 0.05], [6, 1, -0.05], [18, 4, -0.16]];
  for (let i = 0; i < 4; i++) {
    const [x, z, yaw] = pos[i];
    scene.add(lay(await makeR36S(SCR(shots[i])), yaw, x, z));
  }
  scene.add(keyLight(0xffffff, 2.4, [-20, 50, 10], 45));
  scene.add(new THREE.HemisphereLight(0xe8e0ff, 0x2a0f8f, 0.5));
  bloom(r, scene, cam, 0.12);
  overlay(`<img src="../../logo/hqbit-logo-white.svg" style="position:absolute;left:50%;top:${H * 0.07}px;width:${W * 0.17}px;transform:translateX(-50%)">
   <div style="position:absolute;left:0;right:0;top:${H * 0.17}px;text-align:center;font:600 ${W * 0.024}px UB">The R36S theme collection</div>
   <div style="position:absolute;left:0;right:0;bottom:${H * 0.06}px;text-align:center;font:500 ${W * 0.0095}px JB;letter-spacing:.14em;color:rgba(255,255,255,.85)">VOLTA · NEONGLOW · VCR OSD · DESKOS &nbsp;—&nbsp; FOR R36S &amp; CLONES ON ARKOS, dARKOS AND EMUELEC</div>`);
}

const SCENES = { volta, neonglow, vcr, deskos, collection };
await loadFonts();
await SCENES[params.get('s') || 'volta']();
await Promise.all([...document.images].map((i) => (i.complete ? 0 : new Promise((res) => { i.onload = i.onerror = res; }))));
done();
