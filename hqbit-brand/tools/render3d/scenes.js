// HQbit 3D product shots. scene.html?s=tiles | glass | keycap
import { THREE, PURPLE, LIME, makeRenderer, environment, composer, markMesh, keycapGeometry, roundedBox, legend, glowPlane, loadFonts, done } from './common.js';

const params = new URLSearchParams(location.search);
const W = +params.get('w') || 1080;
const H = +params.get('h') || 1350;

const white = () => new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.3, clearcoat: 0.6, emissive: 0xffffff, emissiveIntensity: 0.08 });
const lime = (e = 0.25) => new THREE.MeshPhysicalMaterial({ color: LIME, roughness: 0.3, clearcoat: 0.6, emissive: LIME, emissiveIntensity: e });

// ------------------------------------------------------------------ 1. glass tiles
async function tiles() {
  const r = makeRenderer(W, H);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x030208);
  scene.environment = environment(r, 0.04);
  scene.environmentIntensity = 0.14;
  scene.fog = new THREE.Fog(0x030208, 9.5, 15);

  const cam = new THREE.PerspectiveCamera(30, W / H, 0.1, 100);
  cam.position.set(1.4, 8.4, 9.0);
  cam.lookAt(0.2, 0, 1.2);
  cam.setViewOffset(W, H, 0, -H * 0.3, W, H);

  const grid = new THREE.Group();
  grid.rotation.y = 0.42;
  grid.position.set(0, 0, 1.4);
  scene.add(grid);
  const size = 1.9, gap = 0.14;
  const glass = new THREE.MeshPhysicalMaterial({
    color: 0x4128c0, roughness: 0.36, metalness: 0, transmission: 0.7, thickness: 0.9, ior: 1.42,
    attenuationColor: new THREE.Color(0x3a14b8), attenuationDistance: 0.45, clearcoat: 1, clearcoatRoughness: 0.25,
    specularIntensity: 1, envMapIntensity: 1.2,
  });
  const geo = roundedBox(size, 0.34, size, 0.16, 6);
  const heights = {};
  for (let i = -3; i <= 3; i++) {
    for (let j = -2; j <= 3; j++) {
      const m = new THREE.Mesh(geo, glass);
      const lift = (i === 0 && j === 0) ? 0.18 : (Math.sin(i * 12.9898 + j * 78.233) * 43758.5453 % 1 + 1) % 1 * 0.16;
      heights[`${i},${j}`] = lift;
      m.position.set(i * (size + gap), lift, j * (size + gap));
      m.castShadow = true; m.receiveShadow = true;
      grid.add(m);
    }
  }
  // glowing floor between the tiles
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(40, 40),
    new THREE.MeshStandardMaterial({ color: 0x0a0418, emissive: 0x3a14b8, emissiveIntensity: 0.07, roughness: 1 }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.02;
  grid.add(floor);

  const mark = await markMesh({ width: 1.05, depth: 0.03, bMat: new THREE.MeshPhysicalMaterial({ color: 0xf2efff, roughness: 0.3, clearcoat: 0.6 }), chipMat: new THREE.MeshStandardMaterial({ color: 0xd4f230, roughness: 0.45, emissive: LIME, emissiveIntensity: 0.3 }) });
  mark.position.set(0, 0.34 + heights['0,0'] + 0.002, 0);
  grid.add(mark);

  const key = new THREE.DirectionalLight(0xc9b8ff, 1.5);
  key.position.set(-6, 9, -4);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -10, right: 10, top: 10, bottom: -10 });
  scene.add(key);
  const rim = new THREE.PointLight(0x7a4bff, 60, 14, 1.6);
  rim.position.set(-2.5, 2.2, -2);
  grid.add(rim);
  const spot = new THREE.SpotLight(0xe9e2ff, 38, 18, 0.26, 0.7, 1.5);
  spot.position.set(1.5, 8, 3);
  spot.target = mark;
  scene.add(spot);
  const under = new THREE.PointLight(PURPLE, 12, 6, 2);
  under.position.set(2.2, 0.5, 2.2);
  grid.add(under);

  composer(r, scene, cam, W, H, { strength: 0.4, radius: 0.6, threshold: 0.9 }).render();
  overlay(`<img src="../../logo/hqbit-logo-white.svg" style="position:absolute;left:50%;top:9%;width:46%;transform:translateX(-50%)">`);
}

