# Builds sce_sys/icon0.png (512x512, the PS4 app icon): DeCast-S4, a GD-ROM style disc on a
# deep blue background with the app's name. Drawn at 2x and scaled down for smooth edges.
# Needs Pillow (Windows python on this machine).
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

here = Path(__file__).resolve().parent.parent / "sce_sys"
S = 1024
icon = Image.new("RGB", (S, S))
draw = ImageDraw.Draw(icon)


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def circle(cx, cy, r, fill=None, outline=None, width=1):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=outline, width=width)


# background: deep blue, lighter at the top
for y in range(S):
    draw.line((0, y, S, y), fill=mix((28, 52, 110), (8, 14, 36), y / S))

cx, cy = S // 2, 420
# the disc: shadow, silver body with a rainbow sheen in rings, the inner hub
circle(cx + 12, cy + 18, 318, fill=(4, 8, 22))
for r in range(310, 96, -2):
    t = (r - 96) / (310 - 96)
    hue = (math.sin(t * 9.0) + 1) / 2
    base = mix((176, 186, 204), (236, 240, 248), t)
    tint = mix((150, 200, 255), (255, 196, 150), hue)
    circle(cx, cy, r, fill=mix(base, tint, 0.18))
# the high-density area boundary of a GD-ROM
circle(cx, cy, 214, outline=(120, 132, 156), width=4)
circle(cx, cy, 96, fill=(206, 212, 224))
circle(cx, cy, 70, fill=(150, 160, 178))
circle(cx, cy, 44, fill=(16, 26, 58))

# an orange "D" sweep over the disc
draw.arc((cx - 250, cy - 250, cx + 250, cy + 250), start=-100, end=150, fill=(255, 128, 32), width=46)
draw.arc((cx - 250, cy - 250, cx + 250, cy + 250), start=-100, end=150, fill=(255, 168, 72), width=14)

# the name
def font(size):
    for name in ("arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()

title = "DeCast-S4"
f = font(150)
w = draw.textlength(title, font=f)
draw.text(((S - w) / 2 + 4, 792 + 5), title, font=f, fill=(4, 8, 22))
draw.text(((S - w) / 2, 792), title, font=f, fill=(244, 246, 252))

icon = icon.resize((512, 512), Image.LANCZOS)
here.mkdir(exist_ok=True)
icon.save(here / "icon0.png")
print("wrote", here / "icon0.png")
