"""2026-11-29 8 PM owner reel: 'Aaj Sunday... kitni baar suna?' -> question counter 99+ -> kaanchi ya jawab -> phone answers -> wall QR -> live count on customer phone -> DM JOIN kisi bhi shehar se.
Reuses helpers from r2026-11-26-1600.py and r2026-11-28-2000.py (music, captions, phone, logo...).
Usage: python3 r2026-11-29-2000.py frames OUTDIR [timing.json] | python3 r2026-11-29-2000.py render out.mp4 [timing.json]
"""
import sys, json, math, subprocess, importlib.util, os
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lib', f'{HERE}/r2026-11-26-1600.py'); L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
spec2 = importlib.util.spec_from_file_location('lib2', f'{HERE}/r2026-11-28-2000.py'); L2 = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(L2)
W, H, FPS, Y, INK, WH, GREY, F = L.W, L.H, L.FPS, L.Y, L.INK, L.WH, L.GREY, L.F
ease, pop, ctext, logo, phone, bubble, person, captions = L.ease, L.pop, L.ctext, L.logo, L.phone, L.bubble, L.person, L.captions
stripes, yellow = L2.stripes, L2.yellow
RED = (226, 64, 64); GREEN = (40, 160, 80)

LINES = [
    "Aaj Sunday...|kitni baar suna?",
    "\"Kitne log|aage hain?\"|Kaanchi chalao|ya jawab do?",
    "Ab jawab|phone dega.",
    "Wall pe ek QR...|customer scan kare,|token le.",
    "Apne phone pe|live dekhe...|aage kitne log.",
    "Salon owner ho?|DM karo JOIN...|kisi bhi|shehar se!",
]
DEFAULT_T = [[0.0, 2.3], [2.3, 5.8], [5.8, 7.8], [7.8, 10.6], [10.6, 13.2], [13.2, 17.8]]

def groups(T):
    out = []
    for li, (line, (a, b)) in enumerate(zip(LINES, T)):
        gs = line.split('|'); tot = sum(len(g) + 3 for g in gs); t = a
        for g in gs:
            dt = (b - a) * (len(g) + 3) / tot; out.append((t, t + dt, g, li)); t += dt
    return out

def clicker(img, n, cx, cy, s, col=INK, shake=0):
    """hand tally counter showing n"""
    def fn(d, Lr):
        d.rounded_rectangle((40, 120, 720, 560), 90, fill=WH, outline=Y, width=14)
        d.rounded_rectangle((300, 20, 460, 140), 30, fill=Y, outline=INK, width=8)  # button
        d.rounded_rectangle((110, 210, 650, 470), 40, fill=INK)
        txt = f"{n}" if n < 100 else "99+"
        f = F(220); b = d.textbbox((0, 0), txt, font=f)
        d.text((380 - (b[2] + b[0]) / 2, 340 - (b[3] + b[1]) / 2), txt, font=f, fill=col)
        d.ellipse((330, 560, 430, 660), outline=WH, width=16)  # ring
    r = L.scaled_layer(fn, s, cx, cy, (760, 680))
    if r:
        lay, pos = r
        if shake: lay = lay.rotate(shake, resample=Image.BICUBIC)
        img.alpha_composite(lay, pos)

def scissors(d, cx, cy, s, ang):
    for sgn in (-1, 1):
        a = math.radians(ang * sgn)
        ex, ey = cx + math.sin(a) * 260 * s, cy - math.cos(a) * 260 * s
        bx, by = cx - math.sin(a) * 120 * s, cy + math.cos(a) * 120 * s
        d.line([(bx, by), (ex, ey)], fill=WH, width=int(26 * s))
        hx, hy = cx - math.sin(-a) * 190 * s, cy + math.cos(-a) * 190 * s
        d.ellipse((hx - 55 * s, hy - 55 * s, hx + 55 * s, hy + 55 * s), outline=Y, width=int(20 * s))
    d.ellipse((cx - 18 * s, cy - 18 * s, cx + 18 * s, cy + 18 * s), fill=Y)

QS = [("Kitne log aage hain?", 300, 260), ("Bhaiya, kitna time?", 770, 330), ("Mera number kab?", 300, 1270), ("Kitne log??", 800, 1200)]

