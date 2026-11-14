"""Rova Meme-Serie: mehrere Formate, Sprüche zentral in SERIE anpassbar.
Aufruf: python3 make_serie.py  (Ausgabe in serie/)
"""
import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'serie'); os.makedirs(OUT, exist_ok=True)
W = 720
BG = (244, 244, 245); INK = (24, 24, 30); GREY = (120, 120, 128)
GREEN = (34, 160, 90); RED = (210, 60, 60); ACCENT = (40, 40, 48)
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def F(s, b=True): return ImageFont.truetype(BOLD if b else REG, s)

# ---------- Produkt freistellen ----------
src = Image.open(os.path.join(HERE, 'rova_source.png')).convert('RGB')
diff = ImageChops.difference(src, Image.new('RGB', src.size, BG)).convert('L')
mask = diff.point(lambda v: 255 if v > 14 else 0).filter(ImageFilter.MedianFilter(5))
m = mask.copy(); ImageDraw.floodfill(m, (0, 0), 128)
mask = m.point(lambda v: 0 if v == 128 else 255).filter(ImageFilter.GaussianBlur(0.8))
PROD = src.copy(); PROD.putalpha(mask); PROD = PROD.crop(mask.getbbox())

# ---------- Helfer ----------
def canvas(color=BG): return Image.new('RGB', (W, W), color)

def shadow(img, cx, cy, w, alpha):
    sh = Image.new('L', img.size, 0)
    ImageDraw.Draw(sh).ellipse([cx - w, cy - w * .18, cx + w, cy + w * .18], fill=int(alpha))
    img.paste((200, 200, 206), mask=sh.filter(ImageFilter.GaussianBlur(16)))

def place(img, scale, cx, bottom, sx=1, sy=1, rot=0, with_shadow=True, lift=0):
    q = PROD.resize((max(1, int(PROD.width * scale * sx)), max(1, int(PROD.height * scale * sy))), Image.LANCZOS)
    if rot: q = q.rotate(rot, resample=Image.BICUBIC, expand=True)
    if with_shadow:
        k = max(0.3, 1 - lift / 300)
        shadow(img, cx, bottom + 6 + lift, PROD.width * scale * .45 * k, 120 * k)
    img.paste(q, (int(cx - q.width / 2), int(bottom - q.height)), q)

def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def text_block(img, text, y, size=44, maxw=W - 80, color=INK, bold=True, anchor_y='top', align='center', x=None):
    d = ImageDraw.Draw(img)
    s = size
    while True:
        f = F(s, bold); lines = wrap(d, text, f, maxw)
        if len(lines) <= 3 or s <= 22: break
        s -= 2
    lh = int(s * 1.22); h = lh * len(lines)
    y0 = y - h if anchor_y == 'bottom' else (y - h / 2 if anchor_y == 'middle' else y)
    for i, ln in enumerate(lines):
        if align == 'center':
            d.text((W / 2 if x is None else x, y0 + i * lh), ln, font=f, fill=color, anchor='ma')
        else:
            d.text((x, y0 + i * lh), ln, font=f, fill=color)
    return y0 + h

def ease_out_back(t):
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def save(frames, name, dur=50, hold=0):
    frames = frames + [frames[-1]] * hold
    frames[0].save(os.path.join(OUT, name + '.gif'), save_all=True, append_images=frames[1:],
                   duration=dur, loop=0, optimize=True)
    print('ok', name, len(frames))

