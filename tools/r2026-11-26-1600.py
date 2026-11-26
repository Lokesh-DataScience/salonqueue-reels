"""2026-11-26 4 PM owner reel: 'shaam ka rush' speech-bubble flood -> QR -> live counter -> DM JOIN.
Usage: python3 r1600.py frames  (writes stills)   |  python3 r1600.py render out.mp4 [timing.json]
timing.json: list of 6 [start,end] for VO lines; total length = last end + 1.0
"""
import sys, json, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import qrcode

W, H, FPS = 1080, 1920, 30
Y = (249, 200, 14); INK = (27, 31, 42); WH = (255, 255, 255); GREY = (120, 126, 140)
FB = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
FM = '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf'
REPO = '/home/claude/salonqueue-reels'
_fc = {}
def F(s, b=True):
    s = max(10, int(s)); k = (s, b)
    if k not in _fc: _fc[k] = ImageFont.truetype(FB if b else FM, s)
    return _fc[k]

LOGO_Y = Image.open(f'{REPO}/assets/logo_yellow.png').convert('RGBA')
LOGO_I = Image.open(f'{REPO}/assets/logo_ink.png').convert('RGBA')
_lc = {}
def logo(img, which, size, cx, cy):
    k = (which, size)
    if k not in _lc: _lc[k] = (LOGO_Y if which == 'y' else LOGO_I).resize((size, size), Image.LANCZOS)
    img.alpha_composite(_lc[k], (int(cx - size / 2), int(cy - size / 2)))

qr = qrcode.QRCode(border=0, box_size=1); qr.add_data('https://salonqueue.onrender.com/c'); qr.make()
QRM = np.array(qr.get_matrix(), dtype=bool)

LINES = [
    "Barber bhai...|shaam ka rush|aa raha hai!",
    "Aur phir|wahi sawaal...|kitne log|aage hain?",
    "Bas ek QR code,|wall pe lagao.",
    "Customer|scan kare,|token le...",
    "aur phone pe|live dekhe,|aage kitne log.",
    "Salon owner ho?|DM karo JOIN.|Kisi bhi|shehar se.",
]
DEFAULT_T = [[0.0, 2.5], [2.5, 5.5], [5.5, 8.0], [8.0, 10.5], [10.5, 13.0], [13.0, 17.0]]

def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def pop(x):  # overshoot 0..1
    x = max(0, min(1, x)); return 1 + 2.7 * (x - 1) ** 3 + 1.7 * (x - 1) ** 2 if x < 1 else 1

def ctext(d, txt, cx, cy, font, fill, stroke=0, sfill=INK):
    bb = d.textbbox((0, 0), txt, font=font, stroke_width=stroke)
    d.text((cx - (bb[2] + bb[0]) / 2, cy - (bb[3] + bb[1]) / 2), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill)

def scaled_layer(draw_fn, s, cx, cy, box):
    """draw on a small RGBA layer and paste scaled by s centred at cx,cy"""
    bw, bh = box
    L = Image.new('RGBA', (bw, bh), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(L), L)
    if s <= 0.01: return None
    L = L.resize((max(1, int(bw * s)), max(1, int(bh * s))), Image.BILINEAR)
    return L, (int(cx - L.width / 2), int(cy - L.height / 2))

