"""
MV Data Governance · Master Data Management (MDM): duplicados y golden record.

El motor de calidad (``quality.py``) mide si UNA fila está bien. Este módulo
cubre la otra mitad clásica del MDM: si dos o más filas representan, en
realidad, la MISMA entidad (cliente, producto, proveedor) con datos
levemente distintos — y si es así, cuál sería el "golden record" que las
unifica.

Enfoque: matching por reglas ponderadas (no machine learning) — cada señal
de coincidencia (ID exacto, email exacto, nombre similar…) suma una
confianza, y las filas por encima de un umbral se agrupan en un cluster
(union-find). 100% local, sin dependencias nuevas: usa ``difflib`` de la
librería estándar para similitud de texto.

Advertencia real, encontrada probando contra el dataset de demo
(``dim_customers``, 808 filas): matchear solo por nombre produce muchos
falsos positivos — nombres comunes ("Ana Costa", "Ana Ribeiro"...) se
repiten legítimamente entre personas distintas en cualquier base de
clientes real. Por eso, en las reglas por defecto, el nombre solo no
alcanza el umbral — hace falta que coincida ADEMÁS con un identificador
fuerte (documento, email) para que el cluster se considere un duplicado
real. Este mismo dataset trae 8 colisiones reales de ``document_id`` y 17
de ``email`` — sin inyectar nada a propósito — que sirven de caso de
prueba honesto.
"""
from __future__ import annotations

import difflib
from dataclasses import dataclass, field

import pandas as pd


@dataclass
class MatchRule:
    column: str
    weight: float
    kind: str = "exact"          # "exact" | "fuzzy"
    fuzzy_threshold: float = 0.85  # solo aplica si kind == "fuzzy"


@dataclass
class DuplicateCluster:
    row_indices: list
    confidence: float
    matched_on: list[str] = field(default_factory=list)


_MAX_PAIRS_WITHOUT_BLOCKING = 5000  # ~100 filas sin blocking; con blocking, mucho más


def _sim(a, b) -> float:
    if pd.isna(a) or pd.isna(b):
        return 0.0
    a, b = str(a).strip().lower(), str(b).strip().lower()
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def _pair_score(row_a: dict, row_b: dict, rules: list[MatchRule]) -> tuple[float, list[str]]:
    """``row_a``/``row_b`` son dicts planos (no ``pd.Series``) — evita el
    overhead de ``.loc``/``.get`` de pandas en el hot path de la comparación
    por pares, que domina el tiempo total cuando hay miles de pares."""
    total_weight = sum(r.weight for r in rules) or 1.0
    score = 0.0
    matched: list[str] = []
    for r in rules:
        va, vb = row_a.get(r.column), row_b.get(r.column)
        if r.kind == "exact":
            if pd.notna(va) and pd.notna(vb) and str(va).strip().lower() == str(vb).strip().lower():
                score += r.weight
                matched.append(r.column)
        else:
            sim = _sim(va, vb)
            if sim >= r.fuzzy_threshold:
                score += r.weight * sim
                matched.append(r.column)
    return score / total_weight, matched


def _candidate_pairs(df: pd.DataFrame, block_column: str | None):
    idx = df.index.tolist()
    if block_column and block_column in df.columns:
        for _, members in df.groupby(block_column).groups.items():
            members = list(members)
            for a in range(len(members)):
                for b in range(a + 1, len(members)):
                    yield members[a], members[b]
    else:
        n = len(idx)
        n_pairs = n * (n - 1) // 2
        if n_pairs > _MAX_PAIRS_WITHOUT_BLOCKING:
            raise ValueError(
                f"{len(df):,} filas sin 'block_column' generan {n_pairs:,} pares a comparar — "
                f"demasiado para hacerlo bien. Pasá un block_column (ej. país, categoría) para "
                f"acotar la comparación a filas del mismo grupo (blocking, el enfoque estándar "
                f"de MDM para escalar).")
        for a in range(n):
            for b in range(a + 1, n):
                yield idx[a], idx[b]


