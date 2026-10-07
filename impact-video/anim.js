// IMPACT — "Learning that goes beyond learning." motion graphic.
// Deterministic renderer: render(t) draws the frame at time t (seconds).
const W = 1920, H = 1080, DURATION = 90;
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');

// ---------- Brand palette (from brand guide) ----------
const C = {
  cyan: '#20e0e0', blue: '#00a2ea', navy: '#2a3649',
  orange: '#f85a35', yellow: '#fbb414', green: '#00cc99', sky: '#80dbff',
  indigo: '#3f37c9', violet: '#8164ff', purple: '#672496', pink: '#ed1e6c',
  ink: '#05061a', deep: '#0b0040', light: '#f2f3f5', white: '#ffffff',
};
const SECONDARY = [C.orange, C.yellow, C.green, C.sky, C.indigo, C.violet, C.purple, C.pink];

// ---------- Math / easing ----------
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, k) => a + (b - a) * k;
const prog = (t, a, b) => clamp((t - a) / (b - a));
const eOut = k => 1 - Math.pow(1 - k, 3);
const eOut5 = k => 1 - Math.pow(1 - k, 5);
const eExpo = k => (k >= 1 ? 1 : 1 - Math.pow(2, -10 * k));
const eInOut = k => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
const eIn = k => k * k * k;
const eBack = k => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(k - 1, 3) + c1 * Math.pow(k - 1, 2); };
function rand(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
function hexA(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
}
function mixHex(h1, h2, k) {
  const a = parseInt(h1.slice(1), 16), b = parseInt(h2.slice(1), 16);
  const r = Math.round(lerp((a >> 16) & 255, (b >> 16) & 255, k));
  const g = Math.round(lerp((a >> 8) & 255, (b >> 8) & 255, k));
  const bl = Math.round(lerp(a & 255, b & 255, k));
  return `rgb(${r},${g},${bl})`;
}
// in/out envelope for a scene element
function env(t, a, b, fin = 0.5, fout = 0.5) { return Math.min(eOut(prog(t, a, a + fin)), 1 - eIn(prog(t, b - fout, b))); }

// ---------- Rich text ----------
// "*italic*" -> serif italic accent, "{BOLD}" -> heavy sans
const SANS = 'Montserrat', SERIF = 'Instrument Serif';
function parse(str) {
  const out = [];
  str.split(/(\*[^*]+\*|\{[^}]+\})/).forEach(p => {
    if (!p) return;
    if (p[0] === '*') out.push({ s: p.slice(1, -1), kind: 'i' });
    else if (p[0] === '{') out.push({ s: p.slice(1, -1), kind: 'b' });
    else out.push({ s: p, kind: 'n' });
  });
  return out;
}
function fontFor(kind, size, weight) {
  if (kind === 'i') return `italic 400 ${size * 1.2}px "${SERIF}"`;
  if (kind === 'b') return `800 ${size}px "${SANS}"`;
  return `${weight} ${size}px "${SANS}"`;
}
function words(str, size, o) {
  const res = [];
  parse(str).forEach(seg => {
    seg.s.split(' ').forEach((w, j, arr) => {
      if (w === '') { if (res.length) res[res.length - 1].sp = true; return; }
      const font = fontFor(seg.kind, size, o.weight || 500);
      ctx.font = font;
      const color = seg.kind === 'i' ? (o.accent || C.cyan) : seg.kind === 'b' ? (o.bold || o.color || C.white) : (o.color || C.white);
      res.push({ w, font, color, width: ctx.measureText(w).width, kind: seg.kind, sp: j < arr.length - 1 });
    });
  });
  return res;
}
// Draw multi-line text with per-word blur-in. lines: array of strings.
// o: {x, y, size, align, a (start), b (end), stagger, dur, lh, color, accent, weight, exit:'blur'|'up'|'none', grad}
function say(t, lines, o) {
  const a = o.a, b = o.b;
  if (t < a - 0.01 || t > b + 0.8) return;
  const size = o.size || 72, lh = (o.lh || 1.18) * size, stagger = o.stagger ?? 0.07, dur = o.dur ?? 0.7;
  const align = o.align || 'center';
  const sp = size * 0.27;
  let wi = 0;
  const totalH = lh * (lines.length - 1);
  lines.forEach((line, li) => {
    const ws = words(line, size, o);
    let width = 0; ws.forEach((w, i) => { width += w.width + (i < ws.length - 1 && w.sp !== false ? sp : 0); });
    let x = align === 'center' ? (o.x ?? W / 2) - width / 2 : align === 'right' ? (o.x) - width : (o.x);
    const y = (o.y ?? H / 2) - totalH / 2 + li * lh + size * 0.35;
    ws.forEach((w, i) => {
      const st = a + (o.lineDelay ? li * o.lineDelay : 0) + wi * stagger;
      const k = eOut5(prog(t, st, st + dur));
      const out = prog(t, b, b + (o.outDur || 0.5));
      const ko = eIn(out);
      let alpha = k * (1 - ko);
      if (alpha > 0.002) {
        const blur = (1 - k) * (o.blurIn ?? 22) + ko * 24;
        const dy = (1 - k) * size * 0.45 - ko * size * 0.3;
        ctx.save();
        ctx.globalAlpha = alpha * (o.alpha ?? 1);
        if (blur > 0.4) ctx.filter = `blur(${blur.toFixed(1)}px)`;
        ctx.font = w.font;
        ctx.textBaseline = 'alphabetic';
        if (o.grad && w.kind !== 'n') {
          const g = ctx.createLinearGradient(x, y - size, x + w.width, y);
          g.addColorStop(0, C.cyan); g.addColorStop(1, C.blue);
          ctx.fillStyle = g;
        } else ctx.fillStyle = w.color;
        if (o.ls) { ctx.letterSpacing = o.ls + 'px'; }
        ctx.fillText(w.w, x, y + dy);
        ctx.restore();
      }
      x += w.width + (w.sp !== false ? sp : 0);
      wi++;
    });
  });
}
function textWidth(str, size, o = {}) {
  const ws = words(str, size, o); const sp = size * 0.27;
  return ws.reduce((s, w, i) => s + w.width + (i < ws.length - 1 ? sp : 0), 0);
}
// simple single label (no animation)
function label(str, x, y, size, color, o = {}) {
  ctx.save();
  ctx.font = o.font || `${o.weight || 500} ${size}px "${SANS}"`;
  ctx.fillStyle = color; ctx.textAlign = o.align || 'left'; ctx.textBaseline = o.base || 'middle';
  if (o.ls) ctx.letterSpacing = o.ls + 'px';
  if (o.alpha !== undefined) ctx.globalAlpha = o.alpha;
  if (o.blur) ctx.filter = `blur(${o.blur}px)`;
  ctx.fillText(str, x, y);
  ctx.restore();
}