def bubble(img, txt, cx, cy, s, dark=False, fs=50):
    def fn(d, L):
        f = F(fs); bb = d.textbbox((0, 0), txt, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        x0, y0 = (L.width - tw) / 2 - 34, (L.height - th) / 2 - 30
        x1, y1 = x0 + tw + 68, y0 + th + 52
        fill = INK if dark else WH; tf = WH if dark else INK
        d.rounded_rectangle((x0, y0, x1, y1), 34, fill=fill, outline=Y, width=5)
        d.polygon([(x0 + 50, y1 - 2), (x0 + 95, y1 - 2), (x0 + 40, y1 + 40)], fill=fill)
        d.line([(x0 + 50, y1), (x0 + 40, y1 + 40), (x0 + 95, y1)], fill=Y, width=5)
        d.text(((L.width - tw) / 2 - bb[0], y0 + 26 - bb[1]), txt, font=f, fill=tf)
    r = scaled_layer(fn, s, cx, cy, (760, 220))
    if r: img.alpha_composite(*r)

def clock(d, cx, cy, r, t):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WH, outline=Y, width=12)
    for i in range(12):
        a = i / 12 * 2 * math.pi
        d.line([(cx + math.sin(a) * r * .78, cy - math.cos(a) * r * .78), (cx + math.sin(a) * r * .9, cy - math.cos(a) * r * .9)], fill=INK, width=6)
    # hour hand to 6, minute hand spinning to 12
    ma = (t * 2.2) % 1 * 2 * math.pi
    d.line([(cx, cy), (cx, cy + r * .5)], fill=INK, width=16)
    d.line([(cx, cy), (cx + math.sin(ma) * r * .72, cy - math.cos(ma) * r * .72)], fill=(220, 60, 60), width=9)
    d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=INK)

def person(d, cx, cy, s, col):
    d.ellipse((cx - 26 * s, cy - 92 * s, cx + 26 * s, cy - 40 * s), fill=col)
    d.rounded_rectangle((cx - 40 * s, cy - 34 * s, cx + 40 * s, cy + 40 * s), int(22 * s), fill=col)

def phone(img, cx, cy, s, content):
    pw, ph = 470, 900
    def fn(d, L):
        d.rounded_rectangle((10, 10, pw + 10, ph + 10), 64, fill=INK)
        d.rounded_rectangle((28, 28, pw - 8, ph - 8), 50, fill=WH)
        d.rounded_rectangle((pw / 2 - 50, 44, pw / 2 + 70, 66), 11, fill=INK)
        content(d, L, pw + 20, ph + 20)
    r = scaled_layer(fn, s, cx, cy, (pw + 20, ph + 20))
    if r: img.alpha_composite(*r)

def draw_qr(d, x, y, size, fg=INK):
    n = QRM.shape[0]; c = size / n
    for i in range(n):
        for j in range(n):
            if QRM[i, j]: d.rectangle((x + j * c, y + i * c, x + (j + 1) * c - 0.5, y + (i + 1) * c - 0.5), fill=fg)

# ---------------- captions ----------------
def groups(T):
    out = []
    for li, (line, (a, b)) in enumerate(zip(LINES, T)):
        gs = line.split('|')
        tot = sum(len(g) + 3 for g in gs); t = a
        for g in gs:
            dt = (b - a) * (len(g) + 3) / tot; out.append((t, t + dt, g, li)); t += dt
    return out

def captions(img, t, G):
    cur = [g for g in G if g[0] <= t < g[1]]
    if not cur: return
    st, en, txt, li = cur[0]
    sib = [g for g in G if g[3] == li]
    idx = sib.index(cur[0])
    # show current group big, with previous group of same line small above? keep simple: one group, karaoke words
    d = ImageDraw.Draw(img)
    f = F(92); words = txt.upper().split()
    sp = 26; widths = [d.textlength(w, font=f) for w in words]
    total = sum(widths) + sp * (len(words) - 1)
    if total > W - 120:
        f = F(int(92 * (W - 120) / total)); widths = [d.textlength(w, font=f) for w in words]; total = sum(widths) + sp * (len(words) - 1)
    k = (t - st) / max(.01, en - st); s = 0.85 + 0.15 * ease(k * 4)
    cy = 1500
    x = W / 2 - total / 2
    # word-level karaoke highlight
    nw = len(words); hi = min(nw - 1, int(k * nw))
    # backing plate
    d.rounded_rectangle((W / 2 - total / 2 - 40, cy - 80, W / 2 + total / 2 + 40, cy + 80), 36, fill=(27, 31, 42, 225))
    for i, w in enumerate(words):
        col = Y if i == hi else WH
        d.text((x, cy), w, font=f, fill=col, anchor='lm', stroke_width=4, stroke_fill=INK)
        x += widths[i] + sp