def frame(t, T, G):
    img = Image.new('RGBA', (W, H), INK + (255,)); d = ImageDraw.Draw(img)
    s1, s2, s3, s4, s5, s6 = [a for a, b in T]
    if t < s2:  # HOOK: counter ticking from frame 1
        stripes(d)
        n = int(37 + t / max(.1, s2) * 40)
        ctext(d, "AAJ SUNDAY", W / 2, 230, F(110), Y, 6)
        ctext(d, "kitni baar suna?", W / 2, 350, F(62), WH)
        click = (t * 6) % 1 < 0.3
        clicker(img, n, W / 2, 790, 1.12 * (0.97 if click else 1.0), INK if False else Y, 2 * math.sin(t * 9))
        bubble(img, "\"Kitne log aage hain?\"", W / 2, 1250, pop(0.5 + t / 0.25), dark=False, fs=54)
    elif t < s3:  # PROBLEM: 99+ red, bubbles flood, kaanchi vs jawab
        stripes(d); k = t - s2; dur = s3 - s2
        if k < dur * 0.45:
            clicker(img, 100, W / 2, 760, pop(k / 0.25) * 1.05, RED, 3 * math.sin(k * 20))
            for i, (q, x, y) in enumerate(QS):
                st = 0.1 + i * 0.18
                if k > st: bubble(img, q, x, y, pop((k - st) / 0.25) * 0.85, dark=(i % 2 == 1), fs=50)
        else:
            kk = k - dur * 0.45
            ctext(d, "KAANCHI", 290, 330, F(84), Y, 4)
            ctext(d, "ya", W / 2, 330, F(60, False), WH)
            ctext(d, "JAWAB?", 800, 330, F(84), Y, 4)
            scissors(d, 290, 800, 0.95 * pop(kk / 0.3), 14 + 10 * math.sin(kk * 14))
            bubble(img, "Kitne log?", 800, 640, pop((kk - 0.1) / 0.25), dark=False, fs=52)
            bubble(img, "Kitna time?", 800, 850, pop((kk - 0.3) / 0.25), dark=True, fs=52)
            bubble(img, "Mera kab?", 800, 1060, pop((kk - 0.5) / 0.25), dark=False, fs=52)
            if kk > 0.6:
                ctext(d, "THAK GAYE?", W / 2, 1300, F(int(100 * min(1, pop((kk - 0.6) / 0.3)))), RED, 6, WH)
    elif t < s6:  # SOLUTION on yellow
        d = yellow(img)
        logo(img, 'i', 170, 140, 250)
        if t < s4:  # phone answers
            k = t - s3
            ctext(d, "Jawab phone dega", W / 2 + 70, 250, F(70), INK)
            def content(dd, Lr, pw, ph):
                b = dd.textbbox((0, 0), "Salon Queue", font=F(44)); dd.text((pw / 2 - b[2] / 2, 130), "Salon Queue", font=F(44), fill=INK)
                dd.ellipse((70, 230, 96, 256), fill=(230, 50, 50)); dd.text((108, 220), "LIVE", font=F(38), fill=(230, 50, 50))
                b = dd.textbbox((0, 0), "aage", font=F(56)); dd.text((pw / 2 - b[2] / 2, 300), "aage", font=F(56), fill=GREY)
                f = F(260); b = dd.textbbox((0, 0), "4", font=f); dd.text((pw / 2 - (b[2] + b[0]) / 2, 510 - (b[3] + b[1]) / 2), "4", font=f, fill=INK)
                b = dd.textbbox((0, 0), "log", font=F(56)); dd.text((pw / 2 - b[2] / 2, 650), "log", font=F(56), fill=GREY)
            phone(img, W / 2, 880, 0.8 + 0.2 * pop(k / 0.35), content)
            if k > 0.6:
                clicker(img, 0, 870, 1250, 0.38 * pop((k - 0.6) / 0.3), GREEN)
        elif t < s5:  # wall QR -> scan -> token
            k = t - s4; dur = s5 - s4
            ctext(d, "Wall pe 1 QR", W / 2 + 70, 250, F(76), INK)
            ps = max(0.05, pop(k / 0.3))
            px0, py0 = W / 2 - 300 * ps, 820 - 380 * ps
            d.rounded_rectangle((px0, py0, W / 2 + 300 * ps, 820 + 380 * ps), int(40 * ps) + 1, fill=WH, outline=INK, width=10)
            if ps > 0.9:
                ctext(d, "Token lo, scan karo", W / 2, py0 + 80, F(44), INK)
                L.draw_qr(d, W / 2 - 200, 600, 400)
                logo(img, 'i', 120, W / 2, 1110)
                if k > 0.8:  # scan line
                    yy = 600 + ((k - 0.8) * 500) % 400
                    d.rectangle((W / 2 - 230, yy, W / 2 + 230, yy + 10), fill=(230, 50, 50))
            if k > dur * 0.62:
                bubble(img, "Token #23 mil gaya!", W / 2, 1300, pop((k - dur * 0.62) / 0.3), dark=True, fs=54)
        else:  # customer phone live counter dropping
            k = t - s5; dur = s6 - s5
            ctext(d, "Customer ke phone pe", W / 2 + 70, 250, F(58), INK)
            n = max(1, 4 - int(k / (dur / 3.2)))
            L2.draw_counter.__globals__  # noqa
            def content(dd, Lr, pw, ph):
                dd.ellipse((70, 140, 96, 166), fill=(230, 50, 50)); dd.text((108, 130), "LIVE", font=F(38), fill=(230, 50, 50))
                b = dd.textbbox((0, 0), "Token #23", font=F(40)); dd.text((pw - 70 - b[2], 130), "Token #23", font=F(40), fill=INK)
                b = dd.textbbox((0, 0), "aage", font=F(56)); dd.text((pw / 2 - b[2] / 2, 250), "aage", font=F(56), fill=GREY)
                sc = pop(((k / (dur / 3.2)) % 1) / 0.25)
                f = F(max(10, int(300 * sc))); b = dd.textbbox((0, 0), str(n), font=f)
                dd.text((pw / 2 - (b[2] + b[0]) / 2, 470 - (b[3] + b[1]) / 2), str(n), font=f, fill=INK if n > 1 else GREEN)
                b = dd.textbbox((0, 0), "log", font=F(56)); dd.text((pw / 2 - b[2] / 2, 620), "log", font=F(56), fill=GREY)
                for i in range(4):
                    cx_ = pw / 2 - 120 + i * 80; dd.ellipse((cx_ - 26, 740, cx_ + 26, 792), fill=Y if i < n else (225, 228, 235))
            phone(img, W / 2, 870, 1.0, content)
            if k > dur * 0.4:
                bubble(img, "Bench pe bheed nahi", W / 2, 1300, pop((k - dur * 0.4) / 0.3), dark=True, fs=52)
    else:  # CTA
        k = t - s6
        stripes(d)
        logo(img, 'y', max(1, int(340 * pop(k / 0.4))), W / 2, 390)
        ctext(d, "Salon owner ho?", W / 2, 640, F(76), WH)
        if k > 0.4:
            ps = pop((k - .4) / .35); bw, bh = 820 * ps, 190 * ps
            d.rounded_rectangle((W / 2 - bw / 2, 830 - bh / 2, W / 2 + bw / 2, 830 + bh / 2), int(60 * ps) + 1, fill=Y)
            ctext(d, "DM \"JOIN\"", W / 2, 830, F(max(10, int(100 * ps))), INK)
        if k > 1.5:
            ctext(d, "Kisi bhi shehar se", W / 2, 1030, F(int(66 * min(1, pop((k - 1.5) / .3)))), Y)
        if k > 2.2:
            ctext(d, "@salonqueueapp", W / 2, 1140, F(48, False), WH)
    captions(img, t, G)
    return img.convert('RGB')