// ---------- Logo ----------
const LP = { icon: LOGO.icon.map(d => new Path2D(d)), word: LOGO.word.map(d => new Path2D(d)), tag: LOGO.tag.map(d => new Path2D(d)) };
function iconGrad(c) {
  const g = c.createLinearGradient(0, 0, 0, 165);
  g.addColorStop(0, C.blue); g.addColorStop(1, C.cyan);
  return g;
}
// icon order in svg: 0 inner arc,1 mid arc,2 outer arc,3 small arch,4 mid arch,5 big arch,6 bar
const ICON_ORDER = [6, 3, 4, 5, 0, 1, 2];
// draw the fingerprint icon with ripple reveal. k in [0,1]
function drawIcon(cx, cy, scale, k, alpha = 1, glow = 0) {
  ctx.save();
  ctx.translate(cx, cy); ctx.scale(scale, scale); ctx.translate(-86.35, -95);
  ctx.globalAlpha = alpha;
  const g = iconGrad(ctx);
  ICON_ORDER.forEach((pi, j) => {
    const kk = eOut5(clamp(k * 1.9 - j * 0.15));
    if (kk <= 0) return;
    ctx.save();
    // ripple clip: circle growing from the base of the bar
    ctx.beginPath();
    ctx.arc(86.35, 125, 10 + kk * 160, 0, Math.PI * 2);
    ctx.clip();
    ctx.globalAlpha = alpha * kk;
    ctx.fillStyle = g;
    if (glow) { ctx.shadowColor = hexA(C.cyan, 0.8 * glow); ctx.shadowBlur = 30 * glow; }
    ctx.fill(LP.icon[pi]);
    ctx.restore();
  });
  ctx.restore();
}
// full horizontal logo. kIcon, kWord, kTag in [0,1]; wordColor for wordmark
function drawLogo(cx, cy, scale, kIcon, kWord, kTag, wordColor) {
  // logo viewBox 517.38 x 165.03 -> centre it
  const ox = cx - 517.38 * scale / 2, oy = cy - 165.03 * scale / 2;
  drawIcon(ox + 86.35 * scale, oy + 95 * scale, scale, kIcon);
  ctx.save();
  ctx.translate(ox, oy); ctx.scale(scale, scale);
  // wordmark: left-to-right blur wipe
  const kw = eOut5(kWord);
  if (kw > 0) {
    ctx.save();
    ctx.beginPath(); ctx.rect(200, 0, 330 * kw, 110); ctx.clip();
    ctx.globalAlpha = kw;
    ctx.translate((1 - kw) * -30, 0);
    ctx.fillStyle = wordColor;
    LP.word.forEach(p => ctx.fill(p));
    ctx.restore();
  }
  const kt = eOut(kTag);
  if (kt > 0) {
    ctx.save();
    ctx.globalAlpha = kt;
    ctx.translate(0, (1 - kt) * 12);
    ctx.fillStyle = wordColor;
    LP.tag.forEach(p => ctx.fill(p));
    ctx.restore();
  }
  ctx.restore();
}

