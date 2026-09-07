# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · video breve "antes y después" (ES / EN / PT).

Para qué es
───────────
El video de demo muestra QUÉ hace el producto. Un gerente no compra eso:
compra el resultado. Este video, de unos 40 segundos, muestra una sola cosa
— la misma cartera de datos antes y después de gobernarla — con los números
del caso de ejemplo puestos uno al lado del otro.

Los números NO están escritos acá
─────────────────────────────────
Salen de ``mvdg.lab_case.lab_measure()`` en el momento de generar el video:
el mismo motor de reglas que corre el programa, sobre el mismo caso que
publica la guía (``docs/caso_ejemplo/medir_impacto.py``). Si mañana cambian
las reglas y el resultado se mueve, el video se mueve con él. Un número
hardcodeado acá sería, tarde o temprano, una promesa que el producto ya no
cumple — y eso es exactamente lo que un gerente verifica.

Reusa el pipeline de ``build_video.py`` (render, narración Piper por escena,
mezcla y mux con ffmpeg): solo cambian las escenas y el guion.

Uso
───
    python assets/video/build_antes_despues.py

Sin modelos de voz configurados (MVDG_VOICE_ONNX_ES/EN/PT) sale igual, mudo.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile

from PIL import ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_video import (  # noqa: E402
    AMBER,
    FAINT,
    GREEN,
    INK,
    LANDING_DIR,
    LANGS,
    MUTED,
    RED,
    VIDEO_DIR,
    W,
    badge,
    base_frame,
    build_one,
    center_text,
    ease,
    font,
)

from mvdg.lab_case import lab_measure  # noqa: E402

NOMBRE = "AntesDespues"

# El sitio que se muestra al cierre. Tiene que ser el dominio que de verdad
# resuelve: un gerente lo tipea. Cuando haya dominio propio se define
# MVDG_SITE_HOST —la misma variable que ya usa el resto del proyecto— y se
# regenera el video; hasta entonces, el canónico de Vercel.
SITIO = os.environ.get("MVDG_SITE_HOST", "").strip() or "mv-data-governance.vercel.app"


# ── los números, del motor ──────────────────────────────────────────────
def medicion() -> dict:
    """El antes/después medido por el motor real, no una tabla escrita a mano."""
    m = lab_measure()
    a, d = m["summary_before"], m["summary_after"]
    return {
        "indice_antes": a["indice"], "indice_despues": d["indice"],
        "ok_antes": a["reglas_ok"], "ok_despues": d["reglas_ok"],
        "total": a["reglas_total"],
        "fallas_antes": a["fallas"], "fallas_despues": d["fallas"],
        "filas_antes": a["filas_afectadas"], "filas_despues": d["filas_afectadas"],
        "mejora": m["mejora_indice"], "reduccion": m["reduccion_filas_pct"],
    }


M = medicion()


def miles(n: int) -> str:
    """3656 -> "3.656". El punto es el separador de miles en los 3 idiomas."""
    return f"{int(n):,}".replace(",", ".")


# ── piezas visuales ─────────────────────────────────────────────────────
PANEL_W, PANEL_H = 470, 330


def _panel(d: ImageDraw.ImageDraw, x: int, y: int, titulo: str, color,
           filas: list[tuple[str, str]], destacado: str) -> None:
    """Una columna del comparativo: título de color, número grande y filas."""
    d.rounded_rectangle([x, y, x + PANEL_W, y + PANEL_H], radius=18,
                        fill=(15, 33, 53), outline=color, width=2)
    d.text((x + 26, y + 22), titulo, font=font(21), fill=color)
    d.text((x + 26, y + 58), destacado, font=font(72), fill=color)
    yy = y + 152
    for etiqueta, valor in filas:
        d.text((x + 26, yy), etiqueta, font=font(16, False), fill=MUTED)
        vw = d.textlength(valor, font=font(19))
        d.text((x + PANEL_W - 26 - vw, yy - 2), valor, font=font(19), fill=INK)
        yy += 38


def _flecha(d: ImageDraw.ImageDraw, cx: int, cy: int, alpha: float) -> None:
    """Flecha ámbar entre los dos paneles: marca la dirección del cambio."""
    if alpha <= 0:
        return
    largo = int(46 * ease(alpha))
    d.line([cx - largo, cy, cx + largo, cy], fill=AMBER, width=6)
    d.polygon([(cx + largo + 22, cy), (cx + largo - 4, cy - 16),
               (cx + largo - 4, cy + 16)], fill=AMBER)


