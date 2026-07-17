"""
MV Data Governance · Generador del video de demo (PIL + imageio-ffmpeg) con
narración en voz por idioma (Piper TTS): español (es_AR "daniela"), inglés
(en_US "amy") y portugués (pt_BR "faber").

Produce UN video por idioma, cada uno hablado en ese idioma:
    assets/video/MVDataGovernance_Demo_es.mp4
    assets/video/MVDataGovernance_Demo_en.mp4
    assets/video/MVDataGovernance_Demo_pt.mp4
y una copia por defecto assets/video/MVDataGovernance_Demo.mp4 (= español) para
compatibilidad. Todos se copian a landing/video/ para que la landing sirva el
que corresponda al idioma elegido por el visitante.

La voz va sincronizada escena por escena (la duración de cada escena se ajusta a
su narración, sin desfases). El texto en pantalla se mantiene trilingüe.

Ejecutar desde la raíz del repo:
    python assets/video/build_video.py

Voces (opcional pero recomendado): descargá cada modelo una vez y exportá su
ruta. Sin modelo para un idioma, ese video sale sin narración (pero se genera).
    pip install piper-tts
    # es_AR-daniela-high, en_US-amy-medium, pt_BR-faber-medium (HuggingFace):
    #   https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/...
    MVDG_VOICE_ONNX_ES=./es_AR-daniela-high.onnx \
    MVDG_VOICE_ONNX_EN=./en_US-amy-medium.onnx \
    MVDG_VOICE_ONNX_PT=./pt_BR-faber-medium.onnx \
    python assets/video/build_video.py
    # MVDG_VOICE_ONNX (sin sufijo) sigue valiendo como alias del modelo español.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import wave

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
VIDEO_DIR = os.path.join(ROOT, "assets", "video")
LANDING_DIR = os.path.join(ROOT, "landing", "video")

LANGS = ["es", "en", "pt"]
# variable de entorno con el modelo de voz Piper de cada idioma
_VOICE_ENV = {"es": "MVDG_VOICE_ONNX_ES", "en": "MVDG_VOICE_ONNX_EN",
              "pt": "MVDG_VOICE_ONNX_PT"}


def _voice_model(lang: str) -> str:
    """Ruta al modelo Piper del idioma (o '' si no está configurado)."""
    path = os.environ.get(_VOICE_ENV[lang], "")
    if not path and lang == "es":  # alias histórico: MVDG_VOICE_ONNX == español
        path = os.environ.get("MVDG_VOICE_ONNX", "")
    return path if path and os.path.exists(path) else ""


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


def scene_enterprise(p: float) -> Image.Image:
    img = base_frame()
    d = ImageDraw.Draw(img)
    center_text(d, 46, "Integración enterprise · Enterprise integration", font(32), INK)
    center_text(d, 94, "Purview · Collibra · Azure · MIP — apagado por defecto",
                font(18, False), MUTED)
    tools = [
        "Migración a Purview", "Collibra: push + pull", "Descubrimiento Azure",
        "Enforcement de acceso", "Etiquetas MIP", "Escaneo batch",
    ]
    y0 = 190
    for i, name in enumerate(tools):
        pa = ease(p * 3.2 - i * 0.22)
        if pa <= 0:
            continue
        col_i, row_i = i % 3, i // 3
        x = 130 + col_i * 350
        y = y0 + row_i * 170
        d.rounded_rectangle([x, y, x + 310, y + 130], radius=16,
                            fill=(15, 33, 53), outline=AMBER, width=2)
        d.line([x + 24, y + 26, x + 60, y + 26], fill=AMBER, width=4)
        f = font(21)
        words = name.split(" ")
        lines = [" ".join(words[:2]), " ".join(words[2:])] if len(words) > 2 else [name]
        ty = y + 52
        for line in lines:
            if not line:
                continue
            d.text((x + 24, ty), line, font=f, fill=INK)
            ty += 30
    return img


def scene_outro(p: float) -> Image.Image:
    img = base_frame()
    d = ImageDraw.Draw(img)
    center_text(d, 210, "MV Data Governance", font(56), INK)
    center_text(d, 300, "Tus datos, gobernados. Tus decisiones, confiables.", font(24, False), MUTED)
    center_text(d, 340, "Your data, governed. · Seus dados, governados.", font(20, False), FAINT)
    # cierre orientado a clientes: solo la web de venta — sin nombres de
    # archivos (.bat/.exe) ni el repositorio de GitHub (pedido explícito)
    if p > 0.4:
        badge(d, W // 2, 450, "mv-data-governance.vercel.app", font(22))
    return img


# (escena, duración mínima visual, narración por idioma {es, en, pt})
SCENES = [
    (scene_intro, 6.0, {
        "es": "MV Data Governance: gobierno de datos claro, medible y listo "
              "para BI. Cien por ciento web y PC, en español, inglés y portugués.",
        "en": "MV Data Governance: clear, measurable, BI-ready data governance. "
              "One hundred percent web and desktop, in Spanish, English and "
              "Portuguese.",
        "pt": "MV Data Governance: governança de dados clara, mensurável e "
              "pronta para BI. Cem por cento web e desktop, em espanhol, inglês "
              "e português.",
    }),
    (scene_quality, 8.0, {
        "es": "La calidad de tus datos, medida en seis dimensiones: completitud, "
              "unicidad, validez, consistencia, puntualidad y exactitud. Diecisiete "
              "reglas corren solas y te muestran exactamente dónde está el problema "
              "y cuántas filas afecta.",
        "en": "Your data quality, measured across six dimensions: completeness, "
              "uniqueness, validity, consistency, timeliness and accuracy. Seventeen "
              "rules run on their own and show you exactly where the problem is and "
              "how many rows it affects.",
        "pt": "A qualidade dos seus dados, medida em seis dimensões: completude, "
              "unicidade, validade, consistência, atualidade e exatidão. Dezessete "
              "regras rodam sozinhas e mostram exatamente onde está o problema e "
              "quantas linhas ele afeta.",
    }),
    (scene_catalog, 8.0, {
        "es": "Un catálogo único para toda la empresa: cada dataset con su dueño, "
              "su steward y su clasificación. Los datos personales quedan "
              "identificados y protegidos desde el primer día.",
        "en": "A single catalog for the whole company: every dataset with its "
              "owner, its steward and its classification. Personal data is "
              "identified and protected from day one.",
        "pt": "Um catálogo único para toda a empresa: cada dataset com seu dono, "
              "seu steward e sua classificação. Os dados pessoais ficam "
              "identificados e protegidos desde o primeiro dia.",
    }),
    (scene_lineage, 8.0, {
        "es": "Linaje de punta a punta: seguí el recorrido del dato desde la "
              "fuente hasta el tablero de BI, aguas arriba y aguas abajo, con un clic.",
        "en": "End-to-end lineage: follow the data's journey from the source all "
              "the way to the BI dashboard, upstream and downstream, with one click.",
        "pt": "Linhagem de ponta a ponta: siga o caminho do dado desde a origem "
              "até o painel de BI, para cima e para baixo, com um clique.",
    }),
    (scene_bi, 7.0, {
        "es": "Y todo se conecta con la herramienta que ya usás: Power BI, Tableau, "
              "Looker, MicroStrategy, Qlik o Excel. Por archivo o por API: el "
              "formato lo elegís vos.",
        "en": "And it all connects to the tool you already use: Power BI, Tableau, "
              "Looker, MicroStrategy, Qlik or Excel. By file or by API — you choose "
              "the format.",
        "pt": "E tudo se conecta com a ferramenta que você já usa: Power BI, "
              "Tableau, Looker, MicroStrategy, Qlik ou Excel. Por arquivo ou por "
              "API — o formato você escolhe.",
    }),
    (scene_enterprise, 9.0, {
        "es": "Y para los que ya usan Purview o Collibra: el programa migra el catálogo y "
              "el glosario por su API real, en las dos direcciones con Collibra. Además "
              "descubre tus recursos de datos en Azure, genera el enforcement de acceso, "
              "asigna etiquetas de sensibilidad y escanea todas tus conexiones de un saque. "
              "Todo apagado por defecto, activado solo con tus propias credenciales.",
        "en": "And for teams already using Purview or Collibra: the program migrates the "
              "catalog and glossary through their real API, both ways with Collibra. It "
              "also discovers your data resources in Azure, generates access enforcement, "
              "assigns sensitivity labels and scans every connection in one shot. All off "
              "by default, turned on only with your own credentials.",
        "pt": "E para quem já usa Purview ou Collibra: o programa migra o catálogo e o "
              "glossário pela API real, nas duas direções com o Collibra. Também descobre "
              "seus recursos de dados no Azure, gera o enforcement de acesso, atribui "
              "etiquetas de sensibilidade e escaneia todas as conexões de uma vez. Tudo "
              "desligado por padrão, ativado só com suas próprias credenciais.",
    }),
    (scene_outro, 5.0, {
        "es": "MV Data Governance. Tus datos gobernados, tus decisiones confiables. "
              "Descargalo hoy: sin APK, y sin que tus datos salgan de tu empresa.",
        "en": "MV Data Governance. Your data governed, your decisions trustworthy. "
              "Download it today: no APK, and without your data ever leaving your "
              "company.",
        "pt": "MV Data Governance. Seus dados governados, suas decisões confiáveis. "
              "Baixe hoje: sem APK, e sem que seus dados saiam da sua empresa.",
    }),
]
FADE = 0.5        # segundos de fundido entre escenas
VOICE_LEAD = 0.4  # la voz entra apenas después del corte de escena
VOICE_TAIL = 0.9  # aire después de cada frase


def _synth_narrations(tmpdir: str, lang: str) -> list[str] | None:
    """Genera un WAV por escena con Piper en el idioma dado. None si no hay
    modelo de voz configurado para ese idioma."""
    model = _voice_model(lang)
    if not model:
        return None
    try:
        from piper import PiperVoice
    except ImportError:
        return None
    voice = PiperVoice.load(model)
    paths = []
    for i, (_, _, narration) in enumerate(SCENES):
        text = narration[lang]
        path = os.path.join(tmpdir, f"nar_{lang}_{i}.wav")
        with wave.open(path, "wb") as w:
            voice.synthesize_wav(text, w)
        paths.append(path)
    return paths


def _wav_duration(path: str) -> float:
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def _scene_seconds(narrations: list[str] | None) -> list[float]:
    """Duración final de cada escena: la visual mínima o la narración + aire."""
    secs = []
    for i, (_, min_secs, _) in enumerate(SCENES):
        if narrations:
            secs.append(max(min_secs,
                            VOICE_LEAD + _wav_duration(narrations[i]) + VOICE_TAIL))
        else:
            secs.append(min_secs)
    return secs


def _mix_audio_track(narrations: list[str], secs: list[float],
                     out_wav: str) -> None:
    """Arma la pista completa: cada narración en el arranque de su escena."""
    with wave.open(narrations[0]) as w:
        rate, width, channels = w.getframerate(), w.getsampwidth(), w.getnchannels()
    total = np.zeros(int(sum(secs) * rate) + rate, dtype=np.int16)
    start = 0.0
    for i, nar in enumerate(narrations):
        with wave.open(nar) as w:
            data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
        at = int((start + VOICE_LEAD) * rate)
        total[at:at + len(data)] = data
        start += secs[i]
    total = total[:int(sum(secs) * rate)]
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(width)
        w.setframerate(rate)
        w.writeframes(total.tobytes())


def build_one(lang: str, tmpdir: str) -> tuple[str, bool]:
    """Genera el video de un idioma. Devuelve (ruta, tiene_voz)."""
    out = os.path.join(VIDEO_DIR, f"MVDataGovernance_Demo_{lang}.mp4")
    narrations = _synth_narrations(tmpdir, lang)
    secs_list = _scene_seconds(narrations)

    video_only = os.path.join(tmpdir, f"video_{lang}.mp4") if narrations else out
    writer = imageio.get_writer(video_only, fps=FPS, codec="libx264",
                                quality=7, macro_block_size=16,
                                ffmpeg_params=["-pix_fmt", "yuv420p"])
    black = Image.new("RGB", (W, H), (0, 0, 0))
    for (scene, _, _), secs in zip(SCENES, secs_list):
        n = int(round(secs * FPS))
        for f_i in range(n):
            p = f_i / max(1, n - 1)
            frame = scene(p)
            # fundido de entrada/salida por escena
            t = f_i / FPS
            rem = secs - t
            if t < FADE:
                frame = Image.blend(black, frame, ease(t / FADE))
            elif rem < FADE:
                frame = Image.blend(black, frame, ease(max(0.0, rem) / FADE))
            writer.append_data(np.asarray(frame))
    writer.close()

    if narrations:
        # pista de voz alineada a los cortes de escena + mux con ffmpeg
        track = os.path.join(tmpdir, f"narracion_{lang}.wav")
        _mix_audio_track(narrations, secs_list, track)
        from imageio_ffmpeg import get_ffmpeg_exe
        subprocess.run([get_ffmpeg_exe(), "-y", "-i", video_only, "-i", track,
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                        "-shortest", out],
                       check=True, capture_output=True)

    return out, bool(narrations)


def build() -> list[tuple[str, str, bool]]:
    """Genera un video por idioma (es/en/pt), los copia a landing/video/ y
    deja una copia por defecto (= español). Devuelve [(lang, ruta, con_voz)]."""
    os.makedirs(VIDEO_DIR, exist_ok=True)
    os.makedirs(LANDING_DIR, exist_ok=True)
    results = []
    for lang in LANGS:
        tmpdir = tempfile.mkdtemp(prefix=f"mvdg_video_{lang}_")
        try:
            path, has_voice = build_one(lang, tmpdir)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
        shutil.copyfile(path, os.path.join(LANDING_DIR, os.path.basename(path)))
        results.append((lang, path, has_voice))
    # copia por defecto (compatibilidad con el <source> histórico): español
    es_path = os.path.join(VIDEO_DIR, "MVDataGovernance_Demo_es.mp4")
    if os.path.exists(es_path):
        default = os.path.join(VIDEO_DIR, "MVDataGovernance_Demo.mp4")
        shutil.copyfile(es_path, default)
        shutil.copyfile(es_path, os.path.join(LANDING_DIR, "MVDataGovernance_Demo.mp4"))
    return results


if __name__ == "__main__":
    for lang, path, has_voice in build():
        size_mb = os.path.getsize(path) / 1e6
        voz = f"con voz ({lang})" if has_voice else "SIN voz (falta modelo)"
        print(f"[{lang}] {os.path.basename(path)} ({size_mb:.1f} MB) · {voz} · copiado a landing/video/")
