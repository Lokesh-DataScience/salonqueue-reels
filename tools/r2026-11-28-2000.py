"""2026-11-28 8 PM customer reel: 'Kal Sunday hai' -> bench rush -> token from home -> live count -> seedha kursi -> token link bio.
Reuses helpers from r2026-11-26-1600.py.
Usage: python3 r2026-11-28-2000.py frames OUTDIR [timing.json] | python3 r2026-11-28-2000.py render out.mp4 [timing.json]
timing.json: {"T": 6 [start,end] VO lines, "G": optional per-caption-group [start,end], "vo": voice file}
"""
import sys, json, math, subprocess, importlib.util, os
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lib', f'{HERE}/r2026-11-26-1600.py'); L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
W, H, FPS, Y, INK, WH, GREY, F = L.W, L.H, L.FPS, L.Y, L.INK, L.WH, L.GREY, L.F
ease, pop, ctext, logo, phone, bubble, person, clock, captions = L.ease, L.pop, L.ctext, L.logo, L.phone, L.bubble, L.person, L.clock, L.captions
RED = (226, 64, 64)

LINES = [
    "Kal Sunday hai...|salon jaana hai?",
    "Sunday ka rush|matlab... bench pe|ek ghanta.",
    "Is baar...|book your token|from home.",
    "Phone pe|live dekho...|aage kitne log.",
    "Aage ek bacha?|Tab niklo...|seedha kursi pe!",
    "Token link|bio mein.|Aapka salon|list pe nahi?|Unhe tag karo!",
]
DEFAULT_T = [[0.0, 2.5], [2.5, 5.5], [5.5, 8.0], [8.0, 10.5], [10.5, 13.0], [13.0, 17.5]]

def groups(T):
    out = []
    for li, (line, (a, b)) in enumerate(zip(LINES, T)):
        gs = line.split('|'); tot = sum(len(g) + 3 for g in gs); t = a
        for g in gs:
            dt = (b - a) * (len(g) + 3) / tot; out.append((t, t + dt, g, li)); t += dt
    return out

def stripes(d):
    for i in range(0, W, 120): d.rectangle((i, 0, i + 60, H), fill=(31, 35, 47))

def yellow(img):
    img.paste(Y + (255,), (0, 0, W, H)); d = ImageDraw.Draw(img)
    for i in range(-H, W, 140): d.line([(i, 0), (i + H, H)], fill=(240, 190, 10), width=40)
    return d

def calendar(img, cx, cy, s, flip):
    def fn(d, Lr):
        d.rounded_rectangle((20, 40, 620, 700), 50, fill=WH, outline=Y, width=10)
        d.rounded_rectangle((20, 40, 620, 230), 50, fill=RED); d.rectangle((20, 160, 620, 230), fill=RED)
        for x in (160, 480): d.rounded_rectangle((x - 18, 0, x + 18, 90), 18, fill=INK)
        b = d.textbbox((0, 0), "SUNDAY", font=F(96)); d.text((320 - (b[2] + b[0]) / 2, 140 - (b[3] + b[1]) / 2), "SUNDAY", font=F(96), fill=WH)
        b = d.textbbox((0, 0), "29", font=F(250)); d.text((320 - (b[2] + b[0]) / 2, 440 - (b[3] + b[1]) / 2), "29", font=F(250), fill=INK)
        b = d.textbbox((0, 0), "Salon day", font=F(48, False)); d.text((320 - b[2] / 2, 610), "Salon day", font=F(48, False), fill=GREY)
    r = L.scaled_layer(fn, s, cx, cy, (640, 720))
    if r:
        lay, pos = r
        if flip: lay = lay.rotate(flip, resample=Image.BICUBIC, expand=False)
        img.alpha_composite(lay, pos)

def chair(d, cx, cy, s=1.0, col=INK):
    d.rounded_rectangle((cx - 90 * s, cy - 200 * s, cx + 90 * s, cy - 40 * s), int(30 * s), fill=col)
    d.rounded_rectangle((cx - 120 * s, cy - 50 * s, cx + 120 * s, cy + 10 * s), int(20 * s), fill=col)
    d.rectangle((cx - 14 * s, cy + 10 * s, cx + 14 * s, cy + 110 * s), fill=col)
    d.rounded_rectangle((cx - 100 * s, cy + 100 * s, cx + 100 * s, cy + 130 * s), int(14 * s), fill=col)

def chai(d, cx, cy):
    d.rounded_rectangle((cx - 60, cy - 70, cx + 60, cy + 70), 24, fill=WH, outline=INK, width=8)
    d.arc((cx + 30, cy - 40, cx + 100, cy + 30), -90, 90, fill=INK, width=12)
    for i in (-28, 0, 28):
        d.arc((cx + i - 14, cy - 150, cx + i + 14, cy - 90), 90, 270, fill=WH, width=6)

