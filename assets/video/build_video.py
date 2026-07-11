"""
MV Data Governance · Generador del video de demo (sin dependencias externas
de video: PIL + imageio-ffmpeg).

Produce ``assets/video/MVDataGovernance_Demo.mp4`` (1280×720, ~40 s) con las
escenas del recorrido del producto en los tres idiomas, y lo copia a
``landing/video/`` para que la landing lo sirva.

Ejecutar desde la raíz del repo:
    python assets/video/build_video.py
"""
from __future__ import annotations

import os
import shutil

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
FPS = 24
NAVY = (8, 21, 39)
NAVY2 = (13, 36, 64)
AMBER = (242, 180, 65)
BLUE = (47, 116, 192)
GREEN = (0, 200, 150)
RED = (224, 92, 92)
INK = (234, 241, 251)
MUTED = (157, 176, 200)
FAINT = (108, 127, 153)

_FONT_DIR = "/usr/share/fonts/truetype/dejavu"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "assets", "video", "MVDataGovernance_Demo.mp4")
LANDING_COPY = os.path.join(ROOT, "landing", "video", "MVDataGovernance_Demo.mp4")


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(os.path.join(_FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


def base_frame() -> Image.Image:
    """Fondo navy con brillos radiales estilo landing."""
    img = Image.new("RGB", (W, H), NAVY)
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W * 0.62, -H * 0.35, W * 1.25, H * 0.45], fill=(36, 27, 8))
    gd.ellipse([-W * 0.2, -H * 0.1, W * 0.38, H * 0.55], fill=(9, 23, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    return Image.blend(img, Image.blend(img, glow, 0.9), 0.55)


def ease(p: float) -> float:
    p = max(0.0, min(1.0, p))
    return 3 * p * p - 2 * p * p * p


def center_text(d: ImageDraw.ImageDraw, y: int, text: str,
                f: ImageFont.FreeTypeFont, fill, alpha_bg=None):
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=fill)


def badge(d: ImageDraw.ImageDraw, cx: int, y: int, text: str, f):
    w = d.textlength(text, font=f)
    pad = 16
    d.rounded_rectangle([cx - w / 2 - pad, y - 8, cx + w / 2 + pad, y + 30],
                        radius=19, outline=AMBER, width=2,
                        fill=(24, 22, 12))
    d.text((cx - w / 2, y - 1), text, font=f, fill=AMBER)


def scene_intro(p: float) -> Image.Image:
    img = base_frame()
    d = ImageDraw.Draw(img)
    a = ease(p * 3)  # aparece rápido
    # logo MV
    size = 74
    d.rounded_rectangle([W / 2 - size, 150, W / 2 + size, 150 + size * 2],
                        radius=28, fill=(15, 33, 53), outline=AMBER, width=3)
    f_logo = font(64)
    lw = d.textlength("MV", font=f_logo)
    d.text((W / 2 - lw / 2, 150 + size - 40), "MV", font=f_logo, fill=AMBER)
    if p > 0.18:
        center_text(d, 340, "MV Data Governance", font(58), INK)
    if p > 0.38:
        center_text(d, 425, "Gobierno de datos claro, medible y listo para BI", font(26, False), MUTED)
    if p > 0.52:
        center_text(d, 462, "Clear, measurable, BI-ready data governance", font(22, False), FAINT)
        center_text(d, 494, "Governança de dados clara, mensurável e pronta para BI", font(22, False), FAINT)
    if p > 0.7:
        badge(d, W // 2, 560, "100% WEB + PC · ES / EN / PT · SIN APK", font(19))
    return img


def _kpi_card(d, x, y, w, h, label, value, vcolor):
    d.rounded_rectangle([x, y, x + w, y + h], radius=14,
                        fill=(15, 33, 53), outline=(29, 49, 73), width=2)
    d.text((x + 18, y + 14), label, font=font(15, False), fill=MUTED)
    d.text((x + 18, y + 40), value, font=font(34), fill=vcolor)


def scene_quality(p: float) -> Image.Image:
    img = base_frame()
    d = ImageDraw.Draw(img)
    center_text(d, 46, "Calidad en 6 dimensiones · Quality · Qualidade", font(34), INK)
    center_text(d, 96, "Motor de reglas con umbrales y alertas · Rule engine with thresholds and alerts",
                font(18, False), MUTED)
    a = ease(p * 1.6)
    idx = 99.1 * a
    _kpi_card(d, 130, 150, 320, 92, "ÍNDICE DE CALIDAD · QUALITY INDEX", f"{idx:.1f} / 100", GREEN)
    _kpi_card(d, 480, 150, 320, 92, "DATASETS", f"{int(round(4 * a))}", INK)
    _kpi_card(d, 830, 150, 320, 92, "REGLAS · RULES", f"{int(round(15 * a))}/17 ✓", AMBER)
    dims = [("Completitud · Completeness", 98.6), ("Unicidad · Uniqueness", 99.8),
            ("Validez · Validity", 98.6), ("Consistencia · Consistency", 99.3),
            ("Puntualidad · Timeliness", 99.7), ("Exactitud · Accuracy", 98.0)]
    y = 290
    for i, (name, score) in enumerate(dims):
        pa = ease(max(0.0, p * 2.2 - i * 0.16))
        d.text((130, y + 4), name, font=font(17, False), fill=INK)
        bx0, bx1 = 480, 1040
        d.rounded_rectangle([bx0, y + 2, bx1, y + 22], radius=10, fill=(20, 39, 60))
        fill_w = (bx1 - bx0) * (score / 100) * pa
        if fill_w > 20:
            col = GREEN if score >= 99 else AMBER
            d.rounded_rectangle([bx0, y + 2, bx0 + fill_w, y + 22], radius=10, fill=col)
        d.text((1058, y), f"{score * pa:.1f}", font=font(17), fill=MUTED)
        y += 62
    return img


def scene_catalog(p: float) -> Image.Image:
    img = base_frame()
    d = ImageDraw.Draw(img)
    center_text(d, 46, "Catálogo de datos · Data catalog · Catálogo de dados", font(34), INK)
    center_text(d, 96, "Dueño, steward, clasificación y frescura por dataset", font(18, False), MUTED)
    rows = [
        ("dim_customers", "Clientes", "M. Viera", "PII", GREEN, "99.0"),
        ("dim_products", "Productos", "R. Costa", "Interna", AMBER, "98.3"),
        ("fct_sales", "Ventas", "L. Santos", "Confidencial", GREEN, "99.5"),
        ("fct_payments", "Finanzas", "A. Gomez", "Confidencial", GREEN, "99.6"),
    ]
    x0, y = 110, 170
    headers = ["DATASET", "DOMINIO", "STEWARD", "CLASIFICACIÓN", "CALIDAD"]
    xs = [x0, x0 + 280, x0 + 500, x0 + 700, x0 + 960]
    d.rounded_rectangle([x0 - 20, y - 16, W - 90, y + 24], radius=10, fill=(15, 33, 53))
    for hx, htxt in zip(xs, headers):
        d.text((hx, y - 4), htxt, font=font(15), fill=AMBER)
    y += 56
    for i, (ds, dom, stw, cls, qc, q) in enumerate(rows):
        pa = ease(p * 2.4 - i * 0.28)
        if pa <= 0:
            continue
        d.rounded_rectangle([x0 - 20, y - 14, W - 90, y + 36], radius=10,
                            fill=(11, 26, 45), outline=(29, 49, 73), width=1)
        d.text((xs[0], y), ds, font=font(19), fill=INK)
        d.text((xs[1], y), dom, font=font(18, False), fill=MUTED)
        d.text((xs[2], y), stw, font=font(18, False), fill=MUTED)
        pill_col = RED if cls == "PII" else BLUE
        pw = d.textlength(cls, font=font(14))
        d.rounded_rectangle([xs[3] - 8, y - 2, xs[3] + pw + 10, y + 24],
                            radius=12, outline=pill_col, width=2)
        d.text((xs[3] + 1, y), cls, font=font(14), fill=pill_col)
        d.text((xs[4], y), q, font=font(19), fill=qc)
        y += 74
    if p > 0.75:
        center_text(d, 620, "✓ 17 reglas activas · PII protegida · diccionario trilingüe",
                    font(19, False), FAINT)
    return img


def scene_lineage(p: float) -> Image.Image:
    img = base_frame()
    d = ImageDraw.Draw(img)
    center_text(d, 46, "Linaje de punta a punta · End-to-end lineage", font(34), INK)
    center_text(d, 96, "De la fuente al dashboard de BI · From source to BI dashboard",
                font(18, False), MUTED)
    layers = [
        [("CRM",), ("ERP",), ("POS",)],
        [("raw.customers",), ("raw.products",), ("raw.sales",)],
        [("dim_customers",), ("dim_products",), ("fct_sales",)],
        [("mart_ventas_360",)],
        [("Power BI · Tableau",)],
    ]
    cols_x = [150, 400, 660, 930, 1130]
    layer_col = [FAINT, BLUE, GREEN, AMBER, (196, 121, 232)]
    pos = {}
    for li, layer in enumerate(layers):
        n = len(layer)
        for ni, (name,) in enumerate(layer):
            y = 380 + (ni - (n - 1) / 2) * 150
            pos[(li, ni)] = (cols_x[li], y)
    edges = [((0, 0), (1, 0)), ((0, 1), (1, 1)), ((0, 2), (1, 2)),
             ((1, 0), (2, 0)), ((1, 1), (2, 1)), ((1, 2), (2, 2)),
             ((2, 0), (3, 0)), ((2, 1), (3, 0)), ((2, 2), (3, 0)),
             ((3, 0), (4, 0))]
    prog = ease(p * 1.25)
    for i, (a, b) in enumerate(edges):
        ep = ease(prog * len(edges) - i * 0.55)
        if ep <= 0:
            continue
        (x0, y0), (x1, y1) = pos[a], pos[b]
        xm, ym = x0 + (x1 - x0) * ep, y0 + (y1 - y0) * ep
        d.line([x0, y0, xm, ym], fill=AMBER, width=3)
    for li, layer in enumerate(layers):
        for ni, (name,) in enumerate(layer):
            x, y = pos[(li, ni)]
            d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=layer_col[li],
                      outline=(255, 255, 255), width=2)
            f = font(16)
            wl = d.textlength(name, font=f)
            d.text((x - wl / 2, y + 20), name, font=f, fill=INK)
    return img


def scene_bi(p: float) -> Image.Image:
    img = base_frame()
    d = ImageDraw.Draw(img)
    center_text(d, 46, "Compatible con cualquier BI · Works with any BI tool", font(34), INK)
    center_text(d, 96, "CSV · Excel · JSON · Parquet · API REST", font(20), AMBER)
    tools = ["Power BI", "Tableau", "Looker", "MicroStrategy", "Qlik", "Excel"]
    y0 = 190
    for i, name in enumerate(tools):
        pa = ease(p * 2.6 - i * 0.18)
        if pa <= 0:
            continue
        col_i, row_i = i % 3, i // 3
        x = 150 + col_i * 340
        y = y0 + row_i * 130
        d.rounded_rectangle([x, y, x + 300, y + 96], radius=16,
                            fill=(15, 33, 53), outline=(42, 65, 96), width=2)
        f = font(26)
        wl = d.textlength(name, font=f)
        d.text((x + (300 - wl) / 2, y + 32), name, font=f, fill=INK)
    if p > 0.62:
        d.rounded_rectangle([150, 480, 1130, 600], radius=14, fill=(9, 20, 35),
                            outline=(42, 65, 96), width=2)
        d.text((180, 502), "GET http://127.0.0.1:8600/api/catalog?lang=es",
               font=font(22), fill=(127, 212, 168))
        d.text((180, 546), "GET http://127.0.0.1:8600/api/quality_results?format=csv",
               font=font(22), fill=(127, 212, 168))
    return img


def scene_outro(p: float) -> Image.Image:
    img = base_frame()
    d = ImageDraw.Draw(img)
    center_text(d, 210, "MV Data Governance", font(56), INK)
    center_text(d, 300, "Tus datos, gobernados. Tus decisiones, confiables.", font(24, False), MUTED)
    center_text(d, 340, "Your data, governed. · Seus dados, governados.", font(20, False), FAINT)
    if p > 0.35:
        badge(d, W // 2, 430, "DESCARGA · DOWNLOAD: MV_DataGovernance.bat / .EXE", font(19))
    if p > 0.6:
        center_text(d, 510, "github.com/vieraschiavi/Mv-Data-Governance", font(21), AMBER)
    return img


SCENES = [
    (scene_intro, 6.0),
    (scene_quality, 8.0),
    (scene_catalog, 8.0),
    (scene_lineage, 8.0),
    (scene_bi, 7.0),
    (scene_outro, 5.0),
]
FADE = 0.5  # segundos de fundido entre escenas


def build() -> str:
    writer = imageio.get_writer(OUT, fps=FPS, codec="libx264",
                                quality=7, macro_block_size=16,
                                ffmpeg_params=["-pix_fmt", "yuv420p"])
    black = Image.new("RGB", (W, H), (0, 0, 0))
    for scene, secs in SCENES:
        n = int(secs * FPS)
        for f_i in range(n):
            p = f_i / max(1, n - 1)
            frame = scene(p)
            # fundido de entrada/salida por escena
            t = f_i / FPS
            rem = secs - t
            if t < FADE:
                frame = Image.blend(black, frame, ease(t / FADE))
            elif rem < FADE:
                frame = Image.blend(black, frame, ease(rem / FADE))
            writer.append_data(np.asarray(frame))
    writer.close()
    os.makedirs(os.path.dirname(LANDING_COPY), exist_ok=True)
    shutil.copyfile(OUT, LANDING_COPY)
    return OUT


if __name__ == "__main__":
    path = build()
    size_mb = os.path.getsize(path) / 1e6
    print(f"Video generado: {path} ({size_mb:.1f} MB) · copiado a landing/video/")