# ---------- Format 1: Klassisch oben/unten mit Animation ----------
def fmt_caption(name, top, bottom, motion='drop'):
    fr = []; n = 40
    for i in range(n):
        t = i / n; c = canvas(); sx = sy = 1; rot = 0; x = W / 2; bot = 520; sc = .78; lift = 0
        if motion == 'drop':
            if t < .3: lift = 520 * (1 - (t / .3) ** 2); bot -= lift
            else:
                u = (t - .3) / .7; lift = abs(math.sin(u * math.pi * 3)) * 90 * math.exp(-4 * u); bot -= lift
                sq = .1 * math.exp(-5 * u) * max(0, math.cos(u * math.pi * 6)); sx, sy = 1 + sq, 1 - sq
        elif motion == 'shake':
            if (i // 8) % 2 == 0: x += 9 * math.sin(i * 2.3); rot = 2 * math.sin(i * 1.9)
        elif motion == 'pop':
            sc *= max(.05, ease_out_back(min(1, i / 12)))
        elif motion == 'float':
            lift = 16 + 16 * math.sin(t * 2 * math.pi); bot -= lift; rot = 1.5 * math.sin(t * 2 * math.pi + .6)
        place(c, sc, x, bot, sx, sy, rot, lift=lift)
        text_block(c, top, 40, 44)
        if bottom and (motion != 'pop' or i > 16): text_block(c, bottom, 690, 40, anchor_y='bottom')
        fr.append(c)
    save(fr, name, 50, hold=20)

# ---------- Format 2: Ohne Rova / Mit Rova (Split) ----------
def fmt_split(name, left_title, notes, right_title, right_text):
    fr = []
    note_pos = [(70, 180), (200, 250), (90, 340), (210, 420), (110, 500), (60, 260)]
    cols = [(255, 236, 140), (255, 205, 160), (200, 230, 255), (255, 190, 200), (210, 245, 200), (255, 236, 140)]
    for i in range(36):
        c = canvas(); d = ImageDraw.Draw(c)
        d.rectangle([W / 2, 0, W, W], fill=(252, 252, 253)); d.line([W / 2, 30, W / 2, W - 30], fill=(215, 215, 220), width=2)
        d.text((W / 4, 50), left_title, font=F(34), fill=RED, anchor='mm')
        d.text((3 * W / 4, 50), right_title, font=F(34), fill=GREEN, anchor='mm')
        for k, txt in enumerate(notes):
            px, py = note_pos[k % len(note_pos)]
            jx = 6 * math.sin(i * 1.7 + k * 2); jy = 5 * math.cos(i * 2.1 + k)
            note = Image.new('RGBA', (150, 70), cols[k % len(cols)] + (255,))
            nd = ImageDraw.Draw(note); fs = 22
            while nd.textlength(txt, font=F(fs)) > 136: fs -= 1
            nd.text((75, 35), txt, font=F(fs), fill=INK, anchor='mm')
            note = note.rotate(8 * math.sin(i * .9 + k * 1.3) + (k % 3 - 1) * 6, expand=True, resample=Image.BICUBIC)
            c.paste(note, (int(px + jx), int(py + jy)), note)
        lift = 12 + 10 * math.sin(i / 36 * 2 * math.pi)
        place(c, .42, 3 * W / 4, 470 - lift, lift=lift)
        text_block(c, right_text, 540, 28, maxw=W / 2 - 50, x=3 * W / 4)
        fr.append(c)
    save(fr, name, 70)

# ---------- Format 3: Chat-Verlauf ----------
def bubble(c, text, y, me, show_chars=None):
    d = ImageDraw.Draw(c); f = F(27, False)
    t = text if show_chars is None else text[:show_chars]
    lines = wrap(d, text, f, 400)
    shown, rest = [], t
    for ln in lines:
        shown.append(rest[:len(ln)]); rest = rest[len(ln):].lstrip()
    bw = max(d.textlength(l, font=f) for l in lines) + 44; bh = 36 * len(lines) + 28
    x0 = W - 40 - bw if me else 40
    fill = (40, 120, 255) if me else (255, 255, 255)
    d.rounded_rectangle([x0, y, x0 + bw, y + bh], 22, fill=fill, outline=None if me else (225, 225, 230), width=2)
    for k, l in enumerate(shown):
        d.text((x0 + 22, y + 14 + k * 36), l, font=f, fill=(255, 255, 255) if me else INK)
    return y + bh

def label(c, txt, y, right):
    d = ImageDraw.Draw(c); f = F(20)
    d.text((W - 44 if right else 44, y), txt, font=f, fill=GREY, anchor='ra' if right else 'la')

def fmt_chat(name, who, ask, answer):
    fr = []
    for i in range(70):
        c = canvas((236, 237, 241))
        place(c, .3, 130, 140, with_shadow=False)
        d = ImageDraw.Draw(c); d.text((230, 95), 'Rova', font=F(30), fill=INK, anchor='lm')
        d.text((232, 125), 'im Büro, on-premise', font=F(18, False), fill=GREY, anchor='lm')
        d.line([40, 170, W - 40, 170], fill=(215, 215, 222), width=2)
        if i >= 4:
            label(c, who, 200, True)
            y = bubble(c, ask, 228, True)
            if 16 <= i < 30:
                label(c, 'Rova', y + 30, False)
                d.rounded_rectangle([40, y + 58, 150, y + 108], 22, fill=(255, 255, 255))
                for k in range(3):
                    a = 1 if (i // 3) % 3 == k else 0
                    d.ellipse([66 + k * 26 - 7 - a * 2, y + 76 - a * 2, 66 + k * 26 + 7 + a * 2, y + 90 + a * 2],
                              fill=(150, 150, 160) if a else (200, 200, 208))
            if i >= 30:
                label(c, 'Rova', y + 30, False)
                bubble(c, answer, y + 58, False, show_chars=min(len(answer), (i - 30) * 4))
        fr.append(c)
    save(fr, name, 60, hold=25)

# ---------- Format 4: Niemand / Rova ----------
def fmt_niemand(name, l1, l2, punch):
    fr = []
    for i in range(42):
        c = canvas(); d = ImageDraw.Draw(c)
        d.text((50, 50), l1, font=F(40), fill=INK)
        if i >= 8: d.text((50, 110), l2, font=F(40), fill=INK)
        if i >= 16:
            text_block(c, punch, 180, 40, align='left', x=50, maxw=W - 100)
            u = min(1, (i - 16) / 10)
            if u < 1: lift = 400 * (1 - u * u)
            else: lift = abs(math.sin((i - 26) / 16 * math.pi * 2)) * 40 * math.exp(-(i - 26) / 6)
            place(c, .65, W / 2, 640 - lift, lift=lift)
        fr.append(c)
    save(fr, name, 70, hold=25)

# ---------- Format 5: Nein / Ja ----------
def fmt_neinja(name, nein, ja):
    fr = []
    for i in range(40):
        c = canvas(); d = ImageDraw.Draw(c)
        d.rectangle([0, 0, W, W / 2], fill=(250, 238, 238)); d.rectangle([0, W / 2, W, W], fill=(236, 248, 240))
        # obere Box schüttelt "nein", untere nickt "ja"
        place(c, .38, 150 + 8 * math.sin(i * 1.4), 290, rot=0, with_shadow=False)
        nod = 10 * abs(math.sin(i * .5))
        place(c, .38, 150, 650 + nod * 0 - nod, with_shadow=False)
        d.text((W - 60, 60), '✗', font=F(60), fill=RED, anchor='ra')
        d.text((W - 60, W / 2 + 60), '✓', font=F(60), fill=GREEN, anchor='ra')
        text_block(c, nein, W / 4 + 20, 34, maxw=360, x=480, anchor_y='middle', color=(120, 40, 40))
        text_block(c, ja, 3 * W / 4 + 20, 34, maxw=360, x=480, anchor_y='middle', color=(20, 100, 55))
        fr.append(c)
    save(fr, name, 70)

# ---------- Format 6: POV mit langsamem Zoom ----------
def fmt_pov(name, text):
    fr = []
    for i in range(45):
        c = canvas(); z = .62 + .22 * (i / 44) ** 1.3
        place(c, z, W / 2, 600 + 40 * (i / 44))
        g = Image.new('RGBA', (W, 230), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        for y in range(230): gd.line([0, y, W, y], fill=BG + (int(255 * (1 - y / 230) ** .6),))
        c.paste(g, (0, 0), g)
        text_block(c, text, 50, 40)
        fr.append(c)
    save(fr, name, 60, hold=20)

# ---------- Format 7: Schreibmaschine + Antwort ----------
def fmt_type(name, prompt, reply):
    fr = []; n = len(prompt)
    for i in range(n // 2 + 40):
        c = canvas(); d = ImageDraw.Draw(c)
        k = min(n, i * 2)
        txt = '„' + prompt[:k] + ('“' if k >= n else '|')
        text_block(c, txt, 60, 40)
        j = i - n // 2 - 3
        if j >= 0:
            s = .7 * max(.05, ease_out_back(min(1, j / 10)))
            place(c, s, W / 2, 560)
            if j > 12: text_block(c, 'Rova: ' + reply, 640, 36, color=GREEN)
        fr.append(c)
    save(fr, name, 50, hold=25)

# ---------- Format 8: Aufgabenliste hakt sich ab ----------
def fmt_liste(name, title, items, punch):
    fr = []; step = 9
    for i in range(len(items) * step + 30):
        c = canvas(); d = ImageDraw.Draw(c)
        d.text((W / 2, 50), title, font=F(40), fill=INK, anchor='ma')
        place(c, .4, 170, 560 - 8 * abs(math.sin(i * .35)))
        for k, it in enumerate(items):
            y = 150 + k * 70; vis = i >= k * step
            if not vis: continue
            done = i >= k * step + 5
            d.rounded_rectangle([340, y, 380, y + 40], 8, outline=GREEN if done else (190, 190, 198), width=3,
                                fill=GREEN if done else None)
            if done: d.text((360, y + 20), '✓', font=F(28), fill=(255, 255, 255), anchor='mm')
            fs = 26
            while d.textlength(it, font=F(fs, False)) > 320: fs -= 1
            d.text((395, y + 20), it, font=F(fs, False), fill=INK if done else GREY, anchor='lm')
        if i >= len(items) * step + 6: text_block(c, punch, 650, 34, anchor_y='bottom')
        fr.append(c)
    save(fr, name, 60, hold=25)

# ================== DIE SERIE (hier Sprüche anpassen) ==================
SERIE = [
    (fmt_caption, '01_umsatz', 'Ich: „Wer hat mal eben die Umsatzzahlen?“', 'Rova: „Hier. Schon aufbereitet.“', 'drop'),
    (fmt_caption, '02_wochenbericht', 'Montag, 8:00 Uhr.', 'Rova hat den Wochenbericht schon fertig.', 'shake'),
    (fmt_caption, '03_datenhaus', 'Wenn die Firmendaten das Haus nicht verlassen dürfen', 'Rova: „Hatte ich auch nicht vor.“', 'pop'),
    (fmt_caption, '04_keine_cloud', 'Keine Cloud. Kein Drittland.', 'Rova wohnt bei dir im Büro.', 'float'),
    (fmt_split, '05_ohne_mit', 'Ohne Rova', ['CRM?', 'ERP?', 'Mail von wem?', 'Bericht_v7_final', 'Wer weiß das?', 'Excel??'],
     'Mit Rova', 'Eine Frage. Eine Antwort.'),
    (fmt_chat, '06_chat_angebote', 'Chefin', 'Welche Angebote sind noch offen?', 'Hier ist die Liste. Soll Nova bei den Kunden nachfassen?'),
    (fmt_chat, '07_chat_rechte', 'Praktikant', 'Zeig mir mal die Gehaltsliste.', 'Dafür hast du keine Berechtigung. Netter Versuch.'),
    (fmt_chat, '08_chat_kampagne', 'Chef', 'Ich will eine Kampagne für unser Herbstangebot.', 'Passende Kunden aus dem CRM gefiltert. Nova ruft sie an.'),
    (fmt_niemand, '09_niemand', 'Niemand:', 'Absolut niemand:', 'Rova um 7:59: „Dein Tagesüberblick ist fertig.“'),
    (fmt_neinja, '10_nein_ja_systeme', 'Zahlen aus fünf Systemen zusammensuchen', 'Rova einfach fragen'),
    (fmt_neinja, '11_nein_ja_cloud', 'Firmendaten in irgendeinen Cloud-Chatbot kopieren', 'Rova: alles bleibt im Haus'),
    (fmt_pov, '12_pov_umsatz', 'POV: Du fragst nach dem Umsatz und musst nicht bis Freitag warten.'),
    (fmt_type, '13_kampagne_tippen', 'Ich will eine Kampagne starten.', '„Bin schon dabei.“'),
    (fmt_liste, '14_liste_9uhr', 'Rova, 9:00 Uhr', ['Mails sortiert', 'Bericht erstellt', 'Meeting zusammengefasst', 'Kampagne vorbereitet', 'Termine eingetragen'],
     'Und du? Erst mal Kaffee.'),
]

if __name__ == '__main__':
    for fn, *args in SERIE:
        fn(*args)
