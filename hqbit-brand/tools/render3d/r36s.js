// A white R36S handheld (approximate real proportions, 1 unit = 1 cm), with a theme screenshot on its screen.
// Built standing up: face towards +Z, width along X, height along Y. Rotate the returned group per scene.
import { THREE } from './common.js';

const W = 8.1, H = 12.8, T = 2.0;      // body width, height, thickness (cm)

function roundedRectShape(w, h, r) {
  const s = new THREE.Shape();
  const x = -w / 2, y = -h / 2;
  s.moveTo(x + r, y);
  s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r);
  s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r);
  s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y);
  return s;
}

function slab(w, h, depth, r, bevel, mat) {
  const g = new THREE.ExtrudeGeometry(roundedRectShape(w - 2 * bevel, h - 2 * bevel, Math.max(0.01, r - bevel)), {
    depth, bevelEnabled: true, bevelThickness: bevel, bevelSize: bevel, bevelSegments: 6, curveSegments: 24,
  });
  g.translate(0, 0, -depth / 2);
  const m = new THREE.Mesh(g, mat);
  m.castShadow = m.receiveShadow = true;
  return m;
}

function letterTexture(ch, color) {
  const c = document.createElement('canvas');
  c.width = c.height = 128;
  const g = c.getContext('2d');
  g.fillStyle = '#1b1a20'; g.fillRect(0, 0, 128, 128);
  g.fillStyle = color; g.font = '700 82px IN'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(ch, 64, 70);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

function textTexture(text, { w = 256, h = 64, size = 34, color = '#8b8a96', bg = null, font = '600' } = {}) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  const g = c.getContext('2d');
  if (bg) { g.fillStyle = bg; g.fillRect(0, 0, w, h); }
  g.fillStyle = color; g.font = `${font} ${size}px IN`; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(text, w / 2, h / 2 + 2);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

export async function makeR36S(screenUrl, { screenGlow = 1.0 } = {}) {
  const dev = new THREE.Group();
  const white = new THREE.MeshPhysicalMaterial({ color: 0xf1f0f5, roughness: 0.38, clearcoat: 0.5, clearcoatRoughness: 0.35, sheen: 0.2 });
  const dark = new THREE.MeshPhysicalMaterial({ color: 0x1d1c22, roughness: 0.45, clearcoat: 0.4, clearcoatRoughness: 0.3 });
  const rubber = new THREE.MeshStandardMaterial({ color: 0x17161b, roughness: 0.85 });

  dev.add(slab(W, H, T - 0.6, 0.95, 0.3, white));

  // screen: glossy black bezel, the screenshot, and a glass layer that picks up reflections
  const face = T / 2;
  const bez = slab(7.35, 5.75, 0.02, 0.35, 0.03, new THREE.MeshPhysicalMaterial({ color: 0x0b0b0f, roughness: 0.2, clearcoat: 1 }));
  bez.position.set(0, 3.35, face + 0.01);
  dev.add(bez);
  const tex = await new THREE.TextureLoader().loadAsync(screenUrl);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  const scr = new THREE.Mesh(new THREE.PlaneGeometry(7.04, 5.28),
    new THREE.MeshBasicMaterial({ map: tex, color: new THREE.Color(screenGlow, screenGlow, screenGlow), toneMapped: false }));
  scr.position.set(0, 3.35, face + 0.06);
  dev.add(scr);
  const glass = new THREE.Mesh(new THREE.PlaneGeometry(7.3, 5.7),
    new THREE.MeshPhysicalMaterial({ color: 0x000000, roughness: 0.04, metalness: 0, transparent: true, opacity: 0.12, clearcoat: 1, envMapIntensity: 1.6 }));
  glass.position.set(0, 3.35, face + 0.075);
  dev.add(glass);

  // D-pad
  const dpad = new THREE.Group();
  for (const [w, h] of [[2.3, 0.78], [0.78, 2.3]]) {
    const b = slab(w, h, 0.28, 0.18, 0.08, dark);
    dpad.add(b);
  }
  dpad.position.set(-2.45, -0.95, face + 0.12);
  dev.add(dpad);

  // ABXY
  const abxy = [['X', 0, 0.9, '#3d6fd6'], ['Y', -0.9, 0, '#d7e33a'], ['A', 0.9, 0, '#d6455a'], ['B', 0, -0.9, '#e8c234']];
  for (const [ch, dx, dy, col] of abxy) {
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.22, 40), dark);
    cap.rotation.x = Math.PI / 2;
    const top = new THREE.Mesh(new THREE.CircleGeometry(0.4, 40), new THREE.MeshPhysicalMaterial({ map: letterTexture(ch, col), roughness: 0.32, clearcoat: 0.9 }));
    top.position.z = 0.115;
    const btn = new THREE.Group();
    btn.add(cap, top);
    btn.position.set(2.45 + dx, -0.95 + dy, face + 0.1);
    cap.castShadow = true;
    dev.add(btn);
  }

  // speaker grille (3 rows of slots) and FN button
  const slot = (w) => slab(w, 0.18, 0.02, 0.09, 0.01, new THREE.MeshStandardMaterial({ color: 0x2a2930, roughness: 0.9 }));
  const rows = [[[-0.55, 0.7], [0.15, 0.35], [0.75, 0.7]], [[-0.62, 0.35], [0, 0.7], [0.62, 0.35]], [[-0.55, 0.7], [0.15, 0.35], [0.75, 0.7]]];
  rows.forEach((r, i) => r.forEach(([x, w]) => { const s = slot(w); s.position.set(x - 0.05, 0.05 - i * 0.42, face + 0.005); dev.add(s); }));
  const fnLbl = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 0.18), new THREE.MeshBasicMaterial({ map: textTexture('FN', { w: 128, h: 40, size: 28, color: '#b9b8c4' }), transparent: true }));
  fnLbl.position.set(0, -1.5, face + 0.005);
  dev.add(fnLbl);
  const fn = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.18, 40), dark);
  fn.rotation.x = Math.PI / 2; fn.position.set(0, -2.15, face + 0.08);
  dev.add(fn);

  // select / start with the blue LED between them
  for (const [x, lbl] of [[-0.85, 'SELECT'], [0.85, 'START']]) {
    const b = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 0.16, 36), dark);
    b.rotation.x = Math.PI / 2; b.position.set(x, -3.15, face + 0.07);
    dev.add(b);
    const l = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 0.18), new THREE.MeshBasicMaterial({ map: textTexture(lbl, { w: 256, h: 52, size: 30, color: '#c6c5cf' }), transparent: true }));
    l.position.set(x, -3.68, face + 0.005);
    dev.add(l);
  }
  const led = new THREE.Mesh(new THREE.CircleGeometry(0.1, 24), new THREE.MeshBasicMaterial({ color: 0x5fa8ff, toneMapped: false }));
  led.position.set(0, -3.15, face + 0.006);
  dev.add(led);
  const ledGlow = new THREE.Mesh(new THREE.CircleGeometry(0.32, 24), new THREE.MeshBasicMaterial({ color: 0x3b7dff, transparent: true, opacity: 0.25, toneMapped: false }));
  ledGlow.position.set(0, -3.15, face + 0.005);
  dev.add(ledGlow);

  // analog sticks: dark well, shaft and a concave cap
  for (const x of [-2.15, 2.15]) {
    const well = new THREE.Mesh(new THREE.CylinderGeometry(1.05, 1.05, 0.06, 48), new THREE.MeshStandardMaterial({ color: 0x0f0e12, roughness: 0.9 }));
    well.rotation.x = Math.PI / 2; well.position.set(x, -4.55, face + 0.0);
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.88, 0.95, 0.42, 48), rubber);
    cap.rotation.x = Math.PI / 2; cap.position.set(x, -4.55, face + 0.32);
    cap.castShadow = true;
    const dish = new THREE.Mesh(new THREE.TorusGeometry(0.72, 0.09, 12, 48), new THREE.MeshStandardMaterial({ color: 0x232228, roughness: 0.7 }));
    dish.position.set(x, -4.55, face + 0.53);
    dev.add(well, cap, dish);
  }

  // shoulder buttons on the top edge and the label on the front
  for (const x of [-2.6, 2.6]) {
    const l = slab(2.0, 0.5, 0.9, 0.24, 0.12, dark);
    l.rotation.x = Math.PI / 2;
    l.position.set(x, H / 2 - 0.12, -0.45);
    dev.add(l);
  }
  dev.userData.size = { W, H, T };
  return dev;
}