# ---------------- scenes ----------------
BUBS = [("Kitne log aage?", 300, 660, 0.0), ("Mera number kab?", 770, 800, 0.0), ("Bhaiya, kitna time?", 320, 940, 0.0),
        ("Kitne log aage?", 780, 1080, 2.6), ("Aur kitni der?", 290, 1220, 3.0), ("Mera kab aayega?", 780, 640, 3.3),
        ("Kitne log aage hain??", 540, 1340, 3.7), ("Bas 5 minute?", 300, 1080, 4.1), ("Kitne log??", 800, 1220, 4.4)]

def frame(t, T):
    img = Image.new('RGBA', (W, H), INK + (255,)); d = ImageDraw.Draw(img)
    s1, s2, s3, s4, s5, s6 = [a for a, b in T]
    end = T[-1][1] + 1.0
    if t < s3:  # HOOK + PROBLEM, dark
        # subtle stripes
        for i in range(0, W, 120): d.rectangle((i, 0, i + 60, H), fill=(31, 35, 47))
        # clock top
        cs = pop(0.6 + t / 0.35) if t < s2 else 1
        clock(d, W / 2, 300, int(110 * cs), t)
        ctext(d, "6:00 PM", W / 2, 470, F(64), Y)
        if t < s2:
            ctext(d, "SHAAM KA RUSH", W / 2, 1270, F(108 * min(1, pop(0.6 + t / 0.3))), Y, 6)
            # bench people row
            for i in range(6):
                person(d, 140 + i * 160, 1150, 1.0, WH if i % 2 else (200, 205, 215))
        else:
            # flood of bubbles (problem)
            pass
        for txt, bx, by, bt in BUBS:
            at = bt if t < s2 else bt
            if t >= at and (bt < 1 or t >= s2):
                s = pop((0.6 if at == 0 else 0) + (t - at) / 0.3) * (1 + 0.03 * math.sin(t * 6 + bx))
                bubble(img, txt, bx, by, s, dark=False, fs=50 if t < s2 else 46)
        if t >= s2:
            # tally counter top right
            n = 47 + int((t - s2) * 9)
            ctext(d, f"x{n}", 900, 330, F(86), (240, 80, 80), 5)
            ctext(d, "roz ka sawaal", 900, 410, F(36, False), WH)
    elif t < s6:  # SOLUTION, yellow
        img.paste(Y + (255,), (0, 0, W, H)); d = ImageDraw.Draw(img)
        for i in range(-H, W, 140): d.line([(i, 0), (i + H, H)], fill=(240, 190, 10), width=40)
        logo(img, 'i', 170, 140, 250)
        if t < s4:  # QR on wall
            k = (t - s3)
            ctext(d, "1 QR. Wall pe.", W / 2 + 70, 250, F(76), INK)
            # wall poster
            ps = pop(k / 0.35)
            def fn(dd, L):
                dd.rounded_rectangle((10, 10, 610, 790), 40, fill=WH, outline=INK, width=10)
                dd.rectangle((10, 10, 610, 150), fill=INK);
                b = dd.textbbox((0, 0), "TOKEN LO", font=F(64)); dd.text((310 - (b[2] + b[0]) / 2, 80 - (b[3] + b[1]) / 2), "TOKEN LO", font=F(64), fill=Y)
                draw_qr(dd, 110, 200, 400)
                b = dd.textbbox((0, 0), "Scan karo", font=F(50)); dd.text((310 - (b[2] + b[0]) / 2, 680), "Scan karo", font=F(50), fill=INK)
            r = scaled_layer(fn, ps, W / 2, 800, (620, 800))
            if r: img.alpha_composite(*r)
            # tape
            if ps > .9:
                d.polygon([(W / 2 - 80, 380), (W / 2 + 80, 380), (W / 2 + 70, 430), (W / 2 - 90, 430)], fill=(250, 235, 160))
        elif t < s5:  # phone scanning -> token
            k = t - s4
            ctext(d, "Scan. Token mila.", W / 2 + 70, 250, F(72), INK)
            def content(dd, L, pw, ph):
                if k < 0.9:
                    draw_qr(dd, 95, 250, 300)
                    yy = 250 + (k / 0.9) * 300
                    dd.rectangle((80, yy - 4, pw - 80, yy + 4), fill=(240, 80, 80))
                    b = dd.textbbox((0, 0), "Scanning...", font=F(40)); dd.text((pw / 2 - b[2] / 2, 620), "Scanning...", font=F(40), fill=GREY)
                else:
                    sc = pop((k - 0.9) / 0.3)
                    b = dd.textbbox((0, 0), "Aapka token", font=F(40)); dd.text((pw / 2 - b[2] / 2, 170), "Aapka token", font=F(40), fill=GREY)
                    dd.rounded_rectangle((70, 250, pw - 70, 560), 40, fill=Y)
                    fs = max(10, int(170 * sc)); f = F(fs); b = dd.textbbox((0, 0), "#12", font=f)
                    dd.text((pw / 2 - (b[2] + b[0]) / 2, 405 - (b[3] + b[1]) / 2), "#12", font=f, fill=INK)
                    b = dd.textbbox((0, 0), "Ghar jao, aaram karo", font=F(34, False)); dd.text((pw / 2 - b[2] / 2, 620), "Ghar jao, aaram karo", font=F(34, False), fill=INK)
            phone(img, W / 2, 880, ease(k / 0.3) * 0.2 + 0.8, content)
        else:  # live counter dropping
            k = t - s5; dur = s6 - s5
            ctext(d, "LIVE: aage kitne log", W / 2 + 70, 250, F(62), INK)
            n = max(1, 3 - int(k / (dur / 3)))
            def content(dd, L, pw, ph):
                dd.ellipse((70, 140, 96, 166), fill=(230, 50, 50)); dd.text((108, 130), "LIVE", font=F(38), fill=(230, 50, 50))
                b = dd.textbbox((0, 0), "Token #12", font=F(40)); dd.text((pw - 70 - b[2], 130), "Token #12", font=F(40), fill=INK)
                b = dd.textbbox((0, 0), "aage", font=F(56)); dd.text((pw / 2 - b[2] / 2, 250), "aage", font=F(56), fill=GREY)
                ph_ = (k / (dur / 3)) % 1; sc = pop(ph_ / 0.25)
                f = F(max(10, int(300 * sc))); b = dd.textbbox((0, 0), str(n), font=f)
                dd.text((pw / 2 - (b[2] + b[0]) / 2, 470 - (b[3] + b[1]) / 2), str(n), font=f, fill=INK)
                b = dd.textbbox((0, 0), "log", font=F(56)); dd.text((pw / 2 - b[2] / 2, 620), "log", font=F(56), fill=GREY)
                for i in range(3):
                    col = Y if i < n else (225, 228, 235)
                    cx_ = pw / 2 - 110 + i * 110; dd.ellipse((cx_ - 30, 740, cx_ + 30, 800), fill=col)
            phone(img, W / 2, 880, 1.0, content)
            # bench calm: tick badge
            if n == 1:
                bs = pop((k - 2 * dur / 3) / 0.3)
                bubble(img, "Bench khaali, kaam chalu", W / 2, 1180, bs * 0.95, dark=True, fs=44)
    else:  # CTA
        k = t - s6
        for i in range(0, W, 120): d.rectangle((i, 0, i + 60, H), fill=(31, 35, 47))
        logo(img, 'y', int(360 * pop(k / 0.4)) or 1, W / 2, 400)
        ctext(d, "Salon Queue", W / 2, 640, F(70), WH)
        if k > 0.3:
            ctext(d, "Salon owner ho?", W / 2, 790, F(int(84 * min(1, pop((k - .3) / .3)))), WH)
        if k > 0.9:
            ps = pop((k - .9) / .35); bw, bh = 820 * ps, 190 * ps
            d.rounded_rectangle((W / 2 - bw / 2, 1000 - bh / 2, W / 2 + bw / 2, 1000 + bh / 2), int(60 * ps) + 1, fill=Y)
            ctext(d, 'DM "JOIN"', W / 2, 1000, F(max(10, int(110 * ps))), INK)
        if k > 1.8:
            ctext(d, "Kisi bhi shehar se", W / 2, 1180, F(64), Y)
            ctext(d, "@salonqueueapp", W / 2, 1265, F(46, False), WH)
    captions(img, t, G)
    return img.convert('RGB')

