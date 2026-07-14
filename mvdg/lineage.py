"""
MV Data Governance · Linaje de datos.

Grafo dirigido de activos por capas (fuente → cruda → curada → mart → BI),
con recorridos aguas arriba / aguas abajo y una figura Plotly lista para el
dashboard — sin dependencias de graphviz.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from . import BRAND

# capa -> orden horizontal en el gráfico
LAYERS = ["source", "raw", "curated", "mart", "bi"]

NODES: list[dict] = [
    {"id": "crm", "label": "CRM", "layer": "source"},
    {"id": "erp", "label": "ERP", "layer": "source"},
    {"id": "pos", "label": "POS / eCommerce", "layer": "source"},
    {"id": "gateway", "label": "Pasarela de pagos", "layer": "source"},
    {"id": "raw_customers", "label": "raw.customers", "layer": "raw"},
    {"id": "raw_products", "label": "raw.products", "layer": "raw"},
    {"id": "raw_sales", "label": "raw.sales", "layer": "raw"},
    {"id": "raw_payments", "label": "raw.payments", "layer": "raw"},
    {"id": "dim_customers", "label": "dim_customers", "layer": "curated"},
    {"id": "dim_products", "label": "dim_products", "layer": "curated"},
    {"id": "fct_sales", "label": "fct_sales", "layer": "curated"},
    {"id": "fct_payments", "label": "fct_payments", "layer": "curated"},
    {"id": "mart_sales", "label": "mart_ventas_360", "layer": "mart"},
    {"id": "mart_finance", "label": "mart_finanzas", "layer": "mart"},
    {"id": "bi_dashboard", "label": "Dashboard BI (Power BI / Tableau / Looker…)", "layer": "bi"},
]

EDGES: list[tuple[str, str]] = [
    ("crm", "raw_customers"), ("erp", "raw_products"),
    ("pos", "raw_sales"), ("gateway", "raw_payments"),
    ("raw_customers", "dim_customers"), ("raw_products", "dim_products"),
    ("raw_sales", "fct_sales"), ("raw_payments", "fct_payments"),
    ("dim_customers", "mart_sales"), ("dim_products", "mart_sales"),
    ("fct_sales", "mart_sales"),
    ("fct_sales", "mart_finance"), ("fct_payments", "mart_finance"),
    ("mart_sales", "bi_dashboard"), ("mart_finance", "bi_dashboard"),
]

_NODE_BY_ID = {n["id"]: n for n in NODES}


def lineage_df() -> pd.DataFrame:
    """Aristas del linaje como tabla plana (exportable a BI)."""
    rows = [{
        "source_id": a, "source": _NODE_BY_ID[a]["label"],
        "source_layer": _NODE_BY_ID[a]["layer"],
        "target_id": b, "target": _NODE_BY_ID[b]["label"],
        "target_layer": _NODE_BY_ID[b]["layer"],
    } for a, b in EDGES]
    return pd.DataFrame(rows)


def upstream(node_id: str, edges: list[tuple[str, str]] | None = None) -> set[str]:
    """Todos los ancestros (recursivo) de un nodo."""
    edges = EDGES if edges is None else edges
    out, frontier = set(), {node_id}
    while frontier:
        parents = {a for a, b in edges if b in frontier} - out
        out |= parents
        frontier = parents
    return out


def downstream(node_id: str, edges: list[tuple[str, str]] | None = None) -> set[str]:
    """Todos los descendientes (recursivo) de un nodo."""
    edges = EDGES if edges is None else edges
    out, frontier = set(), {node_id}
    while frontier:
        children = {b for a, b in edges if a in frontier} - out
        out |= children
        frontier = children
    return out


def _layer_order(nodes: list[dict]) -> list[str]:
    """Capas presentes, en el orden canónico (LAYERS) primero y luego extras."""
    present = list(dict.fromkeys(n["layer"] for n in nodes))
    known = [l for l in LAYERS if l in present]
    extra = [l for l in present if l not in LAYERS]
    return known + extra


def _positions(nodes: list[dict] | None = None) -> dict[str, tuple[float, float]]:
    nodes = NODES if nodes is None else nodes
    pos = {}
    for lx, layer in enumerate(_layer_order(nodes)):
        ids = [n["id"] for n in nodes if n["layer"] == layer]
        for i, nid in enumerate(ids):
            y = -(i - (len(ids) - 1) / 2)  # centrado vertical por capa
            pos[nid] = (float(lx), y * 1.15)
    return pos


def graph_from_lineage(edges_df: pd.DataFrame) -> tuple[list[dict], list[tuple[str, str]]]:
    """Convierte una tabla de linaje (columnas de ``lineage_df``) en el par
    ``(nodes, edges)`` que consume ``lineage_figure``. Sirve para dibujar
    linaje dinámico (p.ej. el que devuelve ``powerbi_meta.to_lineage``) sin
    tocar el grafo de demo."""
    nodes: dict[str, dict] = {}
    edges: list[tuple[str, str]] = []
    for _, r in edges_df.iterrows():
        nodes.setdefault(r["source_id"],
                         {"id": r["source_id"], "label": r["source"], "layer": r["source_layer"]})
        nodes.setdefault(r["target_id"],
                         {"id": r["target_id"], "label": r["target"], "layer": r["target_layer"]})
        edges.append((r["source_id"], r["target_id"]))
    return list(nodes.values()), edges


def lineage_figure(focus: str | None = None,
                   layer_titles: dict[str, str] | None = None,
                   nodes: list[dict] | None = None,
                   edges: list[tuple[str, str]] | None = None) -> go.Figure:
    """Figura Plotly del grafo. Si ``focus`` viene, resalta ese nodo y su
    linaje (aguas arriba + aguas abajo) y atenúa el resto. Si ``nodes``/``edges``
    vienen, dibuja ese grafo dinámico en vez del de demo."""
    nodes = NODES if nodes is None else nodes
    edges = EDGES if edges is None else edges
    node_by_id = {n["id"]: n for n in nodes}
    order = _layer_order(nodes)
    pos = _positions(nodes)
    hi = None
    if focus and focus in node_by_id:
        hi = {focus} | upstream(focus, edges) | downstream(focus, edges)

    fig = go.Figure()
    for a, b in edges:
        if a not in pos or b not in pos:  # arista hacia un nodo no definido: la salteamos
            continue
        (x0, y0), (x1, y1) = pos[a], pos[b]
        on_path = hi is None or (a in hi and b in hi)
        fig.add_trace(go.Scatter(
            x=[x0, (x0 + x1) / 2, x1], y=[y0, (y0 + y1) / 2 + 0.06, y1],
            mode="lines", hoverinfo="skip", showlegend=False,
            line={"color": BRAND["amber"] if on_path and hi else BRAND["blue"],
                  "width": 2.4 if on_path and hi else 1.4},
            opacity=1.0 if on_path else 0.18,
        ))

    layer_color = {"source": "#6c7f99", "raw": BRAND["blue"],
                   "curated": BRAND["green"], "mart": BRAND["amber"],
                   "bi": "#c479e8"}
    xs, ys, texts, colors, opac = [], [], [], [], []
    for n in nodes:
        x, y = pos[n["id"]]
        xs.append(x); ys.append(y); texts.append(n["label"])
        colors.append(layer_color.get(n["layer"], "#6c7f99"))
        opac.append(1.0 if (hi is None or n["id"] in hi) else 0.25)
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="markers+text", text=texts,
        textposition="bottom center", hoverinfo="text", showlegend=False,
        textfont={"size": 11, "color": BRAND["ink"]},
        marker={"size": 20, "color": colors, "opacity": opac,
                "line": {"color": "#ffffff", "width": 1.4}},
    ))

    titles = layer_titles or {}
    for lx, layer in enumerate(order):
        fig.add_annotation(x=lx, y=2.35, text=f"<b>{titles.get(layer, layer)}</b>",
                           showarrow=False, font={"size": 12, "color": BRAND["muted"]})

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 10, "r": 10, "t": 30, "b": 10}, height=460,
        xaxis={"visible": False, "range": [-0.5, max(len(order), 1) - 0.4]},
        yaxis={"visible": False, "range": [-2.9, 2.7]},
    )
    return fig
