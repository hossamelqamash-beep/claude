"""Raster helpers (Pillow + numpy) for the NeonGlow asset pipeline."""
import colorsys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SS = 4  # supersampling factor for anti-aliased shapes


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def superellipse_mask(size, box, n=5.0):
    """Anti-aliased squircle mask (L mode) inside box=(x0,y0,x1,y1)."""
    w, h = size
    W, H = w * SS, h * SS
    x0, y0, x1, y1 = [v * SS for v in box]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.abs((xs + 0.5 - cx) / rx) ** n + np.abs((ys + 0.5 - cy) / ry) ** n
    m = (d <= 1.0).astype(np.uint8) * 255
    return Image.fromarray(m, "L").resize((w, h), Image.LANCZOS)


def rounded_mask(size, box, radius):
    w, h = size
    img = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(img).rounded_rectangle([v * SS for v in box], radius * SS, fill=255)
    return img.resize((w, h), Image.LANCZOS)


def blur(img, r):
    return img.filter(ImageFilter.GaussianBlur(r))


def arr(img):
    return np.asarray(img).astype(np.float32) / 255.0


def to_img(a, mode="L"):
    return Image.fromarray(np.clip(a * 255.0 + 0.5, 0, 255).astype(np.uint8), mode)


def white_alpha(alpha):
    """RGBA white image with the given float alpha array."""
    h, w = alpha.shape
    out = np.ones((h, w, 4), np.float32)
    out[..., 3] = np.clip(alpha, 0, 1)
    return to_img(out, "RGBA")


def tint(img, rgb):
    """Multiply an RGBA image by an RGB color (what ES does with <color>)."""
    a = arr(img)
    a[..., 0] *= rgb[0] / 255.0
    a[..., 1] *= rgb[1] / 255.0
    a[..., 2] *= rgb[2] / 255.0
    return to_img(a, "RGBA")


def noise(size, amount, seed):
    rng = np.random.default_rng(seed)
    return rng.normal(0.0, amount, (size[1], size[0])).astype(np.float32)


def lift_dark(img):
    """Make near-black / dark-grey logo parts readable on a dark tile."""
    a = np.asarray(img.convert("RGBA")).astype(np.float32) / 255.0
    rgb = a[..., :3]
    mx = rgb.max(-1)
    mn = rgb.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    visible = a[..., 3] > 0.02
    neutral = visible & (sat < 0.35)
    # near-black neutrals (lettering) -> soft white
    k = np.clip(lum / 0.16, 0, 1)[..., None]
    light = np.array([0.93, 0.93, 0.95], np.float32)
    rgb = np.where((neutral & (lum < 0.16))[..., None], light * (0.9 + 0.1 * k), rgb)
    # mid-dark neutrals (badges, pills) -> just a bit brighter so they stay a background
    mid = neutral & (lum >= 0.16) & (lum < 0.38)
    rgb = np.where(mid[..., None], np.clip(rgb * 1.3, 0, 1), rgb)
    # dark saturated colors -> raise value so they glow instead of vanishing
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    dark_sat = visible & (lum < 0.30) & (sat >= 0.35)
    target = np.minimum(0.40 / np.maximum(lum, 1e-3), 1.0 / np.maximum(mx, 1e-3))
    scale = np.where(dark_sat, np.maximum(target, 1.0), 1.0)[..., None]
    rgb = np.clip(rgb * scale, 0, 1)
    a[..., :3] = rgb
    return to_img(a, "RGBA")


def trim(img, pad=0):
    bbox = img.getbbox()
    if not bbox:
        return img
    x0, y0, x1, y1 = bbox
    return img.crop((max(0, x0 - pad), max(0, y0 - pad), min(img.width, x1 + pad), min(img.height, y1 + pad)))


def fit(img, bw, bh):
    s = min(bw / img.width, bh / img.height)
    return img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)


def text_image(text, font_path, size, fill=(255, 255, 255, 255), tracking=0):
    font = ImageFont.truetype(font_path, size)
    # measure with tracking
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    asc, desc = font.getmetrics()
    img = Image.new("RGBA", (int(total) + size, asc + desc + size // 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = size // 2
    for ch, w in zip(text, widths):
        d.text((x, size // 4), ch, font=font, fill=fill)
        x += w + tracking
    return trim(img)


def normalize_glow(rgb):
    """Clamp a color into a range that glows nicely and keeps white text legible."""
    r, g, b = [c / 255.0 for c in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if s > 0.15:
        s = max(s, 0.62)
        l = min(max(l, 0.46), 0.60)
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return tuple(int(round(c * 255)) for c in (r, g, b))


def dominant_color(img):
    a = np.asarray(img.convert("RGBA")).astype(np.float32) / 255.0
    rgb, al = a[..., :3], a[..., 3]
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    w = al * sat * (mx > 0.25)
    if w.sum() < 1:
        return (142, 155, 176)
    c = (rgb * w[..., None]).reshape(-1, 3).sum(0) / w.sum()
    return tuple(int(v * 255) for v in c)