def find_duplicate_clusters(df: pd.DataFrame, rules: list[MatchRule],
                            min_confidence: float = 0.5,
                            block_column: str | None = None) -> list[DuplicateCluster]:
    """Encuentra clusters de filas que probablemente representen la misma
    entidad, comparando pares según ``rules`` (ponderadas). Con
    ``block_column``, solo se comparan filas que coincidan en esa columna
    (blocking clásico de MDM) — necesario para datasets grandes."""
    parent = {i: i for i in df.index}

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    needed_cols = [r.column for r in rules if r.column in df.columns]
    rows = df[needed_cols].to_dict("index")   # una sola conversión, evita .loc repetido

    pair_info: dict[tuple, tuple[float, list[str]]] = {}
    for i, j in _candidate_pairs(df, block_column):
        score, matched = _pair_score(rows[i], rows[j], rules)
        if score >= min_confidence:
            pair_info[(i, j)] = (score, matched)
            union(i, j)

    groups: dict[int, list] = {}
    for i in df.index:
        groups.setdefault(find(i), []).append(i)

    clusters = []
    for members in groups.values():
        if len(members) < 2:
            continue
        member_set = set(members)
        pairs_in_cluster = [(p, v) for p, v in pair_info.items()
                           if p[0] in member_set and p[1] in member_set]
        confidence = max((v[0] for _, v in pairs_in_cluster), default=0.0)
        matched_on = sorted({c for _, v in pairs_in_cluster for c in v[1]})
        clusters.append(DuplicateCluster(row_indices=sorted(members),
                                         confidence=round(confidence, 3), matched_on=matched_on))
    clusters.sort(key=lambda c: -c.confidence)
    return clusters


def build_golden_record(df: pd.DataFrame, cluster: DuplicateCluster) -> dict:
    """Arma el 'golden record' de un cluster: parte del registro más completo
    (menos nulos) y rellena los huecos con valores no nulos de los demás."""
    sub = df.loc[cluster.row_indices]
    completeness = sub.notna().sum(axis=1)
    best_idx = completeness.idxmax()
    golden = sub.loc[best_idx].to_dict()
    for col in sub.columns:
        if pd.isna(golden.get(col)):
            fill = sub[col].dropna()
            if not fill.empty:
                golden[col] = fill.iloc[0]
    return golden


def dedup_report(df: pd.DataFrame, rules: list[MatchRule], min_confidence: float = 0.5,
                 block_column: str | None = None) -> pd.DataFrame:
    """Resumen tabular de los clusters encontrados, listo para mostrar en el tablero."""
    clusters = find_duplicate_clusters(df, rules, min_confidence, block_column)
    rows = [{
        "cluster_id": f"DUP-{i:03d}",
        "rows": len(c.row_indices),
        "confidence": round(c.confidence * 100, 1),
        "matched_on": ", ".join(c.matched_on) if c.matched_on else "—",
        "row_indices": c.row_indices,
    } for i, c in enumerate(clusters, 1)]
    return pd.DataFrame(rows, columns=["cluster_id", "rows", "confidence", "matched_on", "row_indices"])


_STRONG_ID_HINTS = ("id", "documento", "cedula", "dni", "rut", "cuit", "email",
                    "correo", "mail", "telefono", "phone", "passport")


def suggest_rules(df: pd.DataFrame, columns: list[str]) -> list[MatchRule]:
    """Heurística simple para armar reglas de matching sin que el usuario
    tenga que configurar pesos a mano: columnas cuyo NOMBRE 'suena' a
    identificador único (id/documento/email/teléfono) se comparan EXACTAS y
    pesan fuerte; el resto de texto libre (típicamente nombres) se compara
    por similitud y pesa menos — así un nombre común no alcanza el umbral
    por sí solo (ver advertencia del módulo)."""
    rules = []
    for col in columns:
        low = col.lower()
        if any(h in low for h in _STRONG_ID_HINTS):
            rules.append(MatchRule(col, weight=3.0, kind="exact"))
        elif pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_datetime64_any_dtype(df[col]):
            rules.append(MatchRule(col, weight=1.5, kind="exact"))
        else:
            rules.append(MatchRule(col, weight=1.0, kind="fuzzy", fuzzy_threshold=0.85))
    return rules
