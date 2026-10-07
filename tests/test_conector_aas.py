# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""«Mis datos» desde Azure Analysis Services (el MDW): el conector de la suite, simulado."""
from __future__ import annotations

import os
import sys
import types
from dataclasses import dataclass, field

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mvdg import conector_aas as C  # noqa: E402
from mvdg.i18n import LANGS, t  # noqa: E402

SRV = "asazure://region.asazure.windows.net/servidor"


@dataclass
class _Tabla:
    nombre: str
    datos: pd.DataFrame


@dataclass
class _Lectura:
    con_datos: tuple
    avisos: tuple = ()


@dataclass
class _AS:
    """El conector de la suite (adium_allinone.analysis_services), simulado."""
    faltan: list = field(default_factory=list)
    llamadas: list = field(default_factory=list)

    def librerias_faltantes(self):
        return self.faltan

    def diagnostico_faltantes(self, faltan):
        return "pip install " + " ".join(faltan)

    def usar_usuario(self, servidor, usuario, clave):
        if usuario and "@" not in usuario:
            raise ValueError("El usuario tiene que ser tu mail de la empresa.")
        self.llamadas.append(("usuario", usuario))

    def usar_ventana(self, servidor, si):
        self.llamadas.append(("ventana", si))

    def tablas_del_modelo(self, servidor, modelo, token=""):
        return ["Venta", "Producto"]

    def leer(self, servidor, modelo, token="", tablas=None, limite=None):
        self.llamadas.append(("leer", tuple(tablas or ()), limite))
        todas = {"Venta": pd.DataFrame({"Pais": ["AR", "CL"], "USD": [10.0, 20.0]}),
                 "Producto": pd.DataFrame({"SKU": ["A", "B"]})}
        return _Lectura(tuple(_Tabla(n, d) for n, d in todas.items() if not tablas or n in tablas),
                        ("tope aplicado",))


def test_validaciones_con_su_clave_de_i18n():
    for args, codigo in [(("http://x", "M", "usuario", "a@b", "c"), "aas_err_servidor"),
                         ((SRV, "", "usuario", "a@b", "c"), "aas_err_modelo"),
                         ((SRV, "M", "usuario", "", ""), "aas_err_usuario"),
                         ((SRV, "M", "token", "", "", ""), "aas_err_token"),
                         ((SRV, "M", "otra"), "aas_err_auth")]:
        with pytest.raises(C.ErrorAAS) as e:
            C.validar(*args)
        assert e.value.codigo == codigo
    assert C.validar(f" {SRV} ", " Modelo ", "ventana") == (SRV, "Modelo")
    for codigo in ("aas_err_servidor", "aas_err_suelto", "aas_err_librerias", "aas_err_vacio"):
        assert all(t(codigo, lang) != codigo for lang in LANGS)          # traducido en los tres idiomas


def test_lee_las_tablas_con_el_conector_de_la_suite():
    AS = _AS()
    assert C.listar_tablas(SRV, "MDW", usuario="persona@empresa.com", clave="x", AS=AS) == ["Venta", "Producto"]
    datos, avisos = C.leer(SRV, "MDW", usuario="persona@empresa.com", clave="x", tablas=["Venta"], limite=500, AS=AS)
    assert list(datos) == ["Venta"] and len(datos["Venta"]) == 2 and avisos == ["tope aplicado"]
    assert ("leer", ("Venta",), 500) in AS.llamadas and ("usuario", "persona@empresa.com") in AS.llamadas


def test_errores_que_explican_que_hacer():
    with pytest.raises(C.ErrorAAS) as e:
        C.leer(SRV, "MDW", usuario="a@b.com", clave="x", AS=_AS(faltan=["pythonnet", "pyadomd"]))
    assert e.value.codigo == "aas_err_librerias" and "pythonnet" in e.value.detalle
    with pytest.raises(C.ErrorAAS) as e:
        C.leer(SRV, "MDW", usuario="sin-arroba", clave="x", AS=_AS())
    assert e.value.codigo == "aas_err_conector" and "mail" in e.value.detalle


def test_suelto_dice_que_se_abre_desde_la_suite(monkeypatch):
    monkeypatch.setitem(sys.modules, "adium_allinone", None)
    assert C.motor_suite() is None
    with pytest.raises(C.ErrorAAS) as e:
        C.listar_tablas(SRV, "MDW", auth="ventana")
    assert e.value.codigo == "aas_err_suelto"


def test_mis_datos_ofrece_analysis_services_y_las_tablas_quedan_gobernadas(monkeypatch, tmp_path):
    """«No aparece Azure Analysis Services» en «Mis datos»: ahora es una fuente más, y lo traído se gobierna."""
    from streamlit.testing.v1 import AppTest
    paquete = types.ModuleType("adium_allinone")
    paquete.analysis_services = _AS()
    monkeypatch.setitem(sys.modules, "adium_allinone", paquete)
    monkeypatch.setitem(sys.modules, "adium_allinone.analysis_services", paquete.analysis_services)
    monkeypatch.setenv("MVDG_DATA_DIR", str(tmp_path))
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    at = AppTest.from_file(os.path.join(raiz, "app", "app.py"), default_timeout=300)
    at.run()
    fuente = [r for r in at.radio if r.key == "pr_source"][0]
    assert "Azure Analysis Services (MDW)" in fuente.options
    at = fuente.set_value("aas").run()
    at = [x for x in at.text_input if x.key == "aas_srv"][0].set_value(SRV).run()
    at = [x for x in at.text_input if x.key == "aas_mod"][0].set_value("MDW").run()
    at = [x for x in at.text_input if x.key == "aas_usr"][0].set_value("persona@empresa.com").run()
    at = [x for x in at.text_input if x.key == "aas_clave"][0].set_value("x").run()
    at = [b for b in at.button if b.key == "aas_ver"][0].click().run()
    assert [m for m in at.multiselect if m.key == "aas_sel"][0].options == ["Venta", "Producto"]
    at = [b for b in at.button if b.key == "aas_conectar"][0].click().run()
    assert not at.exception, [str(e) for e in at.exception]
    assert {"Venta", "Producto"} <= set(at.session_state["mvdg_user_datasets"])
    assert any("2 tabla(s)" in s.value for s in at.success)
