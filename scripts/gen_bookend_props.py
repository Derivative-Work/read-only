"""M6: the bookends' printed props as textures (brief: "Design the badge and schedule as rendered props (no logo, no real
names), plus the gold VIP and 'EXPIRED' versions of the badge"; planning chat: "keep the real times, but replace
interviewers' names and room names ... with solid redaction bars").

The real schedule and badge (reference/private/, the human's) were read for two things only: the eight time slots
with the kind of each meeting, and the badge's date and time. No name, title, room, company, logo or mascot is
copied; every name is a redaction bar, its length varied.

  assets/gen/props/badge_visitor.png   the self-expiring visitor badge as printed that morning
  assets/gen/props/badge_expired.png   the same badge a day later: the red stripes have bled through, "EXPIRED"
  assets/gen/props/badge_vip.png       the gold VIP version (the VIP bots' lanyards)
  assets/gen/props/schedule.png        the folded day schedule, names and room redacted

Usage: .venv/bin/python -I scripts/gen_bookend_props.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path("assets/gen/props")
FONT = "assets/fonts/Inter-Medium-flat.ttf"
DATE = "Mar 27, 2018 · 10:51 AM"
SLOTS = [("11:00am–12:00pm", 0.62, "Technical Interview"), ("12:00pm–12:30pm", 0.48, "Lunch!"),
         ("12:30pm–1:00pm", 0.55, "Cross-functional Interview"), ("1:00pm–2:00pm", 0.66, "Technical Interview"),
         ("2:00pm–2:30pm", 0.5, "Candidate AmA"), ("2:30pm–3:30pm", 0.58, "Technical Interview"),
         ("3:30pm–4:00pm", 0.7, "Hiring Manager Interview"), ("4:00pm–4:30pm", 0.6, "")]


def font(px):
    return ImageFont.truetype(FONT, px)


def grain(im, amount=6, seed=1):
    a = np.asarray(im).astype(np.float32)
    a += np.random.default_rng(seed).normal(0, amount, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def badge(kind):
    """A 3.5 x 2.25 in visitor badge at 300 dpi: a blank avatar square, the date, a perforation line."""
    W, H = 1050, 675
    base = {"visitor": (246, 246, 244), "expired": (246, 246, 244), "vip": (214, 178, 92)}[kind]
    im = Image.new("RGB", (W, H), base)
    d = ImageDraw.Draw(im)
    ink = (28, 28, 30) if kind != "vip" else (52, 38, 10)
    if kind == "expired":  # the self-expiring stripes bled through overnight
        stripes = Image.new("L", (W, H), 0)
        sd = ImageDraw.Draw(stripes)
        for x in range(-H, W, 70):
            sd.polygon([(x, H), (x + 34, H), (x + 34 + H, 0), (x + H, 0)], fill=150)
        stripes = stripes.filter(ImageFilter.GaussianBlur(5))
        red = Image.new("RGB", (W, H), (196, 38, 46))
        im = Image.composite(red, im, stripes)
        d = ImageDraw.Draw(im)
    d.line([(40, 110), (W - 40, 110)], fill=ink, width=3)
    for x in range(40, W - 40, 22):  # the tear-off perforation
        d.ellipse([x, 104, x + 8, 112], fill=base)
    title = {"visitor": "VISITOR", "expired": "VISITOR", "vip": "VIP"}[kind]
    d.text((W / 2, 62), title, font=font(70), fill=ink, anchor="mm")
    d.rounded_rectangle([60, 170, 300, 410], 24, fill=(212, 212, 210) if kind != "vip" else (190, 152, 70))
    d.ellipse([135, 205, 225, 295], fill=(236, 236, 234) if kind != "vip" else (222, 192, 120))
    d.pieslice([100, 300, 260, 460], 180, 360, fill=(236, 236, 234) if kind != "vip" else (222, 192, 120))
    d.rounded_rectangle([340, 200, 900, 262], 10, fill=ink)  # the name: redacted
    d.text((340, 320), DATE if kind != "vip" else "ALL ACCESS", font=font(44), fill=ink)
    d.text((340, 390), "Valid today only" if kind != "vip" else "No expiry", font=font(36),
           fill=(90, 90, 92) if kind != "vip" else (90, 66, 20))
    if kind == "expired":
        st = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([210, 470, 840, 620], 18, outline=(255, 255, 255, 255), width=10)
        sd.text((525, 545), "EXPIRED", font=font(110), fill=(255, 255, 255, 255), anchor="mm")
        im = Image.alpha_composite(im.convert("RGBA"), st.rotate(-4, resample=Image.BICUBIC, center=(525, 545))).convert("RGB")
    elif kind == "vip":
        d.text((W / 2, 545), "★  VIP  ★", font=font(90), fill=ink, anchor="mm")
    else:
        d.rounded_rectangle([60, 500, W - 60, 600], 14, outline=(200, 200, 198), width=3)
        d.text((W / 2, 550), "This badge expires", font=font(40), fill=(150, 150, 152), anchor="mm")
    return grain(im, 4, {"visitor": 1, "expired": 2, "vip": 3}[kind])


def schedule():
    """A letter page at 150 dpi, folded in thirds (the creases shaded)."""
    W, H = 1275, 1650
    im = Image.new("RGB", (W, H), (244, 241, 232))
    d = ImageDraw.Draw(im)
    ink = (34, 34, 36)
    d.text((W / 2, 200), "Welcome!", font=font(48), fill=ink, anchor="mm")
    d.text((110, 300), "Here is your schedule for the day:", font=font(34), fill=ink)
    y = 400
    for times, bar, kind in SLOTS:
        d.text((110, y), times + ":", font=font(32), fill=ink)
        x0 = 430
        x1 = x0 + int(bar * 520)
        d.rectangle([x0, y + 2, x1, y + 38], fill=(16, 16, 18))
        if kind:
            d.text((x1 + 18, y), f"({kind})", font=font(30), fill=ink)
        y += 78
    d.text((110, y + 40), "Room:", font=font(32), fill=ink)
    d.rectangle([215, y + 42, 560, y + 78], fill=(16, 16, 18))
    d.text((W / 2, y + 200), "Good luck!", font=font(40), fill=ink, anchor="mm")
    a = np.asarray(im).astype(np.float32)
    for fy in (H // 3, 2 * H // 3):  # the folds
        for k in range(-30, 31):
            a[fy + k] *= 1 - 0.08 * np.exp(-(k / 10) ** 2) + (0.03 if k > 0 else -0.02) * np.exp(-(k / 18) ** 2)
    return grain(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), 3, 4)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for k in ("visitor", "expired", "vip"):
        badge(k).save(OUT / f"badge_{k}.png")
    schedule().save(OUT / "schedule.png")
    print("props ->", OUT)


if __name__ == "__main__":
    main()
