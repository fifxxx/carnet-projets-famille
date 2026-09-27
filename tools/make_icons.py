#!/usr/bin/env python3
"""Génère les icônes de l'application (écran d'accueil du téléphone).

Motif : la couverture marine du carnet, une page crème, le signet ocre
et une pièce dorée. Dessiné en très grand puis réduit, pour des bords nets.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

NAVY       = (31, 46, 69)
NAVY_LIGHT = (49, 68, 99)
CREAM      = (251, 243, 228)
CREAM_DIM  = (235, 224, 203)
OCHRE      = (201, 138, 44)
GOLD       = (217, 164, 65)
GOLD_DARK  = (168, 122, 38)
INK_SOFT   = (60, 78, 107)

SERIF_BOLD = "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf"
FALLBACK   = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

OUT = os.path.join(os.path.dirname(__file__), "..", "icons")
os.makedirs(OUT, exist_ok=True)


def font(size):
    for path in (SERIF_BOLD, FALLBACK):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_mark(img, cx, cy, span):
    """Dessine le carnet + la pièce, centré sur (cx, cy), tenant dans `span`."""
    d = ImageDraw.Draw(img, "RGBA")
    u = span  # unité de référence

    # --- page du carnet -------------------------------------------------
    pw, ph = u * 0.62, u * 0.76
    px = cx - u * 0.36
    py = cy - ph / 2
    # ombre portée douce sous la page
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [px + u * 0.03, py + u * 0.05, px + pw + u * 0.03, py + ph + u * 0.05],
        radius=u * 0.07, fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(u * 0.035))
    img.alpha_composite(shadow)

    d.rounded_rectangle([px, py, px + pw, py + ph], radius=u * 0.07, fill=CREAM)
    # liseré chaud sur le bord droit, effet tranche de papier
    d.rounded_rectangle([px + pw - u * 0.05, py, px + pw, py + ph],
                        radius=u * 0.07, fill=CREAM_DIM)
    d.rounded_rectangle([px, py, px + pw - u * 0.04, py + ph],
                        radius=u * 0.07, fill=CREAM)

    # --- signet / dos du carnet ----------------------------------------
    bx = px + u * 0.09
    d.rectangle([bx, py, bx + u * 0.085, py + ph], fill=OCHRE)

    # --- lignes d'écriture ---------------------------------------------
    lx0 = bx + u * 0.16
    lx1 = px + pw - u * 0.12
    for i, frac in enumerate((0.26, 0.42, 0.58)):
        ly = py + ph * frac
        x1 = lx1 if i < 2 else lx0 + (lx1 - lx0) * 0.55  # dernière ligne plus courte
        d.rounded_rectangle([lx0, ly, x1, ly + u * 0.038],
                            radius=u * 0.019, fill=INK_SOFT + (110,))

    # --- pièce ----------------------------------------------------------
    r = u * 0.235
    ccx, ccy = cx + u * 0.30, cy + u * 0.29
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse(
        [ccx - r - u * 0.03, ccy - r - u * 0.01, ccx + r + u * 0.03, ccy + r + u * 0.05],
        fill=(0, 0, 0, 110))
    glow = glow.filter(ImageFilter.GaussianBlur(u * 0.03))
    img.alpha_composite(glow)

    d.ellipse([ccx - r, ccy - r, ccx + r, ccy + r], fill=GOLD_DARK)
    d.ellipse([ccx - r * 0.93, ccy - r * 0.93, ccx + r * 0.93, ccy + r * 0.93], fill=GOLD)
    d.ellipse([ccx - r * 0.74, ccy - r * 0.74, ccx + r * 0.74, ccy + r * 0.74],
              outline=GOLD_DARK + (150,), width=int(u * 0.016))

    # symbole euro
    f = font(int(r * 1.32))
    txt = "€"
    bbox = d.textbbox((0, 0), txt, font=f)
    d.text((ccx - (bbox[2] - bbox[0]) / 2 - bbox[0],
            ccy - (bbox[3] - bbox[1]) / 2 - bbox[1]),
           txt, font=f, fill=NAVY)


def build(size, maskable=False, rounded=True):
    """Compose une icône complète. `maskable` laisse une marge de sécurité."""
    SS = 4                      # suréchantillonnage
    S = size * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    if rounded and not maskable:
        d.rounded_rectangle([0, 0, S, S], radius=S * 0.225, fill=NAVY)
    else:
        d.rectangle([0, 0, S, S], fill=NAVY)

    # halo discret en haut à gauche, pour éviter un fond parfaitement plat
    halo = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([-S * 0.25, -S * 0.35, S * 0.75, S * 0.55],
                                 fill=NAVY_LIGHT + (120,))
    halo = halo.filter(ImageFilter.GaussianBlur(S * 0.10))
    base = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    if rounded and not maskable:
        ImageDraw.Draw(base).rounded_rectangle([0, 0, S, S], radius=S * 0.225,
                                               fill=(255, 255, 255, 255))
    else:
        ImageDraw.Draw(base).rectangle([0, 0, S, S], fill=(255, 255, 255, 255))
    img.alpha_composite(Image.composite(halo, Image.new("RGBA", (S, S), (0, 0, 0, 0)),
                                        base.split()[3]))

    # zone de sécurité : plus petit pour les icônes masquables (Android)
    span = S * (0.52 if maskable else 0.66)
    # la pièce déborde en bas à droite : on recentre le motif dans son ensemble
    draw_mark(img, S / 2 - span * 0.085, S / 2 - span * 0.075, span)

    return img.resize((size, size), Image.LANCZOS)


def main():
    jobs = [
        ("icon-192.png", 192, False, True),
        ("icon-512.png", 512, False, True),
        ("icon-maskable-512.png", 512, True, False),
        ("apple-touch-icon.png", 180, False, False),   # iOS arrondit lui-même
        ("favicon-32.png", 32, False, True),
    ]
    for name, size, maskable, rounded in jobs:
        img = build(size, maskable=maskable, rounded=rounded)
        if name == "apple-touch-icon.png":
            bg = Image.new("RGB", img.size, NAVY)      # iOS refuse la transparence
            bg.paste(img, (0, 0), img)
            bg.save(os.path.join(OUT, name))
        else:
            img.save(os.path.join(OUT, name))
        print("écrit :", name, f"{size}x{size}")

    # aperçu côte à côte pour vérification visuelle
    preview = Image.new("RGB", (192 * 3 + 80, 232), (245, 245, 245))
    for i, n in enumerate(("icon-192.png", "icon-maskable-512.png", "apple-touch-icon.png")):
        im = Image.open(os.path.join(OUT, n)).convert("RGB").resize((192, 192), Image.LANCZOS)
        preview.paste(im, (20 + i * (192 + 20), 20))
    preview.save(os.path.join(OUT, "_apercu.png"))
    print("aperçu écrit")


if __name__ == "__main__":
    main()