// ---------- Background ----------
// grain
const grain = document.createElement('canvas'); grain.width = grain.height = 256;
(() => {
  const g = grain.getContext('2d'); const id = g.createImageData(256, 256);
  for (let i = 0; i < id.data.length; i += 4) { const v = Math.random() * 255; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
  g.putImageData(id, 0, 0);
})();
function blob(x, y, r, color, a) {
  if (a <= 0.003) return;
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, hexA(color, a)); g.addColorStop(0.45, hexA(color, a * 0.55)); g.addColorStop(1, hexA(color, 0));
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
// "aurora" floor glow like the reference: bright arc rising from the bottom
function floorGlow(t, k, hue = 0) {
  if (k <= 0.003) return;
  const sway = Math.sin(t * 0.35) * 160;
  blob(W * 0.5 + sway, H * 1.25, 1100, C.indigo, 0.85 * k);
  blob(W * 0.25 - sway * 0.6, H * 1.1, 700, C.violet, 0.55 * k);
  blob(W * 0.82 + sway * 0.4, H * 1.08, 650, C.blue, 0.85 * k);
  blob(W * 0.62 - sway, H * 1.18, 520, hue ? C.cyan : C.sky, 0.55 * k);
}
// gradient like the provided background art: deep indigo, blue top light, cyan corner
function brandField(t, k) {
  if (k <= 0.003) return;
  ctx.save(); ctx.globalAlpha = k;
  ctx.fillStyle = '#0a0038'; ctx.fillRect(0, 0, W, H);
  const d = Math.sin(t * 0.25);
  blob(W * 0.52 + d * 120, -120, 900, '#62a0ff', 0.9);
  blob(W * 1.0, H * 0.05, 700, '#1e6af5', 0.8);
  blob(W * 1.02 - d * 60, H * 1.02, 760, '#00e5ff', 0.95);
  blob(W * 0.74 + d * 80, H * 0.55, 380, '#05003a', 0.95);
  blob(-100, H * 1.1, 900, '#080033', 0.9);
  ctx.restore();
}
function vignette(a = 0.65) {
  const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.05);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${a})`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
function drawGrain(t, a = 0.05) {
  ctx.save(); ctx.globalAlpha = a; ctx.globalCompositeOperation = 'overlay';
  const ox = Math.floor(rand(Math.floor(t * 30)) * 256), oy = Math.floor(rand(Math.floor(t * 30) + 7) * 256);
  ctx.translate(-ox, -oy);
  ctx.fillStyle = ctx.createPattern(grain, 'repeat'); ctx.fillRect(0, 0, W + 256, H + 256);
  ctx.restore();
}

// ---------- Shared motifs ----------
function roundRect(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
// thin grid like the reference (lines draw in)
function grid(t, a, b, cols, rows, alpha = 0.16, color = '#ffffff') {
  const k = eInOut(prog(t, a, a + 1.2)) * (1 - eIn(prog(t, b - 0.6, b)));
  if (k <= 0) return;
  ctx.save(); ctx.strokeStyle = hexA(color, alpha); ctx.lineWidth = 1.5;
  for (let i = 1; i < cols; i++) {
    const x = (W / cols) * i, kk = eOut(clamp(k * 1.6 - i * 0.08));
    ctx.beginPath(); ctx.moveTo(x, H / 2 - (H / 2) * kk); ctx.lineTo(x, H / 2 + (H / 2) * kk); ctx.stroke();
  }
  for (let j = 1; j < rows; j++) {
    const y = (H / rows) * j, kk = eOut(clamp(k * 1.6 - j * 0.1));
    ctx.beginPath(); ctx.moveTo(W / 2 - (W / 2) * kk, y); ctx.lineTo(W / 2 + (W / 2) * kk, y); ctx.stroke();
  }
  ctx.restore();
}
// 3D-ish floating brand token (rounded square / circle / plus / arc)
function token(type, x, y, s, color, rot, alpha = 1, blur = 0) {
  if (alpha <= 0.01) return;
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.globalAlpha = alpha;
  if (blur > 0.5) ctx.filter = `blur(${blur}px)`;
  const g = ctx.createLinearGradient(-s, -s, s, s);
  g.addColorStop(0, mixHex(color, '#ffffff', 0.45)); g.addColorStop(0.55, color); g.addColorStop(1, mixHex(color, '#000000', 0.45));
  ctx.fillStyle = g; ctx.strokeStyle = g;
  if (type === 'sq') { roundRect(-s / 2, -s / 2, s, s, s * 0.22); ctx.fill(); }
  else if (type === 'ci') { ctx.beginPath(); ctx.arc(0, 0, s / 2, 0, Math.PI * 2); ctx.fill(); }
  else if (type === 'plus') { const b = s * 0.32; roundRect(-b / 2, -s / 2, b, s, b / 2); ctx.fill(); roundRect(-s / 2, -b / 2, s, b, b / 2); ctx.fill(); }
  else if (type === 'arc') { ctx.lineWidth = s * 0.22; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(0, s * 0.15, s * 0.42, Math.PI, 0); ctx.stroke(); }
  else if (type === 'pill') { roundRect(-s * 0.7, -s * 0.24, s * 1.4, s * 0.48, s * 0.24); ctx.fill(); }
  ctx.restore();
}
// concentric arches — the IMPACT fingerprint as a ripple
function arches(cx, cy, r0, gap, n, k, color, lw, alpha = 1) {
  ctx.save(); ctx.lineCap = 'round';
  for (let i = 0; i < n; i++) {
    const kk = eOut5(clamp(k * 1.5 - i * (0.5 / n)));
    if (kk <= 0) continue;
    const r = r0 + i * gap;
    ctx.strokeStyle = hexA(color, alpha * (1 - i / (n + 2)) * kk);
    ctx.lineWidth = lw;
    ctx.beginPath(); ctx.arc(cx, cy, r, Math.PI + (1 - kk) * Math.PI / 2, -(1 - kk) * Math.PI / 2); ctx.stroke();
  }
  ctx.restore();
}

// =====================================================================
// SCENES
// =====================================================================

// ---- 1. OPENING 0–8 ----
function sceneOpening(t) {
  if (t > 8.6) return;
  // a rising glow
  floorGlow(t, eInOut(prog(t, 0.2, 5.5)) * 0.55 + eOut(prog(t, 5.4, 6.4)) * 0.6);
  say(t, ['Every business wants to *move forward.*'], { a: 0.4, b: 2.6, size: 70 });
  say(t, ["But businesses don’t change", '*on their own.*'], { a: 2.95, b: 5.15, size: 70, lineDelay: 0.25 });
  // "People do." huge, then zoom-through transition
  const z = eIn(prog(t, 7.55, 8.3));
  ctx.save();
  ctx.translate(W / 2, H / 2); ctx.scale(1 + z * 3.5, 1 + z * 3.5); ctx.translate(-W / 2, -H / 2);
  say(t, ['*People* {do.}'], { a: 5.45, b: 8.2, size: 190, accent: C.white, bold: C.white, stagger: 0.18, dur: 0.9, grad: true, alpha: 1 - z });
  ctx.restore();
  // small caption
  const kc = env(t, 6.0, 7.4, 0.6, 0.4);
  label('IMPACT  ·  LEARNING & DEVELOPMENT', W / 2, H - 120, 20, hexA('#ffffff', 0.55 * kc), { align: 'center', ls: 6, weight: 600 });
}

// ---- 2. THE CHALLENGE 8–20 ----
function sceneChallenge(t) {
  if (t < 7.8 || t > 20.6) return;
  // dark grid world
  floorGlow(t, 0.35 * env(t, 7.9, 16.3, 1, 0.5), 1);
  grid(t, 8.1, 16.4, 6, 4, 0.13);
  say(t, ['In a world where', '*everything keeps changing,*'], { a: 8.2, b: 10.75, size: 76, lineDelay: 0.2 });
  say(t, ['what people knew *yesterday*', 'isn’t always enough for *tomorrow.*'], { a: 11.0, b: 13.4, size: 64, lineDelay: 0.35 });

  // three grid cells: New challenges / technologies / expectations
  const cells = [
    { s: 'New *challenges.*', col: C.orange, type: 'sq', cx: 1, cy: 1, d: 0 },
    { s: 'New *technologies.*', col: C.violet, type: 'ci', cx: 2.5, cy: 2, d: 0.65 },
    { s: 'New *expectations.*', col: C.pink, type: 'plus', cx: 4, cy: 1, d: 1.3 },
  ];
  const cw = W / 6, ch = H / 4;
  cells.forEach((c, i) => {
    const a = 13.6 + c.d, b = 16.15;
    const k = eOut5(prog(t, a, a + 0.6)) * (1 - eIn(prog(t, b, b + 0.4)));
    if (k <= 0) return;
    const x = c.cx * cw, y = c.cy * ch;
    // cell fill
    ctx.save(); ctx.globalAlpha = k;
    ctx.fillStyle = hexA('#ffffff', 0.04); ctx.fillRect(x, y, cw * 1.5, ch);
    ctx.strokeStyle = hexA(c.col, 0.9); ctx.lineWidth = 2; ctx.strokeRect(x + 1, y + 1, cw * 1.5 - 2, ch - 2);
    ctx.restore();
    const bob = Math.sin(t * 2 + i) * 6;
    token(c.type, x + cw * 1.5 - 60, y + 60 + bob, 56 * eBack(clamp(k)), c.col, t * 0.6 + i, k);
    say(t, [c.s], { a, b, size: 46, x: x + 36, y: y + ch - 66, align: 'left', accent: c.col, outDur: 0.4 });
  });
  // small tags floating like UI chips
  ['Meetings', 'Deadlines', 'Decisions', 'Pressure'].forEach((s, i) => {
    const a = 8.6 + i * 0.35, k = env(t, a, 13.3, 0.6, 0.5);
    if (k <= 0) return;
    const px = [180, 1560, 260, 1500][i], py = [170, 210, 880, 860][i] + Math.sin(t + i) * 8;
    ctx.save(); ctx.globalAlpha = k * 0.9;
    ctx.font = `600 22px "${SANS}"`; const w = ctx.measureText(s).width + 44;
    roundRect(px, py - 22, w, 44, 22); ctx.fillStyle = hexA('#ffffff', 0.06); ctx.fill();
    ctx.strokeStyle = hexA(SECONDARY[i * 2 + 1], 0.8); ctx.lineWidth = 1.5; ctx.stroke();
    ctx.beginPath(); ctx.arc(px + 20, py, 5, 0, 7); ctx.fillStyle = SECONDARY[i * 2 + 1]; ctx.fill();
    ctx.fillStyle = '#fff'; ctx.textBaseline = 'middle'; ctx.fillText(s, px + 34, py + 1);
    ctx.restore();
  });

  // light question card 16.3 – 20.2  (white wipe like the reference)
  const kw = eInOut(prog(t, 16.15, 16.75)), ko = eInOut(prog(t, 19.85, 20.35));
  if (kw > 0 && ko < 1) {
    ctx.save();
    ctx.beginPath();
    const r = Math.hypot(W, H) * 0.6;
    ctx.arc(W / 2, H / 2, r * kw * (1 - ko) + 0.1, 0, Math.PI * 2);
    ctx.clip();
    ctx.fillStyle = C.light; ctx.fillRect(0, 0, W, H);
    blob(W * 0.5, H * 1.3, 900, C.sky, 0.35);
    say(t, ['The question isn’t simply:'], { a: 16.5, b: 19.6, size: 30, y: 330, color: hexA(C.navy, 0.6), weight: 500 });
    say(t, ['“Are we *learning?*”'], { a: 16.7, b: 17.95, size: 96, y: 540, color: C.navy, accent: C.blue });
    say(t, ['It’s: “Are we learning', 'what *actually makes a difference?*”'], { a: 18.1, b: 19.75, size: 76, y: 560, color: C.navy, accent: C.blue, lineDelay: 0.15, stagger: 0.05 });
    // underline sweep
    const ku = eOut5(prog(t, 18.7, 19.4)) * (1 - prog(t, 19.6, 19.9));
    if (ku > 0) { ctx.fillStyle = C.cyan; ctx.fillRect(W / 2 - 520, 660, 1040 * ku, 6); }
    ctx.restore();
  }
}

// ---- 3. INTRODUCING IMPACT 20–32 ----
function sceneIntro(t) {
  if (t < 19.8 || t > 32.6) return;
  const kf = env(t, 20.0, 32.4, 1.4, 0.6);
  brandField(t, kf * 0.9);
  ctx.fillStyle = `rgba(0,0,0,${0.25 * kf})`; ctx.fillRect(0, 0, W, H);

  // logo icon draws with ripple
  const ki = prog(t, 20.4, 22.2);
  const iconUp = eInOut(prog(t, 22.5, 23.2));
  const ia = env(t, 20.4, 25.4, 0.3, 0.6);
  if (ia > 0) {
    drawIcon(W / 2, lerp(470, 300, iconUp), lerp(1.7, 1.0, iconUp), ki, ia, 0.5);
    // ripple rings echoing out of the icon
    for (let i = 0; i < 3; i++) {
      const rk = prog(t, 21.0 + i * 0.4, 23.4 + i * 0.4);
      if (rk > 0 && rk < 1) arches(W / 2, lerp(470, 300, iconUp) + 50, 120 + rk * 600, 0, 1, 1, C.cyan, 2, (1 - rk) * 0.6 * ia);
    }
  }
  say(t, ['That’s where {IMPACT} comes in.'], { a: 21.6, b: 22.4, size: 64, y: 720, outDur: 0.4 });
  say(t, ['A Learning & Development partner', 'built around one *simple belief:*'], { a: 22.75, b: 25.25, size: 60, y: 560, lineDelay: 0.2 });
  say(t, ['Learning should', '*leave an impact.*'], { a: 25.6, b: 27.7, size: 110, y: 540, lineDelay: 0.2, stagger: 0.12, grad: true, dur: 0.9 });

  // 28–32 timeline with cycling word
  const ka = env(t, 27.9, 32.1, 0.6, 0.5);
  if (ka > 0) {
    say(t, ['Not just in the classroom.'], { a: 27.95, b: 31.9, size: 34, x: 420, y: 330, align: 'left', color: hexA('#ffffff', 0.65) });
    say(t, ['But in the way people'], { a: 28.3, b: 31.9, size: 72, x: 420, y: 470, align: 'left' });
    const wordsList = ['think.', 'decide.', 'lead.', 'perform.'];
    // timeline line
    const lx = 360, ly0 = 300, ly1 = 860;
    ctx.save(); ctx.globalAlpha = ka;
    ctx.strokeStyle = hexA('#ffffff', 0.25); ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(lx, ly0); ctx.lineTo(lx, lerp(ly0, ly1, eOut(prog(t, 28, 28.8)))); ctx.stroke();
    ctx.restore();
    wordsList.forEach((w, i) => {
      const a = 28.75 + i * 0.78, b = i === 3 ? 31.9 : a + 0.78;
      say(t, ['*' + w + '*'], { a, b, size: 150, x: 420, y: 640, align: 'left', accent: [C.cyan, C.sky, C.blue, C.cyan][i], dur: 0.5, outDur: 0.3, grad: i === 3 });
      // milestone dots
      const dk = eBack(prog(t, a, a + 0.4));
      const dy = lerp(560, 820, i / 3);
      ctx.save(); ctx.globalAlpha = ka;
      ctx.beginPath(); ctx.arc(lx, dy, 9 * dk, 0, 7); ctx.fillStyle = t >= a && t < b + 0.05 ? C.cyan : hexA('#ffffff', 0.5); ctx.fill();
      ctx.restore();
      label(w.replace('.', ''), lx - 28, dy, 20, hexA('#ffffff', 0.6 * ka * dk), { align: 'right', weight: 500 });
    });
  }
}

// ---- 4. WHAT IMPACT DOES 32–50 ----
function sceneDoes(t) {
  if (t < 31.8 || t > 50.6) return;
  floorGlow(t, env(t, 32, 50.3, 1, 0.6) * 0.75);

  // 32–36 three cards
  say(t, ['We create learning experiences designed around'], { a: 32.3, b: 35.9, size: 38, y: 250, color: hexA('#ffffff', 0.8), stagger: 0.04 });
  const cards = [
    { s: 'Real *people*', c: C.cyan, type: 'ci' },
    { s: 'Real *challenges*', c: C.orange, type: 'plus' },
    { s: 'Real *business needs*', c: C.violet, type: 'sq' },
  ];
  cards.forEach((cd, i) => {
    const a = 32.8 + i * 0.45, k = eOut5(prog(t, a, a + 0.8)), ko = eInOut(prog(t, 35.8 + i * 0.08, 36.4 + i * 0.08));
    if (k <= 0 || ko >= 1) return;
    const cw = 500, chh = 330, gap = 40;
    const x = W / 2 - (cw * 3 + gap * 2) / 2 + i * (cw + gap);
    const y = 400 + (1 - k) * 120 - ko * 80;
    ctx.save(); ctx.globalAlpha = k * (1 - ko);
    if (1 - k > 0.02) ctx.filter = `blur(${(1 - k) * 16 + ko * 14}px)`;
    roundRect(x, y, cw, chh, 28); ctx.fillStyle = '#ffffff'; ctx.fill();
    ctx.restore();
    token(cd.type, x + cw - 70, y + 70, 60, cd.c, t * 0.5 + i, k * (1 - ko));
    ctx.save(); ctx.globalAlpha = k * (1 - ko);
    const parts = parse(cd.s);
    ctx.textBaseline = 'alphabetic';
    ctx.font = `500 52px "${SANS}"`; ctx.fillStyle = C.navy; ctx.fillText(parts[0].s.trim(), x + 40, y + chh - 110);
    ctx.font = `italic 400 64px "${SERIF}"`; ctx.fillStyle = C.blue; ctx.fillText(parts[1].s, x + 40, y + chh - 44);
    ctx.restore();
  });

  // 36.4–41 Learning -> Practice -> Action
  const fa = 36.5, fb = 40.9;
  const kf = env(t, fa, fb + 0.4, 0.5, 0.6);
  if (kf > 0) {
    say(t, ['From building *stronger leaders*', 'and developing *critical capabilities*'], { a: fa, b: fb, size: 52, y: 270, lineDelay: 0.25 });
    const nodes = ['Learning', 'Practice', 'Action'], xs = [W / 2 - 520, W / 2, W / 2 + 520], y = 680;
    const lk = eInOut(prog(t, fa + 0.8, fa + 2.8));
    ctx.save(); ctx.globalAlpha = kf;
    ctx.strokeStyle = hexA('#ffffff', 0.25); ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(xs[0], y); ctx.lineTo(lerp(xs[0], xs[2], lk), y); ctx.stroke();
    const g = ctx.createLinearGradient(xs[0], 0, xs[2], 0); g.addColorStop(0, C.cyan); g.addColorStop(1, C.blue);
    ctx.strokeStyle = g; ctx.lineWidth = 5;
    ctx.beginPath(); ctx.moveTo(xs[0], y); ctx.lineTo(lerp(xs[0], xs[2], lk), y); ctx.stroke();
    // travelling pulse
    const pk = (t - fa) % 1.4 / 1.4;
    if (lk >= 1) { const px = lerp(xs[0], xs[2], pk); blob(px, y, 70, C.cyan, 0.8 * kf); }
    ctx.restore();
    nodes.forEach((n, i) => {
      const a = fa + 0.8 + i * 0.95, k = eBack(prog(t, a, a + 0.6));
      ctx.save(); ctx.globalAlpha = kf * clamp(k);
      ctx.beginPath(); ctx.arc(xs[i], y, 46 * k, 0, 7); ctx.fillStyle = '#0b0b2a'; ctx.fill();
      ctx.lineWidth = 4; ctx.strokeStyle = [C.cyan, C.sky, C.blue][i]; ctx.stroke();
      ctx.beginPath(); ctx.arc(xs[i], y, 14 * k, 0, 7); ctx.fillStyle = [C.cyan, C.sky, C.blue][i]; ctx.fill();
      ctx.restore();
      label(n, xs[i], y + 100, 40, hexA('#ffffff', kf * clamp(k)), { align: 'center', weight: 600 });
      label(['01', '02', '03'][i], xs[i], y - 90, 20, hexA('#ffffff', 0.5 * kf * clamp(k)), { align: 'center', weight: 600, ls: 4 });
    });
  }

  // 41–45 floating capability pills
  const pa = 41.2, pb = 45.0;
  const kp = env(t, pa, pb + 0.3, 0.6, 0.6);
  if (kp > 0) {
    say(t, ['to helping teams'], { a: pa + 0.1, b: pb, size: 40, y: 470, color: hexA('#ffffff', 0.7) });
    say(t, ['*perform better.*'], { a: pa + 0.35, b: pb, size: 120, y: 580, grad: true });
    const pills = [
      ['Communicate', C.orange, -560, -300], ['Collaborate', C.violet, 520, -320], ['Adapt', C.green, -650, 250],
      ['Lead', C.yellow, 640, 230], ['Decide', C.pink, -150, 380], ['Grow', C.sky, 250, -400],
    ];
    pills.forEach((p, i) => {
      const a = pa + 0.2 + i * 0.22, k = eOut5(prog(t, a, a + 0.9)) * (1 - eIn(prog(t, pb - 0.2 + i * 0.03, pb + 0.4)));
      if (k <= 0) return;
      const depth = 0.75 + rand(i) * 0.5;
      const x = W / 2 + p[2] * lerp(0.5, 1, k) + Math.sin(t * 0.8 + i) * 20 * depth;
      const y = H / 2 + p[3] * lerp(0.5, 1, k) + Math.cos(t * 0.7 + i * 2) * 16 * depth;
      ctx.save(); ctx.globalAlpha = k;
      ctx.translate(x, y); ctx.scale(depth, depth); ctx.rotate(Math.sin(t * 0.5 + i) * 0.06);
      if (depth < 0.9) ctx.filter = `blur(${(0.9 - depth) * 10}px)`;
      ctx.font = `600 34px "${SANS}"`; const w = ctx.measureText(p[0]).width + 80;
      const g = ctx.createLinearGradient(-w / 2, -36, w / 2, 36);
      g.addColorStop(0, mixHex(p[1], '#ffffff', 0.25)); g.addColorStop(1, p[1]);
      roundRect(-w / 2, -36, w, 72, 36); ctx.fillStyle = g; ctx.fill();
      ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(p[0], 0, 2);
      ctx.restore();
    });
  }

  // 45.2–47.6
  say(t, ['Because development shouldn’t feel', '*separate* from the business.'], { a: 45.3, b: 47.4, size: 72, lineDelay: 0.25 });

  // 47.6–50.5 giant motion type FORWARD
  const ga = 47.6, gb = 50.3;
  const kg = env(t, ga, gb, 0.4, 0.5);
  if (kg > 0) {
    const sweep = eOut(prog(t, ga, gb + 0.4));
    ctx.save();
    ctx.globalAlpha = kg * 0.95;
    ctx.font = `800 400px "${SANS}"`;
    ctx.textBaseline = 'middle';
    const g = ctx.createLinearGradient(0, 300, 0, 800); g.addColorStop(0, C.blue); g.addColorStop(1, C.cyan);
    ctx.fillStyle = g;
    const x = lerp(1500, -1100, sweep);
    ctx.filter = `blur(${(1 - eOut(prog(t, ga, ga + 1.2))) * 26 + 2}px)`;
    ctx.fillText('FORWARD', x, H / 2 + 20);
    ctx.restore();
    ctx.fillStyle = `rgba(0,0,10,${0.5 * kg})`; ctx.fillRect(0, 0, W, H);
    say(t, ['It should move the business', '*forward.*'], { a: ga + 0.3, b: gb - 0.1, size: 84, lineDelay: 0.2 });
  }
}

// ---- 5. THE DIFFERENCE 50–64 ----
function sceneDifference(t) {
  if (t < 49.8 || t > 64.6) return;
  floorGlow(t, env(t, 50.1, 64.4, 1, 0.6) * 0.5, 1);
  grid(t, 50.2, 56.0, 8, 5, 0.09);

  // counters crossed out
  say(t, ['Success isn’t measured by'], { a: 50.3, b: 53.4, size: 40, y: 260, color: hexA('#ffffff', 0.75) });
  const stats = [['attended', 248, C.orange], ['slides shown', 136, C.violet]];
  stats.forEach((s, i) => {
    const a = 50.7 + i * 0.6, k = env(t, a, 53.5, 0.6, 0.5);
    if (k <= 0) return;
    const x = W / 2 + (i ? 320 : -320), y = 540;
    const n = Math.round(s[1] * eOut(prog(t, a, a + 1.4)));
    ctx.save(); ctx.globalAlpha = k;
    ctx.font = `700 190px "${SANS}"`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = '#fff';
    ctx.fillText(String(n), x, y);
    ctx.font = `italic 400 54px "${SERIF}"`; ctx.fillStyle = s[2]; ctx.fillText('how many ' + s[0], x, y + 140);
    // strike
    const ks = eOut5(prog(t, 52.5 + i * 0.2, 53.0 + i * 0.2));
    ctx.strokeStyle = C.pink; ctx.lineWidth = 10; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(x - 220, y + 10); ctx.lineTo(x - 220 + 440 * ks, y + 10 - 40 * ks); ctx.stroke();
    ctx.restore();
  });

  say(t, ['It’s what happens'], { a: 53.8, b: 56.0, size: 64, y: 430 });
  say(t, ['*after.*'], { a: 54.2, b: 56.0, size: 250, y: 600, grad: true, dur: 1 });

  // domino chain 56.2 – 64.3
  const da = 56.2, db = 64.2;
  const kd = env(t, da, db, 0.5, 0.6);
  if (kd <= 0) return;
  const N = 16, x0 = 230, x1 = W - 230, base = 760, dh = 190, dw = 26;
  const steps = [
    ['Insight', 'When insight becomes *action.*', 0], ['Action', 'When action becomes *behavior.*', 5],
    ['Behavior', 'And better behavior creates', 10], ['Results', '*better business results.*', 15],
  ];
  const tfall = i => da + 0.9 + i * 0.42; // time domino i starts falling
  ctx.save(); ctx.globalAlpha = kd;
  // floor line
  ctx.strokeStyle = hexA('#ffffff', 0.2); ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(x0 - 60, base); ctx.lineTo(x1 + 60, base); ctx.stroke();
  for (let i = 0; i < N; i++) {
    const x = lerp(x0, x1, i / (N - 1));
    const appear = eOut5(prog(t, da + i * 0.03, da + 0.5 + i * 0.03));
    const f = prog(t, tfall(i), tfall(i) + 0.5);
    // rotate around bottom-right until resting on neighbour (~ 62°), last one goes flat
    const maxA = i === N - 1 ? Math.PI / 2 : 1.08;
    const ang = eIn(clamp(f * 1.3)) * maxA;
    const milestone = steps.find(s => s[2] === i);
    const col = milestone ? [C.cyan, C.sky, C.blue, C.cyan][steps.indexOf(milestone)] : SECONDARY[i % 8];
    const lit = f > 0.2;
    ctx.save();
    ctx.translate(x + dw / 2, base);
    ctx.rotate(ang);
    const hh = (milestone ? dh * 1.25 : dh) * appear;
    roundRect(-dw, -hh, dw, hh, 6);
    ctx.fillStyle = lit ? col : hexA('#ffffff', 0.18);
    if (lit) { ctx.shadowColor = col; ctx.shadowBlur = 30; }
    ctx.fill();
    ctx.restore();
  }
  ctx.restore();
  steps.forEach((s, j) => {
    const i = s[2], x = lerp(x0, x1, i / (N - 1));
    const a = tfall(i) + 0.1, k = env(t, a, db, 0.5, 0.5);
    if (k <= 0) return;
    label(s[0].toUpperCase(), x, base + 60, 22, hexA('#ffffff', 0.85 * k), { align: 'center', weight: 700, ls: 5 });
    blob(x, base, 120, C.cyan, 0.25 * k * (1 - prog(t, a, a + 1.5)));
  });
  // captions above
  say(t, ['When insight becomes *action.*'], { a: da + 0.9, b: 58.7, size: 66, y: 330 });
  say(t, ['When action becomes *behavior.*'], { a: 59.0, b: 61.0, size: 66, y: 330 });
  say(t, ['And better behavior creates', '*better business results.*'], { a: 61.3, b: 64.0, size: 66, y: 330, lineDelay: 0.3, grad: true });
}

// ---- 6. THE IMPACT EFFECT 64–77 ----
// network points: person (0) -> team ring (1..6) -> organisation rings
const NET = (() => {
  const pts = [{ x: 0, y: 0, ring: 0 }];
  for (let i = 0; i < 6; i++) { const a = i / 6 * Math.PI * 2 - Math.PI / 2; pts.push({ x: Math.cos(a) * 150, y: Math.sin(a) * 150, ring: 1 }); }
  const rings = [[300, 14], [450, 22], [600, 30], [760, 40]];
  rings.forEach(([r, n], ri) => {
    for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2 + ri * 0.3 + rand(ri * 50 + i) * 0.2; const rr = r + (rand(i + ri * 9) - 0.5) * 50; pts.push({ x: Math.cos(a) * rr * 1.2, y: Math.sin(a) * rr * 0.75, ring: ri + 2 }); }
  });
  return pts;
})();
function sceneEffect(t) {
  if (t < 63.8 || t > 77.6) return;
  const ks = env(t, 64.0, 77.3, 0.8, 0.5);
  floorGlow(t, ks * 0.4);
  const cx = W / 2, cy = 560;
  // camera pull-back as network grows
  const zoom = lerp(1.6, 0.85, eInOut(prog(t, 64.5, 73.5)));
  const ringVis = r => r === 0 ? prog(t, 64.3, 64.9) : r === 1 ? prog(t, 66.6, 67.4) : prog(t, 71.6 + (r - 2) * 0.35, 72.4 + (r - 2) * 0.35);
  const shiftK = prog(t, 72.2, 74.0); // culture colour wave
  ctx.save();
  ctx.translate(cx, cy); ctx.scale(zoom, zoom);
  ctx.globalAlpha = ks * (1 - eInOut(prog(t, 73.7, 74.5)) * 0.88);
  // connections
  ctx.lineWidth = 1.5 / zoom;
  NET.forEach((p, i) => {
    if (i === 0) return;
    const v = eOut(ringVis(p.ring));
    if (v <= 0) return;
    const parent = p.ring === 1 ? NET[0] : NET[1 + (i % 6)];
    ctx.strokeStyle = hexA('#ffffff', 0.13 * v);
    ctx.beginPath(); ctx.moveTo(parent.x * v, parent.y * v); ctx.lineTo(p.x * v, p.y * v); ctx.stroke();
  });
  // leader highlight 69–71.5
  const lk = env(t, 69.1, 72.0, 0.4, 0.6);
  NET.forEach((p, i) => {
    const v = eBack(ringVis(p.ring));
    if (v <= 0) return;
    const d = Math.hypot(p.x, p.y);
    const wave = clamp((shiftK * 1100 - d) / 200);
    let col = p.ring === 0 ? C.cyan : p.ring === 1 ? C.sky : hexA('#ffffff', 0.7);
    if (wave > 0 && p.ring >= 2) col = mixHex('#b8c4d6', SECONDARY[i % 8], wave);
    let r = p.ring === 0 ? 22 : p.ring === 1 ? 14 : 8;
    if (i === 1 && lk > 0) { r += 10 * lk; }
    ctx.beginPath(); ctx.arc(p.x * clamp(v, 0, 1.2), p.y * clamp(v, 0, 1.2), r * v, 0, 7);
    ctx.fillStyle = col; ctx.fill();
  });
  // pulse rings from the person
  for (let i = 0; i < 4; i++) {
    const rk = prog(t, 64.6 + i * 0.5, 66.6 + i * 0.5);
    if (rk > 0 && rk < 1) { ctx.strokeStyle = hexA(C.cyan, (1 - rk) * 0.7); ctx.lineWidth = 3 / zoom; ctx.beginPath(); ctx.arc(0, 0, 30 + rk * 260, 0, 7); ctx.stroke(); }
  }
  // leader burst lines
  if (lk > 0) {
    const L = NET[1];
    ctx.strokeStyle = hexA(C.yellow, 0.8 * lk); ctx.lineWidth = 3 / zoom;
    ctx.beginPath(); ctx.arc(L.x, L.y, 40 + 20 * Math.sin(t * 6), 0, 7); ctx.stroke();
    NET.forEach((p, i) => { if (p.ring === 1 && i !== 1) { const k2 = eOut(prog(t, 69.5, 70.4)); ctx.beginPath(); ctx.moveTo(L.x, L.y); ctx.lineTo(lerp(L.x, p.x, k2), lerp(L.y, p.y, k2)); ctx.stroke(); } });
  }
  ctx.restore();

  say(t, ['One person *develops.*'], { a: 64.6, b: 66.3, size: 70, y: 150 });
  say(t, ['A team gets *stronger.*'], { a: 66.7, b: 68.9, size: 70, y: 150 });
  say(t, ['A leader makes a *better decision.*'], { a: 69.2, b: 71.4, size: 70, y: 150, accent: C.yellow });
  say(t, ['A culture begins to *shift.*'], { a: 71.7, b: 74.0, size: 70, y: 150 });
  say(t, ['And eventually…', 'learning becomes something much bigger.'], { a: 74.2, b: 75.7, size: 52, y: 520, lineDelay: 0.45, stagger: 0.05 });

  // Progress — arches ripple outward (the fingerprint as a ripple)
  const pa = 75.8;
  const kp = env(t, pa, 77.4, 0.3, 0.5);
  if (kp > 0) {
    const rk = prog(t, pa, pa + 1.6);
    arches(W / 2, H / 2 + 330, 80 + rk * 200, 70 + rk * 40, 9, eOut(rk), C.cyan, 6, 0.6 * kp);
    say(t, ['*Progress.*'], { a: pa + 0.1, b: 77.2, size: 260, y: 520, grad: true, dur: 0.9 });
  }
}

// ---- 7. CLOSING 77–90 ----
function sceneClosing(t) {
  if (t < 76.9) return;
  const kd = env(t, 77.0, 86.0, 1, 0.6);
  floorGlow(t, kd * (0.5 + 0.5 * eOut(prog(t, 83.4, 84.5))));
  say(t, ['We don’t want learning to end', 'when the session *does.*'], { a: 77.2, b: 79.8, size: 72, lineDelay: 0.3 });
  say(t, ['We want it to *stay.*'], { a: 80.0, b: 81.2, size: 96 });
  say(t, ['To *spread.*'], { a: 81.4, b: 82.3, size: 110 });
  say(t, ['To *change something.*'], { a: 82.45, b: 83.4, size: 110 });
  // "To leave an IMPACT"
  say(t, ['To leave an'], { a: 83.55, b: 85.6, size: 64, y: 420 });
  const ki = env(t, 83.9, 85.7, 0.5, 0.4);
  if (ki > 0) {
    ctx.save();
    ctx.globalAlpha = ki;
    const s = lerp(1.25, 1, eOut5(prog(t, 83.9, 84.8)));
    ctx.translate(W / 2, 580); ctx.scale(s, s);
    ctx.filter = `blur(${(1 - eOut5(prog(t, 83.9, 84.6))) * 30 + eIn(prog(t, 85.3, 85.7)) * 30}px)`;
    ctx.font = `800 220px "${SANS}"`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.letterSpacing = '6px';
    const g = ctx.createLinearGradient(-500, 0, 500, 0); g.addColorStop(0, C.cyan); g.addColorStop(1, C.blue);
    ctx.fillStyle = g; ctx.fillText('IMPACT', 0, 0);
    ctx.restore();
  }

  // light reveal + logo
  const kw = eInOut(prog(t, 85.45, 86.25));
  if (kw > 0) {
    ctx.save();
    ctx.beginPath(); ctx.arc(W / 2, H / 2, Math.hypot(W, H) * 0.55 * kw + 0.1, 0, Math.PI * 2); ctx.clip();
    ctx.fillStyle = C.light; ctx.fillRect(0, 0, W, H);
    blob(W * 0.5 + Math.sin(t * 0.4) * 200, H * 1.35, 1000, C.cyan, 0.28);
    blob(W * 0.15, H * 1.2, 700, C.blue, 0.18);
    // ripple arches behind logo
    arches(W / 2, H / 2 + 420, 300, 90, 6, prog(t, 85.8, 88), C.cyan, 2, 0.25);
    const lsc = 1.75;
    const lift = eInOut(prog(t, 88.0, 88.7));
    drawLogo(W / 2, H / 2 - 40 * lift, lsc, prog(t, 86.0, 87.5), prog(t, 86.9, 87.8), prog(t, 87.5, 88.2), C.navy);
    say(t, ['Learning that *moves people.*  People that *move businesses.*'], { a: 88.3, b: 99, size: 40, y: H / 2 + 185, color: C.navy, accent: C.blue, stagger: 0.035 });
    ctx.restore();
  }
}

// ---------- Master ----------
function render(t) {
  ctx.save();
  ctx.filter = 'none'; ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  ctx.fillStyle = C.ink; ctx.fillRect(0, 0, W, H);
  sceneOpening(t);
  sceneChallenge(t);
  sceneIntro(t);
  sceneDoes(t);
  sceneDifference(t);
  sceneEffect(t);
  sceneClosing(t);
  const light = (t > 16.6 && t < 19.9) || t > 86.2;
  if (!light) vignette(0.55);
  drawGrain(t, t > 86 ? 0.03 : 0.06);
  // fade from black at start
  const fin = 1 - prog(t, 0, 0.4);
  if (fin > 0) { ctx.fillStyle = `rgba(0,0,0,${fin})`; ctx.fillRect(0, 0, W, H); }
  ctx.restore();
}
window.render = render;
window.DURATION = DURATION;
window.ready = document.fonts.load(`500 40px "${SANS}"`).then(() => document.fonts.load(`800 40px "${SANS}"`))
  .then(() => document.fonts.load(`italic 400 40px "${SERIF}"`)).then(() => document.fonts.ready).then(() => true);

// live preview when opened in a browser (?t=12 to seek)
if (!navigator.webdriver) {
  const q = new URLSearchParams(location.search); let t0 = performance.now() - (parseFloat(q.get('t')) || 0) * 1000;
  window.ready.then(() => { const loop = () => { const t = ((performance.now() - t0) / 1000) % DURATION; render(t); requestAnimationFrame(loop); }; loop(); });
}