def frame(t, T, G):
    img = Image.new('RGBA', (W, H), INK + (255,)); d = ImageDraw.Draw(img)
    s1, s2, s3, s4, s5, s6 = [a for a, b in T]
    if t < s2:  # HOOK: calendar already on screen at frame 1
        stripes(d)
        ctext(d, "KAL", W / 2, 260, F(120 * min(1, pop(0.6 + t / 0.3))), Y, 6)
        wob = 4 * math.sin(t * 5)
        calendar(img, W / 2, 790, pop(0.65 + t / 0.3) * (1 + 0.02 * math.sin(t * 7)), wob)
        if t > 0.9:
            bubble(img, "Salon jaana hai?", W / 2, 1270, pop((t - 0.9) / 0.3), dark=False, fs=60)
    elif t < s3:  # PROBLEM: bench filling, clock, +1 ghanta
        stripes(d); k = t - s2; dur = s3 - s2
        clock(d, W / 2, 330, 120, t)
        ctext(d, "SUNDAY RUSH", W / 2, 540, F(100), Y, 6)
        d.rounded_rectangle((60, 1010, W - 60, 1050), 16, fill=(120, 80, 50))
        n = min(8, 3 + int(k / (dur * 0.6) * 5))
        for i in range(8):
            if i < n:
                px = 120 + i * 120; ps = min(1, pop((k - max(0, (i - 3)) * dur * 0.12) / 0.25)) if i >= 3 else 1
                person(d, px, 975, 0.95 * ps, WH if i % 2 else (200, 205, 215))
        ctext(d, f"aage {n} log", W / 2, 1150, F(78), WH)
        if k > dur * 0.45:
            bs = pop((k - dur * 0.45) / 0.3)
            ctext(d, "+1 GHANTA", W / 2, 1300, F(max(10, int(120 * bs))), RED, 6, WH)
    elif t < s6:  # SOLUTION on yellow
        d = yellow(img)
        logo(img, 'i', 170, 140, 250)
        if t < s4:  # book token from home
            k = t - s3
            ctext(d, "Ghar se token", W / 2 + 70, 250, F(76), INK)
            def content(dd, Lr, pw, ph):
                b = dd.textbbox((0, 0), "Salon Queue", font=F(44)); dd.text((pw / 2 - b[2] / 2, 130), "Salon Queue", font=F(44), fill=INK)
                if k < 1.1:
                    press = 0.94 if 0.8 < k < 1.0 else 1.0
                    bw, bh = 330 * press, 130 * press
                    dd.rounded_rectangle((pw / 2 - bw / 2, 420 - bh / 2, pw / 2 + bw / 2, 420 + bh / 2), 40, fill=Y)
                    b = dd.textbbox((0, 0), "TOKEN LO", font=F(56)); dd.text((pw / 2 - (b[2] + b[0]) / 2, 420 - (b[3] + b[1]) / 2), "TOKEN LO", font=F(56), fill=INK)
                    if 0.5 < k < 1.05:  # finger
                        fy = 560 - min(1, (k - 0.5) / 0.3) * 110
                        dd.ellipse((pw / 2 + 40, fy, pw / 2 + 110, fy + 70), fill=(240, 196, 160), outline=INK, width=4)
                else:
                    sc = pop((k - 1.1) / 0.3)
                    b = dd.textbbox((0, 0), "Aapka token", font=F(40)); dd.text((pw / 2 - b[2] / 2, 220), "Aapka token", font=F(40), fill=GREY)
                    dd.rounded_rectangle((70, 290, pw - 70, 590), 40, fill=Y)
                    f = F(max(10, int(170 * sc))); b = dd.textbbox((0, 0), "#14", font=f)
                    dd.text((pw / 2 - (b[2] + b[0]) / 2, 440 - (b[3] + b[1]) / 2), "#14", font=f, fill=INK)
                    b = dd.textbbox((0, 0), "Ghar pe aaram karo", font=F(34, False)); dd.text((pw / 2 - b[2] / 2, 640), "Ghar pe aaram karo", font=F(34, False), fill=INK)
            phone(img, W / 2, 870, ease(k / 0.3) * 0.2 + 0.8, content)
        elif t < s5:  # live counter 5 -> 3, chai
            k = t - s4; dur = s5 - s4
            ctext(d, "LIVE: aage kitne log", W / 2 + 70, 250, F(62), INK)
            n = max(3, 5 - int(k / (dur / 3)))
            draw_counter(img, n, (k / (dur / 3)) % 1, 5)
            chai(d, 900, 1220)
        else:  # 1 left -> go -> chair
            k = t - s5; dur = s6 - s5
            if k < dur * 0.5:
                ctext(d, "Aage sirf 1!", W / 2 + 70, 250, F(72), INK)
                draw_counter(img, 1, k / 0.25 if k < 0.25 else 1, 5)
                bubble(img, "Ab niklo!", 800, 375, pop((k - 0.3) / 0.3), dark=True, fs=60)
            else:
                kk = k - dur * 0.5
                ctext(d, "Seedha kursi pe", W / 2 + 70, 250, F(72), INK)
                chair(d, W / 2, 900, 1.6 * pop(kk / 0.35))
                if kk > 0.3:
                    bubble(img, "Apni baari pe pahuncho", W / 2, 1250, pop((kk - 0.3) / 0.3), dark=True, fs=50)
    else:  # CTA
        k = t - s6
        stripes(d)
        logo(img, 'y', max(1, int(340 * pop(k / 0.4))), W / 2, 390)
        ctext(d, "Salon Queue", W / 2, 620, F(70), WH)
        if k > 0.3:
            ps = pop((k - .3) / .35); bw, bh = 900 * ps, 170 * ps
            d.rounded_rectangle((W / 2 - bw / 2, 790 - bh / 2, W / 2 + bw / 2, 790 + bh / 2), int(60 * ps) + 1, fill=Y)
            ctext(d, "Token link bio mein", W / 2, 790, F(max(10, int(74 * ps))), INK)
        if k > 1.6:
            ctext(d, "Aapka salon list pe nahi?", W / 2, 990, F(int(62 * min(1, pop((k - 1.6) / .3)))), WH)
        if k > 2.4:
            ctext(d, "Unhe tag karo / batao", W / 2, 1090, F(int(62 * min(1, pop((k - 2.4) / .3)))), Y)
            ctext(d, "@salonqueueapp", W / 2, 1185, F(46, False), WH)
    captions(img, t, G)
    return img.convert('RGB')

