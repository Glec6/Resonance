# Contact sheet of Resonance's opening (shell/ps4/launcher/intro.cpp) at a few moments, to check the
# layout on a PC: the same timeline and positions, without the light effects.
#   py scripts/preview-intro.py  ->  art/preview/intro-sheet.png
import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "launcher-assets" / "launcher" / "intro"
W, H = 1920, 1080

lay, src = {}, (1024, 559)
for line in open(D / "layout.txt"):
    if line.startswith("# source"):
        src = tuple(float(v.strip(";")) for v in line.split()[2:4])
    elif not line.startswith("#"):
        n, *v = line.split()
        lay[n] = list(map(float, v))
k = H / src[1]


def screen(x, y):
    return W / 2 + (x - src[0] / 2) * k, y * k


def place(canvas, name, dx=0, dy=0, alpha=1.0, angle=0):
    x, y, w, h = lay[name]
    img = Image.open(D / name).convert("RGBA").resize((round(w * k), round(h * k)), Image.LANCZOS)
    if angle:
        img = img.rotate(-math.degrees(angle), expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        img.putalpha(img.getchannel("A").point(lambda a: int(a * alpha)))
    sx, sy = screen(x + w / 2, y + h / 2)
    canvas.alpha_composite(img, (round(sx + dx - img.width / 2), round(sy + dy - img.height / 2)))


ROLL_START, ROLL_END, CATCH, DROP_START = .30, .95, 1.20, .60
R = H * .15


def catch_point():
    x, y, w, h = lay["console.png"]
    return screen(x + w / 2, y + h / 2)


def ball_pos(t):
    p = min(1, max(0, (t - ROLL_START) / (ROLL_END - ROLL_START)))
    floor_y = H * .965 - R
    tx, ty = catch_point()
    x = -R * 1.5 + (tx + R * 1.5) * (1 - (1 - p) ** 2.4)
    if t <= ROLL_END:
        return x, floor_y
    q = min(1, (t - ROLL_END) / (CATCH - ROLL_END))
    return tx, floor_y + (ty - floor_y) * (1 - (1 - q) ** 2)


FUR = None


def ball(canvas, c, angle):
    global FUR
    if FUR is None:
        x, y, w, h = lay["sonic.png"]
        im = Image.open(D / "sonic.png").convert("RGBA")
        sx, sy = im.width / w, im.height / h
        FUR = im.crop((round((505 - 38 - x) * sx), round((105 - 38 - y) * sy), round((505 + 38 - x) * sx), round((105 + 38 - y) * sy)))
    disc = FUR.rotate(math.degrees(angle)).resize((round(2 * R), round(2 * R)))
    mask = Image.new("L", disc.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, disc.width - 1, disc.height - 1), fill=255)
    disc.putalpha(mask)
    d = ImageDraw.Draw(disc)
    d.ellipse((2, 2, disc.width - 3, disc.height - 3), outline=(10, 20, 70, 220), width=round(R * .07))
    canvas.alpha_composite(disc, (round(c[0] - R), round(c[1] - R)))


def frame(t):
    c = Image.open(D / "bg.jpg").convert("RGBA").resize((W, H))
    if t < CATCH:
        if t >= ROLL_START:
            ball(c, ball_pos(t), t * 30)
        if t >= DROP_START:
            q = min(1, (t - DROP_START) / (CATCH - DROP_START))
            x, y, w, h = lay["console.png"]
            drop = (y * k + h * k + H * .15) * (1 - q * q)
            place(c, "console.png", 0, -drop, angle=(1 - q) ** 2 * .9)
    else:
        place(c, "sonic.png")
    ImageDraw.Draw(c).text((20, 20), f"t = {t:.2f} s", fill=(255, 255, 255))
    return c.convert("RGB").resize((640, 360))


times = [.45, .70, .90, 1.05, 1.15, 1.6]
sheet = Image.new("RGB", (640 * 3, 360 * 2))
for i, t in enumerate(times):
    sheet.paste(frame(t), ((i % 3) * 640, (i // 3) * 360))
out = ROOT / "art" / "preview"
out.mkdir(parents=True, exist_ok=True)
sheet.save(out / "intro-sheet.png")
print(out / "intro-sheet.png")