// ------------------------------------------------------------------ 2. glowing glass keycap on a keyboard
function gradientBackground() {
  const c = document.createElement('canvas');
  c.width = W; c.height = H;
  const g = c.getContext('2d');
  const lg = g.createLinearGradient(0, 0, W * 0.4, H);
  lg.addColorStop(0, '#05030f');
  lg.addColorStop(0.45, '#1a0b5c');
  lg.addColorStop(1, '#3d17d6');
  g.fillStyle = lg; g.fillRect(0, 0, W, H);
  const rg = g.createRadialGradient(W * 0.1, H * 0.62, 0, W * 0.1, H * 0.62, W * 0.9);
  rg.addColorStop(0, 'rgba(97,43,254,0.75)');
  rg.addColorStop(1, 'rgba(97,43,254,0)');
  g.fillStyle = rg; g.fillRect(0, 0, W, H);
  g.strokeStyle = 'rgba(255,255,255,0.07)';
  g.lineWidth = 1;
  for (let x = 0; x < W; x += 135) { g.beginPath(); g.moveTo(x + 0.5, 0); g.lineTo(x + 0.5, H); g.stroke(); }
  for (let y = 0; y < H; y += 135) { g.beginPath(); g.moveTo(0, y + 0.5); g.lineTo(W, y + 0.5); g.stroke(); }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

async function glass() {
  const r = makeRenderer(W, H);
  r.toneMapping = THREE.NeutralToneMapping;
  const scene = new THREE.Scene();
  scene.background = gradientBackground();
  scene.environment = environment(r, 0.04);
  scene.environmentIntensity = 0.18;

  const cam = new THREE.PerspectiveCamera(32, W / H, 0.1, 100);
  cam.position.set(-3.1, 7.4, 5.9);
  cam.lookAt(-0.6, 0.6, 1.4);
  cam.setViewOffset(W, H, -W * 0.08, -H * 0.13, W, H);

  const kb = new THREE.Group();
  kb.rotation.y = -0.95;
  kb.position.set(-0.6, 0, 1.4);
  scene.add(kb);
  const alu = new THREE.MeshPhysicalMaterial({ color: 0x9aa0b4, metalness: 0.8, roughness: 0.38, clearcoat: 0.2 });
  const caseMesh = new THREE.Mesh(roundedBox(9, 0.9, 7, 0.35, 8), alu);
  caseMesh.position.set(3.6, -0.55, -2.6);
  caseMesh.castShadow = caseMesh.receiveShadow = true;
  kb.add(caseMesh);
  const plate = new THREE.Mesh(roundedBox(8.3, 0.1, 6.3, 0.1), new THREE.MeshStandardMaterial({ color: 0x1b1240, roughness: 0.8 }));
  plate.position.set(3.6, 0.3, -2.6);
  kb.add(plate);

  const capGeo = keycapGeometry(1.08, 0.72, 1.08, { taper: 0.16, dish: 0.012, radius: 0.16 });
  const whiteCap = new THREE.MeshPhysicalMaterial({ color: 0xb4b9cc, roughness: 0.55, clearcoat: 0.1 });
  const pitch = 1.22;
  for (let i = 0; i < 7; i++) {
    for (let j = 0; j < 5; j++) {
      if (i === 0 && j === 0) continue;
      const m = new THREE.Mesh(capGeo, whiteCap);
      m.position.set(i * pitch, 0.38, -j * pitch);
      m.castShadow = m.receiveShadow = true;
      kb.add(m);
    }
  }
  const lg = legend('~', { size: 0.4, color: '#2a2f4a', font: '500 120px IN' });
  lg.position.set(pitch, 0.38 + 0.72 + 0.003, 0);
  kb.add(lg);

  // the glass keycap with the glowing B inside
  const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0x6f48ff, roughness: 0.14, transmission: 1, thickness: 0.6, ior: 1.35,
    attenuationColor: new THREE.Color(PURPLE), attenuationDistance: 0.7, clearcoat: 1, clearcoatRoughness: 0.05,
    specularIntensity: 1, envMapIntensity: 1.4,
  });
  const gcap = new THREE.Mesh(keycapGeometry(1.08, 0.82, 1.08, { taper: 0.14, dish: 0.02, radius: 0.18 }), glassMat);
  gcap.position.set(0, 0.38, 0);
  kb.add(gcap);
  const bGlow = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xffffff, emissiveIntensity: 1.5 });
  const cGlow = new THREE.MeshStandardMaterial({ color: LIME, emissive: LIME, emissiveIntensity: 0.9 });
  const mark = await markMesh({ width: 0.54, depth: 0.012, bMat: bGlow, chipMat: cGlow });
  mark.position.set(0, 0.38 + 0.82 - 0.012, 0);
  kb.add(mark);
  const inner = new THREE.PointLight(0x8d66ff, 6, 3, 1.6);
  inner.position.set(0, 0.7, 0);
  kb.add(inner);
  const stem = new THREE.Mesh(roundedBox(0.7, 0.3, 0.7, 0.08), new THREE.MeshStandardMaterial({ color: PURPLE, emissive: 0x7a4bff, emissiveIntensity: 0.22 }));
  stem.position.set(0, 0.36, 0);
  kb.add(stem);

  const key = new THREE.DirectionalLight(0xe8e4ff, 0.9);
  key.position.set(-3, 9, 5);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -10, right: 10, top: 10, bottom: -10 });
  scene.add(key);
  const blue = new THREE.PointLight(0x5b3bff, 30, 20, 1.4);
  blue.position.set(-5, 3, 3);
  scene.add(blue);

  composer(r, scene, cam, W, H, { strength: 0.55, radius: 0.5, threshold: 0.9 }).render();
  overlay(`<div style="position:absolute;left:7.4%;top:16%;font-family:UB;font-weight:800;font-size:${W * 0.083}px;line-height:1.08;color:#fff;letter-spacing:-.01em">
  PIXEL<br><span style="color:#E0FE3B">THEMES</span><br>FOR R36S</div>
  <div style="position:absolute;left:7.4%;top:36.5%;font-family:JB;font-size:${W * 0.024}px;color:#ffffffbb;letter-spacing:.08em">BUILT FROM BITS · BY HQBIT</div>
  ${plus(W * 0.75, H * 0.15)}${plus(W * 0.23, H * 0.345)}
  <img src="../../logo/hqbit-logo-white.svg" style="position:absolute;left:7.4%;bottom:5%;width:28%">`);
}

