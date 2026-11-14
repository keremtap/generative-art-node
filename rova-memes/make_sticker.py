"""Giphy/Instagram-Sticker: transparente GIF-Loops ohne Text (oder nur ein Wort).
Aufruf: python3 make_sticker.py   -> Ausgabe in sticker/
Farben oben in ACCENT/MINT anpassbar (z. B. auf eure Markenfarben).
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'sticker'); os.makedirs(OUT, exist_ok=True)
S = 480            # Ausgabegröße
R = 2              # Supersampling
WS = S * R
BG = (244, 244, 245)
ACCENT = (108, 76, 245)   # Violett (Nova / Akzent)
MINT = (34, 197, 139)     # Grün (erledigt)
YELLOW = (255, 200, 40)
PINK = (255, 90, 130)
WHITE = (255, 255, 255)
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
TAU = 2 * math.pi

# ---------- Produkt freistellen (scharfe Kante, kein Schatten) ----------
src = Image.open(os.path.join(HERE, 'rova_source.png')).convert('RGB')
src = src.resize((src.width * 2, src.height * 2), Image.LANCZOS)
diff = ImageChops.difference(src, Image.new('RGB', src.size, BG)).convert('L')
mask = diff.point(lambda v: 255 if v > 16 else 0).filter(ImageFilter.MedianFilter(7))
m = mask.copy(); ImageDraw.floodfill(m, (0, 0), 128)
mask = m.point(lambda v: 0 if v == 128 else 255).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1))
PROD = src.copy(); PROD.putalpha(mask); PROD = PROD.crop(mask.getbbox())

def layer(): return Image.new('RGBA', (WS, WS), (0, 0, 0, 0))

def box(img, cx, cy, width, sx=1, sy=1, rot=0, mirror=False):
    """Rova-Box mittig bei (cx, cy) in Supersampling-Koordinaten."""
    k = width / PROD.width
    w, h = max(2, int(PROD.width * k * abs(sx))), max(2, int(PROD.height * k * sy))
    q = PROD.resize((w, h), Image.LANCZOS)
    if mirror: q = q.transpose(Image.FLIP_LEFT_RIGHT)
    if rot: q = q.rotate(rot, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(q, (int(cx - q.width / 2), int(cy - q.height / 2)))

def star(d, cx, cy, r, fill, rot=0, points=4, inner=.38):
    pts = []
    for i in range(points * 2):
        a = rot + i * math.pi / points
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)

def heart(d, cx, cy, r, fill):
    d.ellipse([cx - r, cy - r * .9, cx, cy + r * .1], fill=fill)
    d.ellipse([cx, cy - r * .9, cx + r, cy + r * .1], fill=fill)
    d.polygon([(cx - r * .97, cy - r * .25), (cx + r * .97, cy - r * .25), (cx, cy + r * 1.05)], fill=fill)

def check(d, cx, cy, r, bg=MINT):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg)
    d.line([(cx - r * .45, cy), (cx - r * .1, cy + r * .38), (cx + r * .5, cy - r * .35)],
           fill=WHITE, width=max(2, int(r * .28)), joint='curve')

# ---------- Export mit Transparenz + weißem Sticker-Rand ----------
def finish(frame, outline=True):
    f = frame.resize((S, S), Image.LANCZOS)
    a = f.getchannel('A')
    if outline:
        edge = a.point(lambda v: 255 if v > 60 else 0).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(.7))
        base = Image.new('RGBA', (S, S), WHITE + (0,)); base.putalpha(edge)
        base.alpha_composite(f); f = base
    a = f.getchannel('A').point(lambda v: 255 if v > 110 else 0)
    rgb = Image.new('RGB', (S, S), WHITE); rgb.paste(f.convert('RGB'), mask=a)
    p = rgb.quantize(255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = p.getpalette()[:255 * 3]; pal += [0] * (768 - len(pal)); p.putpalette(pal)
    p.paste(255, mask=a.point(lambda v: 255 - v))
    return p

def save(frames, name, dur=50, outline=True):
    ps = [finish(f, outline) for f in frames]
    ps[0].save(os.path.join(OUT, name + '.gif'), save_all=True, append_images=ps[1:], duration=dur,
               loop=0, transparency=255, disposal=2, optimize=False)
    print('ok', name, len(ps), os.path.getsize(os.path.join(OUT, name + '.gif')) // 1024, 'KB')

C = WS / 2

# ================= ROVA =================
def rova_jelly(n=28):
    fr = []
    for i in range(n):
        t = i / n; ph = math.sin(t * TAU)
        hop = max(0, ph) * 140
        sq = (.16 if ph < 0 else -.06) * abs(ph)
        img = layer(); box(img, C, C + 120 - hop, 560, 1 + sq, 1 - sq); fr.append(img)
    save(fr, 'rova_01_huepfen', 40)

def rova_spin(n=32):
    fr = []
    for i in range(n):
        a = i / n * TAU; c = math.cos(a)
        img = layer(); box(img, C, C + 20 * math.sin(a * 2), 600, sx=max(.04, abs(c)), mirror=c < 0); fr.append(img)
    save(fr, 'rova_02_drehen', 45)

def rova_sparkle(n=30):
    rnd = random.Random(3)
    sp = [(rnd.uniform(.12, .88) * WS, rnd.uniform(.15, .85) * WS, rnd.uniform(28, 60), rnd.random()) for _ in range(9)]
    fr = []
    for i in range(n):
        t = i / n; img = layer(); d = ImageDraw.Draw(img)
        box(img, C, C + 30, 560, rot=2 * math.sin(t * TAU))
        for x, y, r, ph in sp:
            s = max(0, math.sin((t + ph) * TAU))
            if abs(x - C) < 260 and abs(y - C - 30) < 150: continue
            star(d, x, y, r * s, YELLOW if ph > .5 else WHITE if ph > .25 else ACCENT, rot=t * 2)
        fr.append(img)
    save(fr, 'rova_03_glitzern', 50)

def rova_hearts(n=36):
    rnd = random.Random(7)
    hs = [(rnd.uniform(.25, .75) * WS, rnd.random(), rnd.uniform(26, 50), rnd.choice([PINK, (255, 60, 90), (255, 140, 170)])) for _ in range(7)]
    fr = []
    for i in range(n):
        t = i / n; img = layer(); d = ImageDraw.Draw(img)
        pulse = 1 + .05 * max(0, math.sin(t * TAU * 2)) ** 4
        box(img, C, C + 170, 520 * pulse)
        for x, ph, r, col in hs:
            u = (t + ph) % 1
            y = C + 60 - u * 620; xx = x + 40 * math.sin(u * TAU * 1.5 + ph * 6)
            rr = r * min(1, u * 5) * (1 - max(0, u - .8) * 5)
            if rr > 2: heart(d, xx, y, rr, col)
        fr.append(img)
    save(fr, 'rova_04_herzen', 50)

def rova_tasks(n=40):
    """Häkchen poppen aus der Box: Aufgaben erledigt."""
    fr = []; slots = [(-260, -330), (0, -400), (260, -330)]
    for i in range(n):
        t = i / n; img = layer(); d = ImageDraw.Draw(img)
        kick = sum(max(0, 1 - abs(t - k / 3 - .05) * 25) for k in range(3))
        box(img, C, C + 210, 540, 1 + .06 * kick, 1 - .08 * kick)
        for k, (dx, dy) in enumerate(slots):
            u = (t - k / 3 - .05)
            if u < 0: continue
            e = min(1, u * 6); sc = 1 + .25 * math.sin(min(1, u * 6) * math.pi)
            if t > .9: sc *= max(0, 1 - (t - .9) * 10)
            if sc > .05: check(d, C + dx * e, C + 150 + (dy - 0) * e, 70 * sc)
        fr.append(img)
    save(fr, 'rova_05_erledigt', 50)

def rova_dance(n=24):
    fr = []
    for i in range(n):
        t = i / n; b = abs(math.sin(t * TAU))
        img = layer(); box(img, C + 50 * math.sin(t * TAU), C + 80 - 60 * b, 560,
                           1 + .05 * (1 - b), 1 - .07 * (1 - b), rot=9 * math.sin(t * TAU))
        fr.append(img)
    save(fr, 'rova_06_tanzen', 45)

def rova_think(n=36):
    fr = []
    for i in range(n):
        t = i / n; img = layer(); d = ImageDraw.Draw(img)
        box(img, C, C + 200, 520, rot=3 * math.sin(t * TAU))
        bx, by = C + 120, C - 170
        d.ellipse([C + 30, C + 10, C + 70, C + 50], fill=WHITE, outline=(210, 210, 218), width=6)
        d.ellipse([C + 60, C - 60, C + 120, C], fill=WHITE, outline=(210, 210, 218), width=6)
        d.rounded_rectangle([bx - 190, by - 110, bx + 190, by + 110], 100, fill=WHITE, outline=(210, 210, 218), width=6)
        for k in range(3):
            h = max(0, math.sin((t * 2 - k * .18) * TAU))
            d.ellipse([bx - 110 + k * 110 - 30, by - 30 - h * 30, bx - 110 + k * 110 + 30, by + 30 - h * 30],
                      fill=ACCENT if h > .3 else (190, 190, 200))
        fr.append(img)
    save(fr, 'rova_07_denkt_nach', 45)

def rova_drop(n=36):
    fr = []
    for i in range(n):
        t = i / n; img = layer(); d = ImageDraw.Draw(img)
        if t < .3: y = -300 + (C + 260) * (t / .3) ** 2; sx = sy = 1
        else:
            u = (t - .3) / .7; y = C - 40 - abs(math.sin(u * math.pi * 2)) * 140 * math.exp(-3 * u)
            s = .18 * math.exp(-6 * u); sx, sy = 1 + s, 1 - s
        if .3 <= t < .55:
            u = (t - .3) / .25
            for side in (-1, 1):
                for k in range(3):
                    r = (40 - k * 10) * (1 - u)
                    px = C + side * (300 + u * 120 + k * 50); py = C + 110 - k * 30 - u * 40
                    if r > 3: d.ellipse([px - r, py - r, px + r, py + r], fill=(225, 225, 232))
        box(img, C, y, 560, sx, sy); fr.append(img)
    save(fr, 'rova_08_plopp', 45)

# ================= NOVA =================
def phone(img, cx, cy, h, rot=0, screen=None):
    w = h * .52
    ph = Image.new('RGBA', (int(w) + 40, int(h) + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(ph)
    d.rounded_rectangle([20, 20, 20 + w, 20 + h], int(w * .2), fill=(30, 30, 38))
    d.rounded_rectangle([20 + w * .07, 20 + h * .04, 20 + w * .93, 20 + h * .96], int(w * .15), fill=ACCENT)
    d.rounded_rectangle([20 + w * .38, 20 + h * .065, 20 + w * .62, 20 + h * .09], 10, fill=(30, 30, 38))
    if screen: screen(d, 20 + w / 2, 20 + h / 2, w, h)
    if rot: ph = ph.rotate(rot, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(ph, (int(cx - ph.width / 2), int(cy - ph.height / 2)))

def nova_ring(n=30):
    fr = []
    for i in range(n):
        t = i / n; img = layer(); d = ImageDraw.Draw(img)
        ring = (i // 3) % 2 == 0 and t < .6
        rot = 9 * math.sin(i * 2.4) if t < .6 else 0
        for k in range(3):
            u = (t * 2 + k / 3) % 1
            r = 260 + u * 300; a = int(255 * (1 - u))
            for side in (-1, 1):
                st, en = (-40, 40) if side > 0 else (140, 220)
                d.arc([C - r, C - r, C + r, C + r], st, en, fill=ACCENT + (a,), width=26)
        def scr(dd, x, y, w, h):
            dd.ellipse([x - w * .3, y - w * .3, x + w * .3, y + w * .3], fill=MINT)
            dd.text((x, y), '☎', font=ImageFont.truetype(BOLD, int(w * .34)), fill=WHITE, anchor='mm')
        phone(img, C, C, 560, rot, scr); fr.append(img)
    save(fr, 'nova_01_klingelt', 45)

def nova_wave(n=30):
    fr = []; bars = 9
    for i in range(n):
        t = i / n; img = layer(); d = ImageDraw.Draw(img)
        d.rounded_rectangle([C - 380, C - 230, C + 380, C + 230], 230, fill=ACCENT)
        for k in range(bars):
            x = C - 300 + k * 75
            h = 30 + 150 * abs(math.sin(t * TAU * 2 + k * .7)) * (1 - abs(k - 4) / 6)
            d.rounded_rectangle([x - 22, C - h, x + 22, C + h], 22, fill=WHITE)
        fr.append(img)
    save(fr, 'nova_02_spricht', 40)

def nova_bubble(n=36):
    fr = []
    for i in range(n):
        t = i / n; img = layer(); d = ImageDraw.Draw(img)
        sc = 1 + .04 * math.sin(t * TAU * 2)
        w, h = 620 * sc, 400 * sc
        d.rounded_rectangle([C - w / 2, C - h / 2 - 40, C + w / 2, C + h / 2 - 40], 120, fill=WHITE, outline=ACCENT, width=18)
        d.polygon([(C - 140, C + h / 2 - 50), (C - 220, C + h / 2 + 90), (C - 30, C + h / 2 - 50)], fill=ACCENT)
        d.polygon([(C - 132, C + h / 2 - 58), (C - 190, C + h / 2 + 45), (C - 52, C + h / 2 - 58)], fill=WHITE)
        for k in range(3):
            hh = max(0, math.sin((t * 2 - k * .15) * TAU))
            r = 42 + 10 * hh
            d.ellipse([C - 170 + k * 170 - r, C - 40 - hh * 40 - r, C - 170 + k * 170 + r, C - 40 - hh * 40 + r], fill=ACCENT)
        fr.append(img)
    save(fr, 'nova_03_tippt', 45)

def nova_done(n=36):
    """Anruf kommt rein -> wird zum Häkchen."""
    fr = []
    for i in range(n):
        t = i / n; img = layer(); d = ImageDraw.Draw(img)
        if t < .45:
            rot = 10 * math.sin(i * 2.5)
            phone(img, C, C, 560, rot)
        elif t < .55:
            u = (t - .45) / .1
            phone(img, C, C, 560 * (1 - u) + 1)
        else:
            u = min(1, (t - .55) / .12)
            r = 260 * (1 + .25 * math.sin(u * math.pi)) if u < 1 else 260
            check(d, C, C, r)
            for k in range(8):
                a = k / 8 * TAU; v = min(1, (t - .55) / .2)
                if v < 1:
                    rr = 300 + v * 140
                    star(d, C + rr * math.cos(a), C + rr * math.sin(a), 40 * (1 - v), YELLOW)
        fr.append(img)
    save(fr, 'nova_04_erledigt', 50)

# ================= WORT-STICKER & OPTIK =================
def word(text, name, color, n=30):
    f = ImageFont.truetype(BOLD, 250)
    fr = []
    for i in range(n):
        t = i / n; img = layer(); d = ImageDraw.Draw(img)
        widths = [d.textlength(ch, font=f) for ch in text]
        x = C - sum(widths) / 2
        for k, ch in enumerate(text):
            b = max(0, math.sin((t - k * .12) * TAU))
            y = C - 30 - b * 90
            d.text((x + widths[k] / 2 + 10, y + 14), ch, font=f, fill=(30, 30, 38), anchor='mm')
            d.text((x + widths[k] / 2, y), ch, font=f, fill=color, anchor='mm')
            x += widths[k]
        fr.append(img)
    save(fr, name, 45)

def burst(n=24):
    fr = []
    for i in range(n):
        t = i / n; img = layer(); d = ImageDraw.Draw(img)
        star(d, C, C, 300 + 40 * math.sin(t * TAU), YELLOW, rot=t * TAU / 8, points=12, inner=.72)
        star(d, C, C, 180 + 30 * math.sin(t * TAU + 1), ACCENT, rot=-t * TAU / 8, points=4, inner=.35)
        for k in range(6):
            a = k / 6 * TAU + t * TAU / 6; rr = 380
            star(d, C + rr * math.cos(a), C + rr * math.sin(a), 40 * abs(math.sin(t * TAU + k)), WHITE)
        fr.append(img)
    save(fr, 'optik_01_stern', 45)

def rova_logo_glow(n=30):
    """Box mit pulsierendem Glanz-Ring (Signal 'Rova ist an')."""
    fr = []
    for i in range(n):
        t = i / n; img = layer(); d = ImageDraw.Draw(img)
        for k in range(2):
            u = (t + k / 2) % 1; r = 200 + u * 260
            d.ellipse([C - r, C - r * .55 + 60, C + r, C + r * .55 + 60], outline=MINT + (int(255 * (1 - u)),), width=22)
        box(img, C, C, 580, rot=0); fr.append(img)
    save(fr, 'rova_09_signal', 45)

if __name__ == '__main__':
    rova_jelly(); rova_spin(); rova_sparkle(); rova_hearts(); rova_tasks()
    rova_dance(); rova_think(); rova_drop(); rova_logo_glow()
    nova_ring(); nova_wave(); nova_bubble(); nova_done()
    word('Rova', 'wort_rova', WHITE); word('Nova', 'wort_nova', ACCENT); burst()