if __name__ == '__main__':
    T = DEFAULT_T; VO = None; GT = None
    if len(sys.argv) > 3:
        cfg = json.load(open(sys.argv[3])); T = cfg['T']; GT = cfg.get('G'); VO = cfg.get('vo')
    G = groups(T); DUR = T[-1][1] + 1.0
    if GT:
        assert len(GT) == len(G), (len(GT), len(G))
        G = [(a, b, g[2], g[3]) for (a, b), g in zip(GT, G)]
    if sys.argv[1] == 'frames':
        for tt in [0.0, 1.5, 3.0, 4.8, 6.6, 8.2, 9.8, 11.5, 12.9, 14.2, 17.5]:
            frame(tt, T, G).save(f'{sys.argv[2]}/f_{tt:05.2f}.png')
    else:
        out = sys.argv[2]; sp = os.path.dirname(os.path.abspath(out))
        L.music(DUR, f'{sp}/music.wav')
        tmp = f'{sp}/video_tmp.mp4'
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
        for i in range(int(DUR * FPS)):
            p.stdin.write(frame(i / FPS, T, G).tobytes())
        p.stdin.close(); assert p.wait() == 0
        if VO:
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-i', VO, '-i', f'{sp}/music.wav',
                            '-filter_complex', '[2:a]volume=0.13,aresample=48000[m];[1:a]aresample=48000,apad[v];[v][m]amix=inputs=2:duration=shortest:normalize=0[a]',
                            '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', str(DUR), '-movflags', '+faststart', out], check=True)
            print('done vo', DUR); sys.exit()
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-i', f'{sp}/music.wav', '-map', '0:v', '-map', '1:a',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-filter:a', 'volume=0.6', '-shortest', '-movflags', '+faststart', out], check=True)
        print('done', DUR)