function plus(x, y) {
  return `<div style="position:absolute;left:${x}px;top:${y}px;width:22px;height:22px;opacity:.55">
  <div style="position:absolute;left:10px;top:0;width:2px;height:22px;background:#fff"></div>
  <div style="position:absolute;top:10px;left:0;height:2px;width:22px;background:#fff"></div></div>`;
}

// ------------------------------------------------------------------ 3. purple keycap among black keycaps
async function keycap() {
  const r = makeRenderer(W, H);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x050407);
  scene.environment = environment(r, 0.04);
  scene.environmentIntensity = 0.12;
  scene.fog = new THREE.Fog(0x050407, 11, 19);

  const cam = new THREE.PerspectiveCamera(30, W / H, 0.1, 100);
  cam.position.set(0.95, 8.1, 5.7);
  cam.lookAt(0, 0.4, 0.2);
  cam.rotateZ(-0.12);

  const kb = new THREE.Group();
  kb.rotation.y = 0.18;
  scene.add(kb);
  const capGeo = keycapGeometry(1.5, 0.95, 1.5, { taper: 0.17, dish: 0.012, radius: 0.22 });
  const black = new THREE.MeshPhysicalMaterial({ color: 0x0c0b10, roughness: 0.78, sheen: 0.5, sheenRoughness: 0.6, sheenColor: 0x3a3060 });
  const purple = new THREE.MeshPhysicalMaterial({ color: 0x5222ea, roughness: 0.62, metalness: 0.1, sheen: 0.7, sheenRoughness: 0.5, sheenColor: 0x9c7bff });
  const letters = { '-1,-1': 'H', '0,-1': 'Q', '1,-1': 'I', '-1,0': 'T', '1,0': 'X', '-1,1': 'Z', '0,1': 'S', '1,1': 'A',
    '-2,0': 'D', '2,0': 'G', '-2,-1': 'R', '2,-1': 'Y', '-2,1': 'C', '2,1': 'N', '0,-2': '2', '-1,-2': '1', '1,-2': '3' };
  const pitch = 1.72;
  for (let i = -3; i <= 3; i++) {
    for (let j = -3; j <= 3; j++) {
      const centre = i === 0 && j === 0;
      const m = new THREE.Mesh(capGeo, centre ? purple : black);
      const x = i * pitch + (j % 2 ? 0.25 : 0), z = j * pitch;
      m.position.set(x, centre ? 0.14 : 0, z);
      m.castShadow = m.receiveShadow = true;
      kb.add(m);
      const t = letters[`${i},${j}`];
      if (t) {
        const l = legend(t, { size: 0.62, color: '#cfcadc', font: '500 140px IN' });
        l.position.set(x - 0.24, 0.955, z - 0.22);
        kb.add(l);
      }
    }
  }
  const mark = await markMesh({ width: 0.66, depth: 0.012, bMat: new THREE.MeshStandardMaterial({ color: 0xc9c3dd, roughness: 0.55 }), chipMat: new THREE.MeshStandardMaterial({ color: 0xc8e22e, roughness: 0.5, emissive: LIME, emissiveIntensity: 0.18 }) });
  mark.position.set(0, 0.14 + 0.95 - 0.004, 0);
  kb.add(mark);

  // purple light leaking from under the centre key
  const base = new THREE.Mesh(new THREE.PlaneGeometry(30, 30), new THREE.MeshStandardMaterial({ color: 0x060509, roughness: 0.9 }));
  base.rotation.x = -Math.PI / 2;
  base.position.y = -0.05;
  base.receiveShadow = true;
  kb.add(base);
  const glow = glowPlane(5.2, '#6a3cff', 0.95);
  glow.position.y = -0.02;
  kb.add(glow);
  const under = new THREE.PointLight(0x7a4bff, 22, 4.5, 1.4);
  under.position.set(0, 0.25, 0);
  kb.add(under);

  const key = new THREE.SpotLight(0xf1ecff, 70, 20, 0.42, 0.8, 1.4);
  key.position.set(-2.5, 8, 2);
  key.target.position.set(0, 0, 0);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  scene.add(key, key.target);
  const rim = new THREE.PointLight(0x9c7bff, 25, 9, 1.5);
  rim.position.set(3, 2.4, -3);
  scene.add(rim);

  composer(r, scene, cam, W, H, { strength: 0.45, radius: 0.7, threshold: 0.92 }).render();
  overlay(`<div style="position:absolute;inset:0;background:radial-gradient(120% 90% at 50% 45%,transparent 55%,rgba(0,0,0,.6) 100%)"></div>`);
}

function overlay(html) {
  const d = document.createElement('div');
  d.style.cssText = 'position:absolute;inset:0;pointer-events:none';
  d.innerHTML = html;
  document.getElementById('stage').appendChild(d);
}

await loadFonts();
await ({ tiles, glass, keycap })[params.get('s') || 'tiles']();
await Promise.all([...document.images].map((i) => (i.complete ? 0 : new Promise((r) => (i.onload = r)))));
done();
