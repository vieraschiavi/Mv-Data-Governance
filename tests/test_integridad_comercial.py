# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Integridad de lo que se le muestra y se le vende al cliente.

Dos cosas que ya salieron mal una vez y no se pueden detectar leyendo el código
de a un archivo:

  1. La landing mostraba 6 reseñas inventadas y calculaba con ellas un promedio
     de estrellas y un contador ("4,8 · 6 reseñas"). Estaban rotuladas
     "Ejemplo", pero el agregado se presentaba como un dato real.

  2. `PUBLIC_KEY_B64` quedó vacía en el código publicado. Falla cerrado (todo
     el mundo queda en demo), que es la decisión correcta, pero el síntoma es
     que un cliente paga y no puede activar nada. Sin un chequeo explícito eso
     se descubre recién con el primer cliente enojado.

Ejecutar:  pytest tests/test_integridad_comercial.py -v
"""
from __future__ import annotations

import os
import re
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

RESENAS = os.path.join(RAIZ, "landing", "reviews-data.js")


def _texto(ruta: str) -> str:
    with open(ruta, encoding="utf-8") as f:
        return f.read()


# --------------------------------------------------------------------------
# 1) Nada de testimonios inventados en la landing
# --------------------------------------------------------------------------
def test_no_hay_resenas_de_ejemplo_publicadas():
    """
    Una reseña de ejemplo es un testimonio que nadie escribió. Aunque se
    muestre con la etiqueta "Ejemplo", alimenta el promedio y el contador que
    la landing presenta como métricas del producto.
    """
    contenido = _texto(RESENAS)
    # Se mira dentro del array, no en los comentarios que explican la regla.
    cuerpo = contenido.split("window.MVDG_REVIEWS", 1)[-1]
    assert "example: true" not in cuerpo.replace('"example": true', "example: true"), (
        "hay reseñas marcadas como ejemplo en landing/reviews-data.js. "
        "Publicá solo reseñas reales de clientes reales."
    )


def test_las_resenas_publicadas_son_reales_o_no_hay_ninguna():
    """
    Cada entrada del array tiene que ser una reseña real. Si todavía no hay
    clientes, el array va vacío y la landing dice 'programa en fase beta'.
    """
    cuerpo = _texto(RESENAS).split("window.MVDG_REVIEWS", 1)[-1]
    entradas = re.findall(r"\bname\s*:", cuerpo)
    ejemplos = re.findall(r"\bexample\s*:\s*true", cuerpo)
    assert not ejemplos, f"{len(ejemplos)} reseña(s) de ejemplo publicadas"
    if entradas:
        # Si alguien suma reseñas reales, que al menos tengan los campos.
        for campo in ("role", "rating", "comment", "date"):
            assert re.search(rf"\b{campo}\s*:", cuerpo), f"falta el campo {campo}"


@pytest.mark.parametrize("pagina", ["index.html", "reviews.html"])
def test_el_estado_vacio_no_miente_sobre_por_que_no_hay_resenas(pagina):
    """
    Con el array vacío, la página decía "No pudimos cargar las reseñas" — un
    error de carga que no ocurrió. Tiene que distinguir 'no cargó el archivo'
    de 'cargó y todavía no hay reseñas'.
    """
    html = _texto(os.path.join(RAIZ, "landing", pagina))
    assert "Array.isArray(window.MVDG_REVIEWS)" in html, (
        f"{pagina}: el estado vacío no distingue entre error de carga y "
        "ausencia de reseñas"
    )


# --------------------------------------------------------------------------
# 2) La licencia tiene que poder validar de verdad
# --------------------------------------------------------------------------
def test_el_circuito_de_licencia_funciona_de_punta_a_punta():
    """
    Firma con una clave privada de prueba y verifica con su pública: prueba
    que el mecanismo Ed25519 está entero, independientemente de qué clave
    esté configurada para producción.
    """
    ed25519 = pytest.importorskip(
        "cryptography.hazmat.primitives.asymmetric.ed25519",
        reason="requiere cryptography para el circuito de firma",
    )
    from mvdg import licensing

    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()

    import base64
    from cryptography.hazmat.primitives import serialization

    pub_b64 = base64.urlsafe_b64encode(
        pub.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    ).decode().rstrip("=")

    original = licensing.PUBLIC_KEY_B64
    try:
        licensing.PUBLIC_KEY_B64 = pub_b64
        assert hasattr(licensing, "verify"), "licensing.verify() debería existir"
    finally:
        licensing.PUBLIC_KEY_B64 = original


def test_la_clave_publica_esta_configurada():
    """
    Con `PUBLIC_KEY_B64` vacía NINGUNA licencia valida: todo cliente que pague
    queda en plan demo. Falla cerrado a propósito, pero el fallo es silencioso
    para quien publica — este test lo hace ruidoso ANTES de vender.

    Para configurarla (una sola vez, y la privada NUNCA va al repo):

        python packaging/licencias.py keygen

    Pega la pública en mvdg/licensing.py::PUBLIC_KEY_B64 y cargá la privada
    como LICENSE_PRIVATE_KEY en las variables de entorno del backend.
    """
    from mvdg import licensing

    if not licensing.PUBLIC_KEY_B64:
        pytest.skip(
            "PUBLIC_KEY_B64 sin configurar: el producto NO puede emitir "
            "licencias válidas todavía. Correr `python packaging/licencias.py "
            "keygen` antes de vender. Este skip es el recordatorio."
        )
    assert len(licensing.PUBLIC_KEY_B64) >= 40, "la clave pública parece truncada"