_TXT = {
    "antes": {"es": "ANTES", "en": "BEFORE", "pt": "ANTES"},
    "despues": {"es": "DESPUÉS", "en": "AFTER", "pt": "DEPOIS"},
    "reglas": {"es": "Reglas en verde", "en": "Rules passing", "pt": "Regras em verde"},
    "fallas": {"es": "Reglas que fallan", "en": "Rules failing", "pt": "Regras que falham"},
    "filas": {"es": "Filas con problemas", "en": "Rows with problems",
              "pt": "Linhas com problemas"},
    "indice": {"es": "Índice de calidad", "en": "Quality index",
               "pt": "Índice de qualidade"},
    "h_problema": {"es": "El dato en el que nadie confía",
                   "en": "The data nobody trusts",
                   "pt": "O dado em que ninguém confia"},
    "s_problema": {
        "es": "Decisiones tomadas sobre una base que nadie auditó.",
        "en": "Decisions made on a base nobody ever audited.",
        "pt": "Decisões tomadas sobre uma base que ninguém auditou."},
    "h_cierre": {"es": "El mismo dato, gobernado", "en": "The same data, governed",
                 "pt": "O mesmo dado, governado"},
    "medido": {
        "es": "Medido por el motor del programa · reproducible en tu PC",
        "en": "Measured by the program's own engine · reproducible on your PC",
        "pt": "Medido pelo motor do programa · reproduzível no seu PC"},
    "cta": {"es": "PROBALO CON TUS PROPIOS DATOS",
            "en": "TRY IT WITH YOUR OWN DATA",
            "pt": "TESTE COM SEUS PRÓPRIOS DADOS"},
}


def _t(clave: str, lang: str) -> str:
    return _TXT[clave][lang]


