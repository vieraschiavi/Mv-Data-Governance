"""
MV Data Governance · Datos de demostración 100% sintéticos.

Genera de forma determinística (semilla fija) cuatro datasets con problemas
de calidad inyectados a propósito, para que el motor de reglas tenga algo
real que detectar: nulos, duplicados, emails inválidos, montos negativos,
categorías inconsistentes y fechas viejas.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 42
TODAY = pd.Timestamp("2026-07-01")  # fecha de referencia fija (demo reproducible)

_FIRST = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Fabio", "Gina", "Hugo",
          "Iris", "Joao", "Karen", "Luis", "Marta", "Nico", "Olga", "Pablo",
          "Rita", "Sofia", "Tomas", "Vera"]
_LAST = ["Silva", "Gomez", "Pereira", "Rodriguez", "Santos", "Fernandez",
         "Costa", "Martinez", "Oliveira", "Lopez", "Souza", "Diaz",
         "Almeida", "Torres", "Ribeiro", "Vargas"]
_COUNTRIES = ["UY", "AR", "BR", "CL", "PY"]
_SEGMENTS = ["Retail", "Corporate", "SMB"]
_CATEGORIES = ["Electrónica", "Hogar", "Deportes", "Moda", "Alimentos"]
_CHANNELS = ["web", "tienda", "app", "mayorista"]


def _rng() -> np.random.Generator:
    return np.random.default_rng(SEED)


def make_customers(n: int = 800) -> pd.DataFrame:
    rng = _rng()
    ids = np.arange(1, n + 1)
    first = rng.choice(_FIRST, n)
    last = rng.choice(_LAST, n)
    emails = np.array([f"{f.lower()}.{l.lower()}{i}@mail.com"
                       for f, l, i in zip(first, last, ids)], dtype=object)
    df = pd.DataFrame({
        "customer_id": ids,
        "full_name": [f"{f} {l}" for f, l in zip(first, last)],
        "email": emails,
        "document_id": [f"{rng.integers(10_000_000, 60_000_000)}" for _ in ids],
        "country": rng.choice(_COUNTRIES, n, p=[0.35, 0.25, 0.2, 0.12, 0.08]),
        "segment": rng.choice(_SEGMENTS, n, p=[0.6, 0.15, 0.25]),
        "signup_date": TODAY - pd.to_timedelta(rng.integers(30, 1500, n), unit="D"),
        "birth_date": TODAY - pd.to_timedelta(rng.integers(18 * 365, 80 * 365, n), unit="D"),
    })
    # --- problemas inyectados ---
    bad = rng.choice(n, 32, replace=False)
    df.loc[bad[:12], "email"] = None                       # nulos
    df.loc[bad[12:22], "email"] = "sin-arroba.mail.com"    # inválidos
    df.loc[bad[22:], "segment"] = "retail "                # inconsistencia de categoría
    dupes = df.sample(8, random_state=SEED)                # duplicados exactos de id
    df = pd.concat([df, dupes], ignore_index=True)
    return df


def make_products(n: int = 120) -> pd.DataFrame:
    rng = _rng()
    df = pd.DataFrame({
        "product_id": np.arange(1, n + 1),
        "product_name": [f"Producto {i:03d}" for i in range(1, n + 1)],
        "category": rng.choice(_CATEGORIES, n),
        "unit_price": np.round(rng.uniform(5, 900, n), 2),
        "active": rng.choice([True, False], n, p=[0.85, 0.15]),
    })
    bad = rng.choice(n, 6, replace=False)
    df.loc[bad[:3], "unit_price"] = -df.loc[bad[:3], "unit_price"]  # precios negativos
    df.loc[bad[3:], "category"] = None                              # categoría nula
    return df


def make_sales(n: int = 5000, n_customers: int = 800, n_products: int = 120) -> pd.DataFrame:
    rng = _rng()
    df = pd.DataFrame({
        "sale_id": np.arange(1, n + 1),
        "customer_id": rng.integers(1, n_customers + 1, n),
        "product_id": rng.integers(1, n_products + 1, n),
        "sale_date": TODAY - pd.to_timedelta(rng.integers(0, 365, n), unit="D"),
        "quantity": rng.integers(1, 8, n),
        "amount": np.round(rng.gamma(2.2, 90, n), 2),
        "channel": rng.choice(_CHANNELS, n, p=[0.45, 0.3, 0.2, 0.05]),
    })
    bad = rng.choice(n, 120, replace=False)
    df.loc[bad[:40], "amount"] = None                     # montos nulos
    df.loc[bad[40:70], "amount"] = -np.abs(df.loc[bad[40:70], "amount"].fillna(50))
    df.loc[bad[70:90], "customer_id"] = 99_999            # FK huérfana
    df.loc[bad[90:], "channel"] = "WEB"                   # inconsistencia de dominio
    return df


def make_payments(n: int = 3200) -> pd.DataFrame:
    rng = _rng()
    df = pd.DataFrame({
        "payment_id": np.arange(1, n + 1),
        "sale_id": rng.integers(1, 5001, n),
        "payment_date": TODAY - pd.to_timedelta(rng.integers(0, 700, n), unit="D"),
        "amount_paid": np.round(rng.gamma(2.0, 85, n), 2),
        "method": rng.choice(["tarjeta", "transferencia", "efectivo"], n, p=[0.55, 0.3, 0.15]),
        "status": rng.choice(["ok", "pendiente", "rechazado"], n, p=[0.86, 0.09, 0.05]),
    })
    bad = rng.choice(n, 50, replace=False)
    df.loc[bad[:25], "method"] = None
    df.loc[bad[25:], "payment_date"] = TODAY - pd.Timedelta(days=900)  # datos viejos
    return df


def load_demo_tables() -> dict[str, pd.DataFrame]:
    """Devuelve los cuatro datasets de la demo, siempre idénticos (semilla fija)."""
    return {
        "dim_customers": make_customers(),
        "dim_products": make_products(),
        "fct_sales": make_sales(),
        "fct_payments": make_payments(),
    }