def music(dur, path):
    sr = 44100; n = int(sr * dur); tt = np.arange(n) / sr; out = np.zeros(n)
    bpm = 100; beat = 60 / bpm
    chords = [[220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7], [164.8, 207.7, 246.9]]
    for bi in range(int(dur / beat) + 1):
        st = int(bi * beat * sr)
        # kick
        L = int(.25 * sr); e = np.exp(-np.arange(L) / sr * 18); f = 50 + 70 * np.exp(-np.arange(L) / sr * 30)
        k = np.sin(2 * np.pi * np.cumsum(f) / sr) * e * .55
        if bi % 2 == 0: out[st:st + L] += k[:max(0, min(L, n - st))]
        # hat
        hs = int((bi + .5) * beat * sr); L2 = int(.05 * sr)
        h = np.random.randn(L2) * np.exp(-np.arange(L2) / sr * 90) * .12
        out[hs:hs + L2] += h[:max(0, min(L2, n - hs))]
        if bi % 2 == 1:  # snare-ish clap
            L3 = int(.15 * sr); c = np.random.randn(L3) * np.exp(-np.arange(L3) / sr * 25) * .22
            out[st:st + L3] += c[:max(0, min(L3, n - st))]
    bar = beat * 4
    for ci in range(int(dur / bar) + 1):
        ch = chords[ci % 4]; st = int(ci * bar * sr); L = int(bar * sr); seg = np.arange(L) / sr
        env = np.minimum(1, seg * 8) * np.exp(-seg * .6)
        s = sum(np.sin(2 * np.pi * fr * seg) + .3 * np.sin(4 * np.pi * fr * seg) for fr in ch) * env * .08
        s += np.sin(2 * np.pi * ch[0] / 2 * seg) * env * .12
        e2 = min(L, n - st)
        if e2 > 0: out[st:st + e2] += s[:e2]
    fo = int(1.5 * sr); out[-fo:] *= np.linspace(1, 0, fo); out[:int(.05 * sr)] *= np.linspace(0, 1, int(.05 * sr))
    out = out / np.max(np.abs(out)) * 0.5
    import wave
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out * 32767).astype(np.int16).tobytes())

if __name__ == '__main__':
    T = DEFAULT_T
    if len(sys.argv) > 3: T = json.load(open(sys.argv[3]))
    G = groups(T); DUR = T[-1][1] + 1.0
    if sys.argv[1] == 'frames':
        for tt in [0.0, 0.5, 1.5, 4.5, 6.5, 8.3, 9.8, 12.5, 14.0, 16.5]:
            frame(tt, T).save(f'{sys.argv[2]}/f_{tt:05.2f}.png')
    else:
        out = sys.argv[2]; sp = out.rsplit('/', 1)[0]
        music(DUR, f'{sp}/music.wav')
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', f'{sp}/video_tmp.mp4'], stdin=subprocess.PIPE)
        for i in range(int(DUR * FPS)):
            p.stdin.write(frame(i / FPS, T).tobytes())
        p.stdin.close(); assert p.wait() == 0
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{sp}/video_tmp.mp4', '-i', f'{sp}/music.wav', '-map', '0:v', '-map', '1:a',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-filter:a', 'volume=0.6', '-shortest', '-movflags', '+faststart', out], check=True)
        print('done', DUR)
