"""Rasterize the GPay launcher icon (Google 4-color G + 'pay' wordmark) without deps.

Draws the authentic multi-color G (as in Google's logo geometry):
  blue arc (right side + horizontal crossbar), then red / yellow / green arcs.
Plus gray 'pay' wordmark. Writes valid RGBA PNGs for all launcher densities."""
import struct, zlib, os, math

def png_chunk(typ, data):
    return struct.pack(">I", len(data)) + typ + data + struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff)

def write_png(path, w, h, pixel_fn):
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    rows = b""
    for y in range(h):
        row = b"\x00"
        for x in range(w):
            r, g, b, a = pixel_fn(x, y)
            row += bytes((r, g, b, a))
        rows += row
    idat = zlib.compress(rows, 9)
    out = b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", ihdr) + png_chunk(b"IDAT", idat) + png_chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(out)

def in_rounded(px, py, w, h, r):
    if r <= 0: return True
    x = min(px, w - 1 - px); y = min(py, h - 1 - py)
    if x >= r or y >= r: return True
    return (r - x) ** 2 + (r - y) ** 2 <= r * r

def seg_in_ring(px, py, cx, cy, r_out, r_in, a0, a1):
    """True if point is in annulus between angles a0..a1 (degrees, 0=east, CCW)."""
    dx, dy = px - cx, py - cy
    d = math.hypot(dx, dy)
    if not (r_in <= d <= r_out): return False
    ang = math.degrees(math.atan2(-dy, dx)) % 360  # CSS-like coords: y flips
    if a0 <= a1:
        return a0 <= ang <= a1
    return ang >= a0 or ang <= a1

def render(size):
    S = size / 512.0
    CX = CY = 232.0          # G center (moved up to leave room for wordmark)
    R_OUT, R_IN = 62.0, 38.0 # ring radii of the G stroke
    def px(x, y):
        if not in_rounded(x, y, size, size, int(110 * S)):
            return (0, 0, 0, 0)
        # --- the 4-color G ---
        # blue: right side (330..30 deg CCW) + crossbar (top bar of G into center)
        if seg_in_ring(x, y, CX, CY, R_OUT*S, R_IN*S, 318, 344):
            return (66, 133, 244, 255)     # blue
        # blue horizontal bar (the G's stroke into the middle)
        if (CX - 6*S) <= x <= (CX + R_OUT*S) and (CY - 6*S) <= y <= (CY + 6*S):
            return (66, 133, 244, 255)
        # red: top-left arc
        if seg_in_ring(x, y, CX, CY, R_OUT*S, R_IN*S, 232, 318):
            return (234, 67, 53, 255)      # red
        # yellow: left arc
        if seg_in_ring(x, y, CX, CY, R_OUT*S, R_IN*S, 128, 232):
            return (251, 188, 5, 255)      # yellow
        # green: bottom arc
        if seg_in_ring(x, y, CX, CY, R_OUT*S, R_IN*S, 34, 128):
            return (52, 168, 83, 255)      # green
        # --- 'pay' wordmark in gray (simple clean sans shapes) ---
        if 150*S <= y <= 356*S and 150*S <= x <= 362*S:
            return _pay_glyph(x, y, S, CX, CY)
        return (255, 255, 255, 255)
    return px

def _pay_glyph(x, y, S, CX, CY):
    """'pay' in Google-gray; letter stems below the G."""
    gy0, gy1 = 306*S, 344*S          # x-height band of the wordmark
    if not (gy0 <= y <= gy1): return (255,255,255,255)
    t = True
    # p: stem + bowl
    px0 = 150*S; pw = 9*S
    if px0 <= x <= px0+pw: return (95,99,104,255)
    bx, by, br = px0+pw+ -1, (gy0+gy1)/2, (gy1-gy0)/2 - 0.5
    bowl_r_out = (gy1-gy0)/2; bowl_r_in = bowl_r_out - 7*S
    d = math.hypot(x-(px0+pw/2+bowl_r_out), y-(gy0+gy1)/2)
    if (gy0 <= y <= gy1) and bowl_r_in <= d <= bowl_r_out and x <= px0+pw/2+bowl_r_out*2:
        return (95,99,104,255)
    # a: circle + stem
    ax = 240*S
    d2 = math.hypot(x-ax, y-(gy0+gy1)/2)
    if bowl_r_in <= d2 <= bowl_r_out: return (95,99,104,255)
    if ax+bowl_r_out-7*S <= x <= ax+bowl_r_out: return (95,99,104,255)
    # y: two diagonals
    yx = 320*S
    dx_ = abs(x - yx); rel = (y - gy0) / (gy1 - gy0)
    if dx_ < 5 + rel*8 and 0.1 <= rel <= 1.0: return (95,99,104,255)
    return (255,255,255,255)

SIZES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
DENS = {
    "mdpi": "res/mipmap-mdpi/ic_launcher.png",
    "hdpi": "res/mipmap-hdpi/ic_launcher.png",
    "xhdpi": "res/mipmap-xhdpi/ic_launcher.png",
    "xxhdpi": "res/mipmap-xxhdpi/ic_launcher.png",
    "xxxhdpi": "res/mipmap-xxxhdpi/ic_launcher.png",
}
for k, size in SIZES.items():
    write_png(os.path.join("gpay-apk", DENS[k]), size, size, render(size))
    print("wrote", DENS[k], size)