def draw_counter(img, n, phase, total):
    def content(dd, Lr, pw, ph):
        dd.ellipse((70, 140, 96, 166), fill=(230, 50, 50)); dd.text((108, 130), "LIVE", font=F(38), fill=(230, 50, 50))
        b = dd.textbbox((0, 0), "Token #14", font=F(40)); dd.text((pw - 70 - b[2], 130), "Token #14", font=F(40), fill=INK)
        b = dd.textbbox((0, 0), "aage", font=F(56)); dd.text((pw / 2 - b[2] / 2, 250), "aage", font=F(56), fill=GREY)
        sc = pop(phase / 0.25)
        f = F(max(10, int(300 * sc))); b = dd.textbbox((0, 0), str(n), font=f)
        dd.text((pw / 2 - (b[2] + b[0]) / 2, 470 - (b[3] + b[1]) / 2), str(n), font=f, fill=INK if n > 1 else (40, 160, 80))
        b = dd.textbbox((0, 0), "log", font=F(56)); dd.text((pw / 2 - b[2] / 2, 620), "log", font=F(56), fill=GREY)
        for i in range(total):
            col = Y if i < n else (225, 228, 235)
            cx_ = pw / 2 - 160 + i * 80; dd.ellipse((cx_ - 26, 740, cx_ + 26, 792), fill=col)
    phone(img, W / 2, 870, 1.0, content)

if __name__ == '__main__':
    T = DEFAULT_T; VO = None; GT = None
    if len(sys.argv) > 3:
        cfg = json.load(open(sys.argv[3])); T = cfg['T']; GT = cfg.get('G'); VO = cfg.get('vo')
    G = groups(T); DUR = T[-1][1] + 1.0
    if GT:
        assert len(GT) == len(G), (len(GT), len(G))
        G = [(a, b, g[2], g[3]) for (a, b), g in zip(GT, G)]
    if sys.argv[1] == 'frames':
        for tt in [0.0, 1.2, 3.0, 5.0, 6.0, 7.2, 9.0, 11.0, 12.3, 14.0, 16.5]:
            frame(tt, T, G).save(f'{sys.argv[2]}/f_{tt:05.2f}.png')
    else:
        out = sys.argv[2]; sp = os.path.dirname(os.path.abspath(out))
        L.music(DUR, f'{sp}/music.wav')
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', f'{sp}/video_tmp.mp4'], stdin=subprocess.PIPE)
        for i in range(int(DUR * FPS)):
            p.stdin.write(frame(i / FPS, T, G).tobytes())
        p.stdin.close(); assert p.wait() == 0
        if VO:
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{sp}/video_tmp.mp4', '-i', VO, '-i', f'{sp}/music.wav',
                            '-filter_complex', '[2:a]volume=0.13,aresample=48000[m];[1:a]aresample=48000,apad[v];[v][m]amix=inputs=2:duration=shortest:normalize=0[a]',
                            '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', str(DUR), '-movflags', '+faststart', out], check=True)
            print('done vo', DUR); sys.exit()
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{sp}/video_tmp.mp4', '-i', f'{sp}/music.wav', '-map', '0:v', '-map', '1:a',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-filter:a', 'volume=0.6', '-shortest', '-movflags', '+faststart', out], check=True)
        print('done', DUR)
