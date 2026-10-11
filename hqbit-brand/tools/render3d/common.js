// Shared helpers for the HQbit 3D product shots (three.js, rendered headless by render.mjs).
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { SVGLoader } from 'three/addons/loaders/SVGLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

export { THREE };
export const PURPLE = 0x612bfe;
export const LIME = 0xe0fe3b;

export function makeRenderer(w, h) {
  const r = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  r.setPixelRatio(1);
  r.setSize(w, h);
  r.toneMapping = THREE.ACESFilmicToneMapping;
  r.toneMappingExposure = 1.0;
  r.outputColorSpace = THREE.SRGBColorSpace;
  r.shadowMap.enabled = true;
  r.shadowMap.type = THREE.PCFSoftShadowMap;
  document.getElementById('stage').appendChild(r.domElement);
  return r;
}

export function environment(renderer, intensity = 0.04) {
  const pm = new THREE.PMREMGenerator(renderer);
  return pm.fromScene(new RoomEnvironment(), intensity).texture;
}

export function composer(renderer, scene, camera, w, h, { strength = 0.5, radius = 0.5, threshold = 0.85 } = {}) {
  const rt = new THREE.WebGLRenderTarget(w, h, { type: THREE.HalfFloatType, samples: 4 });
  const c = new EffectComposer(renderer, rt);
  c.setPixelRatio(1);
  c.setSize(w, h);
  c.addPass(new RenderPass(scene, camera));
  c.addPass(new UnrealBloomPass(new THREE.Vector2(w, h), strength, radius, threshold));
  c.addPass(new OutputPass());
  return c;
}

// The logo mark: the B and its lime chip, taken from the official logo's paths.
let markShapes = null;
export async function loadMark() {
  if (markShapes) return markShapes;
  const txt = await (await fetch('../../logo/official/hqbit-logo-original.svg')).text();
  const ds = [...txt.matchAll(/<path class="(\w)" d="([^"]+)"/g)].map((m) => m[2]);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg"><g transform="scale(1,-1)"><path d="${ds[2]}"/><path d="${ds[3]}"/></g></svg>`;
  const data = new SVGLoader().parse(svg);
  markShapes = { b: SVGLoader.createShapes(data.paths[0]), chip: SVGLoader.createShapes(data.paths[1]) };
  return markShapes;
}

/** B mark lying flat (in the XZ plane, facing +Y), centred, `width` wide. */
export async function markMesh({ width = 1, depth = 0.02, bMat, chipMat, chipLift = 0 }) {
  const { b, chip } = await loadMark();
  const s = width / 110.28;
  const opts = { depth: depth / s, bevelEnabled: true, bevelThickness: depth * 0.25 / s, bevelSize: 0.6, bevelSegments: 2, curveSegments: 32 };
  const g = new THREE.Group();
  const bg = new THREE.ExtrudeGeometry(b, opts);
  const cg = new THREE.ExtrudeGeometry(chip, { ...opts, depth: (depth / s) * 1.02 });
  for (const geo of [bg, cg]) {
    geo.translate(-488.22, 296.925, 0);
    geo.scale(s, s, s);
  }
  if (chipLift) cg.translate(0, 0, chipLift);
  const mb = new THREE.Mesh(bg, bMat);
  const mc = new THREE.Mesh(cg, chipMat);
  for (const m of [mb, mc]) { m.castShadow = true; m.receiveShadow = true; }
  g.add(mb, mc);
  g.rotation.x = -Math.PI / 2;      // extruded along +Z -> now along +Y (facing up)
  return g;
}

/** Keycap: rounded box, tapered towards the top, with a shallow dish. */
export function keycapGeometry(w, h, d, { taper = 0.14, dish = 0.02, radius = 0.12, segments = 8 } = {}) {
  const g = new RoundedBoxGeometry(w, h, d, segments, radius);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    let x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    const t = (y + h / 2) / h;
    const s = 1 - taper * t;
    x *= s; z *= s;
    if (y > h / 2 - radius * 0.6) {
      const r = (x * x) / ((w * w) / 4) + (z * z) / ((d * d) / 4);
      y -= dish * Math.max(0, 1 - r);
    }
    p.setXYZ(i, x, y, z);
  }
  g.translate(0, h / 2, 0);
  return g;
}

export function roundedBox(w, h, d, r = 0.1, seg = 6) {
  const g = new RoundedBoxGeometry(w, h, d, seg, r);
  g.translate(0, h / 2, 0);
  return g;
}

/** A legend (printed letter) as a transparent plane texture. */
export function legend(text, { size = 0.34, color = '#ffffff', font = '600 150px IN' } = {}) {
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const ctx = c.getContext('2d');
  ctx.fillStyle = color;
  ctx.font = font;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, 128, 138);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(size, size),
    new THREE.MeshStandardMaterial({ map: tex, transparent: true, roughness: 0.6, depthWrite: false }));
  m.rotation.x = -Math.PI / 2;
  return m;
}

export async function loadFonts() {
  const f = [new FontFace('IN', 'url(../fonts/Inter-Variable.woff2)', { weight: '100 900' }),
    new FontFace('UB', 'url(../fonts/Unbounded-800.ttf)', { weight: '800' }),
    new FontFace('UB', 'url(../fonts/Unbounded-600.ttf)', { weight: '600' }),
    new FontFace('JB', 'url(../fonts/JetBrainsMono-Medium.ttf)', { weight: '500' })];
  for (const x of f) { await x.load(); document.fonts.add(x); }
}

/** Soft radial glow (additive), lying flat. */
export function glowPlane(size, color = '#7a4bff', opacity = 1) {
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const g = c.getContext('2d');
  const rg = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  rg.addColorStop(0, color); rg.addColorStop(0.35, color + 'aa'); rg.addColorStop(1, color + '00');
  g.fillStyle = rg; g.fillRect(0, 0, 256, 256);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(size, size), new THREE.MeshBasicMaterial({ map: t, transparent: true, opacity,
    blending: THREE.AdditiveBlending, depthWrite: false }));
  m.rotation.x = -Math.PI / 2;
  return m;
}

export function done() { window.__done = true; }