# ── escenas ─────────────────────────────────────────────────────────────
def _escena_problema(p: float, lang: str):
    img = base_frame()
    d = ImageDraw.Draw(img)
    center_text(d, 168, _t("h_problema", lang), font(50), INK)
    if p > 0.22:
        center_text(d, 244, _t("s_problema", lang), font(24, False), MUTED)
    if p > 0.42:
        _panel(d, (W - PANEL_W) // 2, 310, _t("antes", lang), RED,
               [(_t("reglas", lang), f"{M['ok_antes']} / {M['total']}"),
                (_t("fallas", lang), str(M["fallas_antes"])),
                (_t("filas", lang), miles(M["filas_antes"]))],
               f"{M['indice_antes']:.1f}")
        d.text(((W - PANEL_W) // 2 + 26, 310 + 132), _t("indice", lang),
               font=font(15, False), fill=FAINT)
    return img


def _escena_comparativo(p: float, lang: str):
    img = base_frame()
    d = ImageDraw.Draw(img)
    center_text(d, 62, _t("h_cierre", lang), font(42), INK)
    izq, der = 78, W - 78 - PANEL_W
    _panel(d, izq, 168, _t("antes", lang), RED,
           [(_t("reglas", lang), f"{M['ok_antes']} / {M['total']}"),
            (_t("fallas", lang), str(M["fallas_antes"])),
            (_t("filas", lang), miles(M["filas_antes"]))],
           f"{M['indice_antes']:.1f}")
    _flecha(d, W // 2, 300, min(1.0, p / 0.35))
    # El panel "después" entra después: el orden cuenta la historia.
    if p > 0.3:
        _panel(d, der, 168, _t("despues", lang), GREEN,
               [(_t("reglas", lang), f"{M['ok_despues']} / {M['total']}"),
                (_t("fallas", lang), str(M["fallas_despues"])),
                (_t("filas", lang), miles(M["filas_despues"]))],
               f"{M['indice_despues']:.1f}")
    if p > 0.62:
        center_text(d, 540, f"+{M['mejora']:.1f} pts   ·   −{M['reduccion']}% "
                    f"{_t('filas', lang).lower()}", font(30), AMBER)
    if p > 0.8:
        center_text(d, 596, _t("medido", lang), font(19, False), FAINT)
    return img


def _escena_cierre(p: float, lang: str):
    img = base_frame()
    d = ImageDraw.Draw(img)
    center_text(d, 196, "MV Data Governance", font(56), INK)
    if p > 0.2:
        center_text(d, 288, f"{M['indice_antes']:.1f}  →  {M['indice_despues']:.1f}",
                    font(64), AMBER)
    if p > 0.42:
        center_text(d, 384, _t("medido", lang), font(22, False), MUTED)
    if p > 0.62:
        badge(d, W // 2, 470, _t("cta", lang), font(21))
    if p > 0.78:
        center_text(d, 552, SITIO, font(24, False), FAINT)
    return img


def _por_idioma(fn, lang: str):
    """Las escenas del pipeline reciben solo `p`; el idioma va cerrado acá."""
    return lambda p: fn(p, lang)


def escenas(lang: str) -> list:
    return [
        (_por_idioma(_escena_problema, lang), 7.0, _NARRACION[0]),
        (_por_idioma(_escena_comparativo, lang), 12.0, _NARRACION[1]),
        (_por_idioma(_escena_cierre, lang), 7.0, _NARRACION[2]),
    ]


# Las cifras se interpolan de la medición: la voz dice lo mismo que la
# pantalla, y ninguna de las dos se puede desincronizar del motor.
_NARRACION = [
    {
        "es": "Así llegan los datos de una empresa sin gobierno: "
              f"{M['fallas_antes']} de {M['total']} reglas de calidad fallando, "
              f"y {miles(M['filas_antes'])} filas con problemas. "
              "Sobre esa base se toman decisiones todos los días.",
        "en": "This is how a company's data arrives without governance: "
              f"{M['fallas_antes']} of {M['total']} quality rules failing, "
              f"and {miles(M['filas_antes'])} rows with problems. "
              "Decisions are made on that base every single day.",
        "pt": "É assim que chegam os dados de uma empresa sem governança: "
              f"{M['fallas_antes']} de {M['total']} regras de qualidade falhando, "
              f"e {miles(M['filas_antes'])} linhas com problemas. "
              "É sobre essa base que se decide todos os dias.",
    },
    {
        "es": "Los mismos datos, gobernados con MV Data Governance: el índice de "
              f"calidad pasa de {M['indice_antes']:.1f} a {M['indice_despues']:.1f}, "
              f"las reglas en verde van de {M['ok_antes']} a {M['ok_despues']}, y las "
              f"filas con problemas bajan de {miles(M['filas_antes'])} a "
              f"{miles(M['filas_despues'])}: un {M['reduccion']} por ciento menos.",
        "en": "The same data, governed with MV Data Governance: the quality index "
              f"goes from {M['indice_antes']:.1f} to {M['indice_despues']:.1f}, rules "
              f"passing go from {M['ok_antes']} to {M['ok_despues']}, and rows with "
              f"problems drop from {miles(M['filas_antes'])} to "
              f"{miles(M['filas_despues'])}: {M['reduccion']} percent fewer.",
        "pt": "Os mesmos dados, governados com MV Data Governance: o índice de "
              f"qualidade vai de {M['indice_antes']:.1f} a {M['indice_despues']:.1f}, "
              f"as regras em verde vão de {M['ok_antes']} a {M['ok_despues']}, e as "
              f"linhas com problemas caem de {miles(M['filas_antes'])} para "
              f"{miles(M['filas_despues'])}: {M['reduccion']} por cento a menos.",
    },
    {
        "es": "No es una promesa: lo mide el mismo motor de reglas que vas a correr "
              "en tu PC, sobre tus propios datos, sin que salgan de tu empresa.",
        "en": "This is not a promise: it is measured by the same rule engine you "
              "will run on your own PC, on your own data, without it ever leaving "
              "your company.",
        "pt": "Não é uma promessa: é medido pelo mesmo motor de regras que você vai "
              "rodar no seu PC, sobre os seus dados, sem que eles saiam da sua "
              "empresa.",
    },
]


def build() -> list[tuple[str, str, bool]]:
    os.makedirs(VIDEO_DIR, exist_ok=True)
    os.makedirs(LANDING_DIR, exist_ok=True)
    salidas = []
    for lang in LANGS:
        tmpdir = tempfile.mkdtemp(prefix=f"mvdg_ad_{lang}_")
        try:
            ruta, con_voz = build_one(lang, tmpdir, scenes=escenas(lang), nombre=NOMBRE)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
        shutil.copyfile(ruta, os.path.join(LANDING_DIR, os.path.basename(ruta)))
        salidas.append((lang, ruta, con_voz))
    return salidas


if __name__ == "__main__":
    print(f"Medición del motor: índice {M['indice_antes']} -> {M['indice_despues']} "
          f"(+{M['mejora']}) · filas {M['filas_antes']} -> {M['filas_despues']} "
          f"(-{M['reduccion']}%)")
    for lang, ruta, con_voz in build():
        mb = os.path.getsize(ruta) / 1e6
        voz = "con voz" if con_voz else "SIN voz (falta modelo Piper)"
        print(f"[{lang}] {os.path.basename(ruta)} ({mb:.1f} MB) · {voz} "
              "· copiado a landing/video/")
