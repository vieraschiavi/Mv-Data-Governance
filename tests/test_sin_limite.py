"""Sin tope de filas por defecto en la carga de datos.

Pedido del dueño: "¿Hay límite de filas? 100.000 por tabla por defecto...
debe [ser] sin límite de tamaño cada módulo." Estos tests fijan tres cosas,
con datos 100 % sintéticos:

1. Por defecto se lee TODO: una tabla/CSV de 150.000 filas (más que el viejo
   default de 100.000) llega entera.
2. Con un tope explícito se recorta, y el recorte se avisa con el total real
   (COUNT) — nunca un recorte mudo.
3. Tope 0 o None = todo.
"""
from __future__ import annotations

import os
import sqlite3
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mvdg import connectors as C  # noqa: E402
from mvdg import dataeng, fabric  # noqa: E402

FILAS = 150_000          # más que el viejo default de 100.000


@pytest.fixture(scope="module")
def sqlite_grande(tmp_path_factory):
    ruta = tmp_path_factory.mktemp("sinlimite") / "grande.db"
    con = sqlite3.connect(ruta)
    con.execute("CREATE TABLE ventas (id INTEGER, monto REAL)")
    con.executemany("INSERT INTO ventas VALUES (?, ?)",
                    ((i, i * 1.5) for i in range(FILAS)))
    con.commit()
    con.close()
    return {"engine": "sqlite", "database": str(ruta), "host": "", "port": None,
            "user": "", "extra": ""}


@pytest.fixture(scope="module")
def csv_grande():
    df = pd.DataFrame({"id": range(FILAS), "cliente": [f"c{i % 97}" for i in range(FILAS)]})
    return df.to_csv(index=False).encode("utf-8")


# ─────────────────────────── 1. por defecto, todo ───────────────────────────
def test_los_defaults_no_tienen_tope():
    assert C.MAX_ROWS == 0
    assert fabric.MAX_FILAS == 0
    assert dataeng.TOPE_FILAS == 0
    assert dataeng.MUESTRA_SQL_DEFECTO == 0


def test_sqlite_de_150k_filas_se_lee_entera_por_defecto(sqlite_grande):
    assert len(C.load_table(sqlite_grande, "ventas")) == FILAS
    assert len(C.run_query(sqlite_grande, "SELECT * FROM ventas")) == FILAS


def test_csv_de_150k_filas_se_lee_entero_por_defecto(csv_grande):
    tablas = dataeng.leer_archivo_bytes("grande.csv", csv_grande)
    df = next(iter(tablas.values()))
    assert len(df) == FILAS


def test_el_analisis_no_recorta_por_defecto():
    """`analizar_tabla` cortaba en 200.000 filas sin que nadie lo pidiera."""
    df = pd.DataFrame({"id": range(250_000)})
    res = dataeng.analizar_tabla("t", df, con_features=False)
    assert res["filas_originales"] == 250_000
    assert res["muestreado"] is False
    assert res["perfil"]["filas"] == 250_000


# ──────────────────── 2. tope explícito: recorta y avisa ────────────────────
def test_tope_explicito_recorta_y_avisa_el_total_real(sqlite_grande):
    df = C.load_table(sqlite_grande, "ventas", 1_000)
    assert len(df) == 1_000
    assert C.aviso_recorte(sqlite_grande, df, 1_000, table="ventas") == FILAS

    dq = C.run_query(sqlite_grande, "SELECT * FROM ventas WHERE id < 5000;", 1_000)
    assert len(dq) == 1_000
    assert C.aviso_recorte(sqlite_grande, dq, 1_000,
                           sql="SELECT * FROM ventas WHERE id < 5000;") == 5_000


def test_tope_que_no_recorta_no_avisa(sqlite_grande):
    df = C.run_query(sqlite_grande, "SELECT * FROM ventas WHERE id < 10", 1_000)
    assert len(df) == 10
    assert C.aviso_recorte(sqlite_grande, df, 1_000,
                           sql="SELECT * FROM ventas WHERE id < 10") is None
    # tope igual al total exacto: vinieron N filas pero no se cortó nada
    df = C.run_query(sqlite_grande, "SELECT * FROM ventas WHERE id < 10", 10)
    assert C.aviso_recorte(sqlite_grande, df, 10,
                           sql="SELECT * FROM ventas WHERE id < 10") is None


def test_el_conteo_respeta_la_validacion_de_solo_lectura(sqlite_grande):
    with pytest.raises(ValueError):
        C.total_filas(sqlite_grande, sql="DELETE FROM ventas")


def test_tope_explicito_en_csv_y_analisis(csv_grande):
    tablas = dataeng.leer_archivo_bytes("grande.csv", csv_grande, muestra=500)
    assert len(next(iter(tablas.values()))) == 500
    res = dataeng.analizar_tabla("t", pd.DataFrame({"id": range(2_000)}),
                                 con_features=False, muestra=500)
    assert res["muestreado"] is True and res["filas_originales"] == 2_000


# ───────────────────────────── 3. 0/None = todo ─────────────────────────────
@pytest.mark.parametrize("tope", [0, None])
def test_tope_cero_o_none_es_todo(sqlite_grande, tope):
    df = C.load_table(sqlite_grande, "ventas", tope)
    assert len(df) == FILAS
    assert C.aviso_recorte(sqlite_grande, df, tope, table="ventas") is None
    assert len(C.run_query(sqlite_grande, "SELECT * FROM ventas", tope)) == FILAS


# ─────────────────────────────── Fabric ─────────────────────────────────────
class _Tabla:
    def __init__(self, pdf):
        self._pdf = pdf

    def limit(self, n):
        return _Tabla(self._pdf.head(n))

    def toPandas(self):                          # noqa: N802 - API de Spark
        return self._pdf.copy()

    def count(self):
        return len(self._pdf)


class _Spark:
    def __init__(self, tablas):
        self._tablas = tablas
        self.catalog = type("C", (), {"listTables": lambda _s: [
            type("T", (), {"name": n})() for n in tablas]})()
        self.read = self

    def table(self, nombre):
        return _Tabla(self._tablas[nombre])


def test_fabric_sin_tope_por_defecto_y_con_tope_avisa_el_total():
    spark = _Spark({"Grande": pd.DataFrame({"id": range(FILAS), "v": 1})})
    tablas, muestreadas = fabric.leer_tablas(spark=spark)
    assert len(tablas["Grande"]) == FILAS and muestreadas == {}

    r = fabric.gobernar_lakehouse(spark=spark, muestra=1_000, escribir=False)
    assert r["muestreadas"] == {"Grande": 1_000}
    assert r["filas_totales"] == {"Grande": FILAS}

    r = fabric.gobernar_lakehouse(spark=spark, muestra=None, escribir=False)
    assert r["muestreadas"] == {} and r["filas_totales"] == {}
    assert r["tablas_leidas"] == {"Grande": FILAS}


# ────────────────────────────────── i18n ────────────────────────────────────
def test_textos_nuevos_en_los_tres_idiomas():
    from mvdg.i18n import _T as STRINGS
    for clave in ("db_recorte", "db_recorte_sin_total", "de_db_recorte", "db_limit"):
        assert set(STRINGS[clave]) >= {"es", "en", "pt"}, clave
    txt = STRINGS["db_recorte"]["es"].format(n=1000, total=FILAS)
    assert "150,000" in txt and "1,000" in txt
