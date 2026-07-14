"""
MV Data Governance · Dashboard de escritorio (Streamlit).

Trilingüe (ES/EN/PT), estilo MV Kobra: navy + ámbar. Se ejecuta con el .bat,
con `streamlit run app/app.py` o empaquetado como .exe (PyInstaller).
"""
from __future__ import annotations

import os
import sys

# Permite ejecutar tanto desde la raíz del repo como desde el bundle PyInstaller.
_ROOT = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from mvdg import APP_NAME, BRAND, __version__
from mvdg.catalog import catalog_df, dictionary_df, dataset_names, pii_columns
from mvdg.clients import (BI_TOOLS, IT_RESTRICTIONS, STATUSES, clients_df,
                          data_dir, delete_client, load_clients,
                          recommended_pack, save_client)
from mvdg.connectors import (ENGINES, delete_connection, list_tables,
                             load_connections, load_table, run_query,
                             save_connection, stored_password, test_connection)
from mvdg.help_center import automation_rows, speeches
from mvdg.lab_case import lab_measure, lab_steps
from mvdg import dmbok
from mvdg import samples as ext_samples
from mvdg.remediation import suggest_fix
from mvdg.ai_provider import ai_suggest_fix, configured_provider, provider_label
from mvdg.demo_data import load_demo_tables
from mvdg.exporters import (bi_bundle_xlsx, governance_tables, to_csv_bytes,
                            to_excel_bytes, to_json_bytes, to_parquet_bytes)
from mvdg.glossary import glossary_df, term_count
from mvdg.i18n import LANG_NAMES, LANGS, t
from mvdg.lineage import NODES, lineage_df, lineage_figure
from mvdg.policies import policies_df
from mvdg.profiler import profile_table, suggest_rules, summary
from mvdg.quality import (open_issues, overall_index, quality_by_dimension,
                          quality_by_dataset, quality_matrix, quality_trend,
                          run_rules)

# ----------------------------------------------------------------- página
st.set_page_config(page_title=APP_NAME, page_icon="🛡️", layout="wide")

st.markdown(f"""
<style>
.stApp {{ background: linear-gradient(160deg, {BRAND['navy']} 0%, #0a1a2f 100%); }}
h1, h2, h3 {{ color: {BRAND['ink']}; }}
[data-testid="stMetricValue"] {{ color: {BRAND['amber']}; }}
[data-testid="stMetricLabel"] {{ color: {BRAND['muted']}; }}
[data-testid="stSidebar"] {{ background: {BRAND['navy2']}; }}
.mv-badge {{ display:inline-block; background:rgba(242,180,65,.12);
  border:1px solid rgba(242,180,65,.4); color:{BRAND['amber']};
  border-radius:20px; padding:4px 14px; font-size:12px; font-weight:700;
  letter-spacing:.06em; text-transform:uppercase; margin-bottom:6px; }}
</style>
""", unsafe_allow_html=True)

_PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font={"color": BRAND["ink"]},
    margin={"l": 10, "r": 10, "t": 40, "b": 10},
)


@st.cache_data(show_spinner=False)
def _tables():
    return load_demo_tables()


@st.cache_data(show_spinner=False)
def _results(lang: str):
    return run_rules(_tables(), lang)


@st.cache_data(show_spinner=False)
def _lab(lang: str):
    return lab_measure(lang)


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown(f"## 🛡️ {APP_NAME}")
    lang = st.radio(
        f"🌐 {t('language', 'es')} / Language / Idioma",
        LANGS, format_func=lambda code: LANG_NAMES[code], horizontal=True,
        key="lang",
    )
    st.caption(t("sidebar_help", lang))
    st.divider()
    st.caption(f"v{__version__} · {t('demo_note', lang)}")

st.markdown(f"<span class='mv-badge'>MV · Data Governance Suite</span>", unsafe_allow_html=True)
st.title(APP_NAME)
st.caption(t("app_tagline", lang))

results = _results(lang)
tables = _tables()

(tab_ov, tab_lab, tab_dk, tab_cat, tab_q, tab_lin, tab_g, tab_p, tab_pr, tab_bi,
 tab_cl, tab_h) = st.tabs([
    t("tab_overview", lang), t("tab_lab", lang), t("tab_dmbok", lang),
    t("tab_catalog", lang), t("tab_quality", lang),
    t("tab_lineage", lang), t("tab_glossary", lang), t("tab_policies", lang),
    t("tab_profiler", lang), t("tab_bi", lang),
    t("tab_clients", lang), t("tab_help", lang),
])

_DIM_LABEL = {d: t(f"dim_{d}", lang) for d in
              ["completeness", "uniqueness", "validity", "consistency",
               "timeliness", "accuracy"]}
_STATUS_LABEL = {"pass": t("q_pass", lang), "warn": t("q_warn", lang),
                 "fail": t("q_fail", lang)}


def _render_fixes(results_df, lang):
    """Por cada regla en warn/fail: sugerencia local para corregirla, al
    lado de la falla — causa probable, corto plazo y prevención. Si el
    usuario configuró su propia API key (Claude/ChatGPT/Gemini), además se
    puede pedir una sugerencia generada en vivo por ese modelo, por regla."""
    st.subheader(t("fix_title", lang))
    provider = configured_provider()
    if provider:
        st.caption(t("fix_note_ai", lang).format(provider=provider_label(provider)))
    else:
        st.caption(t("fix_note", lang))
    broken = results_df[results_df["status"] != "pass"]
    if broken.empty:
        st.success(t("fix_none", lang), icon="✅")
        return
    for _, row in broken.iterrows():
        icon = "🟠" if row["status"] == "warn" else "🔴"
        with st.expander(f"{icon} {row['rule_id']} — {row['description']}", expanded=False):
            fix = suggest_fix(row["rule_id"], row["dimension"], row["column"],
                              int(row["affected_rows"]), lang)
            st.markdown(f"🖥️ **{t('fix_local_title', lang)}**")
            st.markdown(f"**{t('fix_root', lang)}:** {fix['root_cause']}")
            st.markdown(f"**{t('fix_short', lang)}:** {fix['short_term']}")
            st.markdown(f"**{t('fix_long', lang)}:** {fix['long_term']}")
            st.caption(f"{t('fix_owner', lang)}: {fix['owner']}")

            if provider:
                cache_key = f"ai_fix_{row['dataset']}_{row['rule_id']}_{lang}"
                if st.button(t("fix_ai_button", lang).format(provider=provider_label(provider)),
                            key=f"btn_{cache_key}"):
                    with st.spinner(t("fix_ai_loading", lang)):
                        st.session_state[cache_key] = ai_suggest_fix(
                            row["dataset"], row["column"], row["dimension"],
                            row["description"], int(row["affected_rows"]),
                            lang, provider) or "error"
                cached = st.session_state.get(cache_key)
                if cached == "error":
                    st.warning(t("fix_ai_error", lang), icon="⚠️")
                elif cached:
                    st.divider()
                    st.markdown(f"✨ **{t('fix_ai_title', lang).format(provider=provider_label(provider))}**")
                    st.markdown(f"**{t('fix_root', lang)}:** {cached['root_cause']}")
                    st.markdown(f"**{t('fix_short', lang)}:** {cached['short_term']}")
                    st.markdown(f"**{t('fix_long', lang)}:** {cached['long_term']}")
                    st.caption(f"{t('fix_owner', lang)}: {cached['owner']}")

# --------------------------------------------------------------- Panorama
with tab_ov:
    cat = catalog_df(lang, tables)
    dic = dictionary_df(lang)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("kpi_datasets", lang), len(cat))
    c2.metric(t("kpi_columns", lang), len(dic))
    c3.metric(t("kpi_quality", lang), f"{overall_index(results)} / 100")
    npass = int((results["status"] == "pass").sum())
    c4.metric(t("kpi_rules_pass", lang), f"{npass} / {len(results)}")
    c5, c6, c7, c8 = st.columns(4)
    c5.metric(t("kpi_pii", lang), len(pii_columns()))
    c6.metric(t("kpi_stewards", lang), cat["steward"].nunique())
    c7.metric(t("kpi_terms", lang), term_count())
    c8.metric(t("kpi_rules", lang), len(results))

    col_a, col_b = st.columns(2)
    with col_a:
        by_ds = quality_by_dataset(results).merge(
            cat[["dataset", "domain"]], on="dataset", how="left")
        fig = px.bar(by_ds, x="domain", y="quality_index", text="quality_index",
                     title=t("ov_quality_by_domain", lang),
                     color_discrete_sequence=[BRAND["amber"]])
        fig.update_traces(texttemplate="%{text:.1f}")
        fig.update_layout(**_PLOTLY_LAYOUT, yaxis_range=[90, 100.5],
                          xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, width="stretch")
    with col_b:
        by_dim = quality_by_dimension(results)
        by_dim["dimension"] = by_dim["dimension"].map(_DIM_LABEL)
        fig = go.Figure(go.Scatterpolar(
            r=by_dim["quality_index"], theta=by_dim["dimension"],
            fill="toself", line={"color": BRAND["amber"]},
            fillcolor="rgba(242,180,65,.25)"))
        fig.update_layout(**_PLOTLY_LAYOUT, title=t("ov_quality_by_dim", lang),
                          polar={"radialaxis": {"range": [90, 100],
                                                "color": BRAND["muted"]},
                                 "bgcolor": "rgba(255,255,255,.03)"})
        st.plotly_chart(fig, width="stretch")

    col_c, col_d = st.columns(2)
    with col_c:
        trend = quality_trend(results)
        fig = px.area(trend, x="month", y="quality_index",
                      title=t("ov_trend", lang),
                      color_discrete_sequence=[BRAND["green"]])
        fig.update_layout(**_PLOTLY_LAYOUT, yaxis_range=[80, 101],
                          xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, width="stretch")
    with col_d:
        issues = open_issues(results)
        sev = issues["severity"].value_counts().reset_index()
        sev.columns = ["severity", "count"]
        fig = px.bar(sev, x="severity", y="count", text="count",
                     title=t("ov_issues", lang),
                     color="severity",
                     color_discrete_map={"alta": BRAND["red"],
                                         "media": BRAND["amber"]})
        fig.update_layout(**_PLOTLY_LAYOUT, showlegend=False,
                          xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, width="stretch")

# ------------------------------------------------------------ Laboratorio
with tab_lab:
    st.info(t("lab_intro", lang), icon="🧪")
    steps = {s["step_id"]: s for s in lab_steps(lang)}
    lab = _lab(lang)

    def _theory(step_id: str):
        s = steps[step_id]
        st.subheader(s["title"])
        tc1, tc2 = st.columns(2)
        tc1.markdown(f"**{t('lab_plain', lang)}**  \n{s['plain']}")
        tc2.markdown(f"**{t('lab_tech', lang)}**  \n{s['tech']}")
        if s["dmbok_area"]:
            st.caption(f"🔗 {t('lab_dmbok_tag', lang)}: {s['dmbok_area']}")

    # 0. Contexto
    _theory("contexto")
    st.divider()

    # 1. Catalogar
    _theory("catalogar")
    cat_lab = catalog_df(lang, tables)
    st.dataframe(cat_lab[["dataset", "domain", "owner", "steward",
                          "classification", "refresh"]].rename(columns={
        "dataset": t("col_dataset", lang), "domain": t("cat_domain", lang),
        "owner": t("col_owner", lang), "steward": t("col_steward", lang),
        "classification": t("col_classification", lang),
        "refresh": t("col_freshness", lang),
    }), width="stretch", hide_index=True)
    with st.expander(t("tbl_dictionary", lang)):
        st.dataframe(dictionary_df(lang, "dim_customers").drop(columns=["dataset"]),
                    width="stretch", hide_index=True)
    st.divider()

    # 2. Medir ANTES
    _theory("medir_antes")
    b = lab["summary_before"]
    c1, c2, c3 = st.columns(3)
    c1.metric(t("lab_index", lang), f"{b['indice']} / 100")
    c2.metric(t("lab_rows_affected", lang), f"{b['filas_afectadas']:,}")
    c3.metric(t("lab_rules_fail", lang), f"{b['fallas']} / {b['reglas_total']}")
    issues_before = lab["issues_before"].copy()
    issues_before["dimension"] = issues_before["dimension"].map(_DIM_LABEL)
    with st.expander(t("lab_issues_before", lang)):
        st.dataframe(issues_before.rename(columns={
            "rule_id": "ID", "dataset": t("col_dataset", lang),
            "column": t("col_column", lang), "dimension": t("q_dimension", lang),
            "severity": t("q_status", lang), "score": t("q_score", lang),
            "affected_rows": t("q_affected", lang),
        }), width="stretch", hide_index=True)
    st.divider()

    # 3. Gobernar
    _theory("gobernar")
    st.dataframe(glossary_df(lang).drop(columns=["term_id"]).rename(columns={
        "term": t("g_term", lang), "definition": t("g_definition", lang),
        "owner": t("col_owner", lang), "linked_datasets": t("g_linked", lang),
    }), width="stretch", hide_index=True)
    st.divider()

    # 4. Medir DESPUÉS + comparación
    _theory("medir_despues")
    a = lab["summary_after"]
    c4, c5, c6 = st.columns(3)
    c4.metric(t("lab_index", lang), f"{a['indice']} / 100", delta=f"+{lab['mejora_indice']}")
    c5.metric(t("lab_rows_affected", lang), f"{a['filas_afectadas']:,}",
             delta=f"-{lab['reduccion_filas_pct']}%")
    c6.metric(t("lab_rules_fail", lang), f"{a['fallas']} / {a['reglas_total']}")

    by_dim = lab["by_dimension"].copy()
    by_dim["dimension"] = by_dim["dimension"].map(_DIM_LABEL)
    by_dim_long = by_dim.melt(id_vars="dimension", value_vars=["antes", "despues"],
                              var_name="momento", value_name="quality_index")
    by_dim_long["momento"] = by_dim_long["momento"].map(
        {"antes": t("lab_before", lang), "despues": t("lab_after", lang)})
    fig = px.bar(by_dim_long, x="dimension", y="quality_index", color="momento",
                barmode="group", title=t("lab_compare_dim", lang),
                color_discrete_map={t("lab_before", lang): BRAND["red"],
                                    t("lab_after", lang): BRAND["green"]})
    fig.update_layout(**_PLOTLY_LAYOUT, yaxis_range=[0, 101],
                      xaxis_title=None, yaxis_title=None, legend_title=None)
    st.plotly_chart(fig, width="stretch", key="lab_compare_dim")
    st.divider()

    # 5. Linaje
    _theory("linaje")
    lab_layer_titles = {
        "source": t("lin_layer_source", lang), "raw": t("lin_layer_raw", lang),
        "curated": t("lin_layer_curated", lang), "mart": t("lin_layer_mart", lang),
        "bi": t("lin_layer_bi", lang),
    }
    st.plotly_chart(lineage_figure(None, lab_layer_titles), width="stretch", key="lab_lineage")
    st.divider()

    # 6. Políticas
    _theory("politicas")
    pdf_lab = policies_df(lang, lab["results_after"])
    status_label_lab = {"compliant": t("p_compliant", lang),
                        "partial": t("p_partial", lang),
                        "noncompliant": t("p_noncompliant", lang)}
    pdf_lab["status"] = pdf_lab["status"].map(status_label_lab)
    st.dataframe(pdf_lab.rename(columns={
        "policy_id": "ID", "policy": t("p_policy", lang),
        "category": t("p_category", lang), "status": t("p_compliance", lang),
        "evidence": t("p_evidence", lang),
    }), width="stretch", hide_index=True)
    st.divider()

    # 7. BI
    _theory("bi")
    st.divider()

    # Resultado final
    st.subheader(t("lab_summary_title", lang))
    r1, r2 = st.columns(2)
    r1.metric(t("lab_delta", lang), f"+{lab['mejora_indice']} pts",
             help=f"{b['indice']} → {a['indice']}")
    r2.metric(t("lab_rows_cut", lang), f"-{lab['reduccion_filas_pct']}%",
             help=f"{b['filas_afectadas']:,} → {a['filas_afectadas']:,}")
    st.caption(t("lab_reproducible", lang))

# ----------------------------------------------------------- Tutorial DMBOK
with tab_dk:
    st.info(t("dk_intro", lang), icon="📘")

    # --- Teoría: qué es el DMBOK ---
    st.subheader(t("dk_what", lang))
    st.markdown(t("dk_what_p", lang))

    # --- Principios rectores ---
    st.subheader(t("dk_principles", lang))
    pr_cols = st.columns(3)
    for i, pr in enumerate(dmbok.principles(lang)):
        with pr_cols[i % 3]:
            st.markdown(f"**{pr['title']}**  \n{pr['text']}")

    # --- Dashboard 1: radar de cobertura por área ---
    st.subheader(t("dk_radar", lang))
    cov = dmbok.coverage_summary()
    k1, k2, k3 = st.columns(3)
    k1.metric(t("dk_covered", lang), cov["covered"])
    k2.metric(t("dk_partial", lang), cov["partial"])
    k3.metric(t("dk_out", lang), cov["out"])
    radar = dmbok.coverage_scores(lang)
    r_theta = [name for name, _ in radar] + [radar[0][0]]
    r_r = [score for _, score in radar] + [radar[0][1]]
    fig = go.Figure(go.Scatterpolar(r=r_r, theta=r_theta, fill="toself",
                                    line={"color": BRAND["amber"]},
                                    fillcolor="rgba(242,180,65,.25)"))
    fig.update_layout(**_PLOTLY_LAYOUT, height=460,
                      polar={"radialaxis": {"range": [0, 100], "color": BRAND["muted"]},
                             "bgcolor": "rgba(255,255,255,.03)"})
    st.plotly_chart(fig, width="stretch", key="dk_radar")

    # --- Las 11 áreas (expandibles, teoría + entregables + cobertura) ---
    st.subheader(t("dk_areas", lang))
    _COV_LABEL = {"covered": t("h_dmbok_covered", lang),
                  "partial": t("h_dmbok_partial", lang),
                  "out": t("h_dmbok_out", lang)}
    for ar in dmbok.areas(lang):
        with st.expander(f"{ar['n']}. {_COV_LABEL[ar['coverage']]} — {ar['area']}"):
            st.markdown(f"**{t('dk_plain', lang)}:** {ar['plain']}")
            st.markdown(f"**{t('dk_tech', lang)}:** {ar['tech']}")
            st.markdown(f"**{t('dk_deliverables', lang)}:** {ar['deliverables']}")
            st.caption(ar["note"])

    # --- Conceptos clave (glosario buscable) ---
    st.subheader(t("dk_concepts", lang))
    cq = st.text_input(t("dk_concept_search", lang), "", key="dk_cq")
    cdf = pd.DataFrame(dmbok.concepts(lang))[["cat", "term", "def"]]
    if cq:
        mask = cdf.apply(lambda r: cq.lower() in " ".join(map(str, r)).lower(), axis=1)
        cdf = cdf[mask]
    st.dataframe(cdf.rename(columns={
        "cat": t("p_category", lang), "term": t("g_term", lang),
        "def": t("g_definition", lang)}), width="stretch", hide_index=True)

    # --- Roles del gobierno de datos ---
    st.subheader(t("dk_roles", lang))
    rdf = pd.DataFrame(dmbok.roles(lang))[["term", "def"]]
    st.dataframe(rdf.rename(columns={
        "term": t("dk_role", lang), "def": t("dk_responsibility", lang)}),
        width="stretch", hide_index=True)

    # --- Dashboard 2: modelo de madurez ---
    st.subheader(t("dk_maturity", lang))
    st.markdown(t("dk_maturity_note", lang))
    mat = dmbok.maturity(lang)
    mat_df = pd.DataFrame(mat)
    fig = px.bar(mat_df, x="level", y=[1] * len(mat_df), text="name",
                 color="level", color_continuous_scale=["#e05c5c", "#f2b441", "#00c896"],
                 title=None)
    fig.update_traces(textposition="inside", insidetextanchor="middle",
                      hovertemplate="%{text}")
    fig.update_layout(**_PLOTLY_LAYOUT, height=180, showlegend=False,
                      coloraxis_showscale=False, yaxis={"visible": False},
                      xaxis={"title": None, "tickmode": "linear"})
    st.plotly_chart(fig, width="stretch", key="dk_maturity_bar")
    for m in mat:
        st.markdown(f"**{t('dk_level', lang)} {m['level']} · {m['name']}** — {m['desc']}")

    # --- Ciclo de vida (POSMAD) ---
    st.subheader(t("dk_lifecycle", lang))
    st.markdown(t("dk_lifecycle_note", lang))
    lc_cols = st.columns(len(dmbok.lifecycle(lang)))
    for i, ph in enumerate(dmbok.lifecycle(lang)):
        with lc_cols[i]:
            st.markdown(f"**{i+1}. {ph['phase']}**")
            st.caption(ph["desc"])

    # --- Dashboard 3: las 6 dimensiones de calidad medidas en vivo ---
    st.subheader(t("dk_quality_dims", lang))
    by_dim = quality_by_dimension(results)
    by_dim["dimension"] = by_dim["dimension"].map(_DIM_LABEL)
    fig = px.bar(by_dim, x="dimension", y="quality_index", text="quality_index",
                 color_discrete_sequence=[BRAND["green"]])
    fig.update_traces(texttemplate="%{text:.1f}")
    fig.update_layout(**_PLOTLY_LAYOUT, yaxis_range=[0, 101],
                      xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig, width="stretch", key="dk_quality_dims")

# --------------------------------------------------------------- Catálogo
with tab_cat:
    st.info(t("cat_intro", lang), icon="📚")
    cat = catalog_df(lang, tables)
    f1, f2 = st.columns([2, 1])
    query = f1.text_input(t("cat_search", lang), "")
    domains = [t("cat_all", lang)] + sorted(cat["domain"].unique().tolist())
    dom = f2.selectbox(t("cat_domain", lang), domains)
    view = cat.copy()
    if query:
        mask = view.apply(lambda r: query.lower() in " ".join(map(str, r)).lower(), axis=1)
        view = view[mask]
    if dom != t("cat_all", lang):
        view = view[view["domain"] == dom]
    qidx = quality_by_dataset(results).set_index("dataset")["quality_index"]
    view = view.assign(**{t("col_quality", lang): view["dataset"].map(qidx)})
    st.dataframe(view.rename(columns={
        "dataset": t("col_dataset", lang), "domain": t("cat_domain", lang),
        "description": t("col_description", lang), "owner": t("col_owner", lang),
        "steward": t("col_steward", lang),
        "classification": t("col_classification", lang),
        "refresh": t("col_freshness", lang), "rows": t("col_rows", lang),
    }), width="stretch", hide_index=True)

    st.subheader(t("cat_detail", lang))
    ds = st.selectbox(t("cat_pick", lang), dataset_names())
    dic = dictionary_df(lang, ds)
    st.dataframe(dic.rename(columns={
        "column": t("col_column", lang), "type": t("col_type", lang),
        "pii": t("col_pii", lang), "business_term": t("col_term", lang),
        "description": t("col_description", lang),
    }).drop(columns=["dataset"]), width="stretch", hide_index=True)

# ---------------------------------------------------------------- Calidad
with tab_q:
    st.info(t("q_intro", lang), icon="✅")
    if st.button(t("q_run", lang)):
        _results.clear()
        results = _results(lang)
    show = results.copy()
    show["dimension"] = show["dimension"].map(_DIM_LABEL)
    show["status"] = show["status"].map(_STATUS_LABEL)
    st.subheader(t("q_results", lang))
    st.dataframe(show.rename(columns={
        "rule_id": "ID", "dataset": t("col_dataset", lang),
        "column": t("col_column", lang), "dimension": t("q_dimension", lang),
        "description": t("q_rule", lang), "score": t("q_score", lang),
        "threshold": t("q_threshold", lang), "status": t("q_status", lang),
        "affected_rows": t("q_affected", lang),
    }), width="stretch", hide_index=True)

    _render_fixes(results, lang)

    matrix = quality_matrix(results)
    matrix.columns = [_DIM_LABEL[c] for c in matrix.columns]
    fig = px.imshow(matrix, text_auto=".1f", aspect="auto",
                    color_continuous_scale=["#e05c5c", "#f2b441", "#00c896"],
                    zmin=90, zmax=100, title=t("q_heatmap", lang))
    fig.update_layout(**_PLOTLY_LAYOUT, height=380)
    st.plotly_chart(fig, width="stretch")

# ----------------------------------------------------------------- Linaje
with tab_lin:
    st.info(t("lin_intro", lang), icon="🧬")
    labels = {n["id"]: n["label"] for n in NODES}
    focus = st.selectbox(t("lin_focus", lang),
                         ["—"] + list(labels.keys()),
                         format_func=lambda k: labels.get(k, k))
    layer_titles = {
        "source": t("lin_layer_source", lang), "raw": t("lin_layer_raw", lang),
        "curated": t("lin_layer_curated", lang), "mart": t("lin_layer_mart", lang),
        "bi": t("lin_layer_bi", lang),
    }
    fig = lineage_figure(None if focus == "—" else focus, layer_titles)
    st.plotly_chart(fig, width="stretch")
    with st.expander(t("tbl_lineage", lang)):
        st.dataframe(lineage_df(), width="stretch", hide_index=True)

# --------------------------------------------------------------- Glosario
with tab_g:
    st.info(t("g_intro", lang), icon="📖")
    gdf = glossary_df(lang)
    gq = st.text_input(t("g_search", lang), "")
    if gq:
        mask = gdf.apply(lambda r: gq.lower() in " ".join(map(str, r)).lower(), axis=1)
        gdf = gdf[mask]
    st.dataframe(gdf.rename(columns={
        "term": t("g_term", lang), "definition": t("g_definition", lang),
        "owner": t("col_owner", lang), "linked_datasets": t("g_linked", lang),
    }).drop(columns=["term_id"]), width="stretch", hide_index=True)

# --------------------------------------------------------------- Políticas
with tab_p:
    st.info(t("p_intro", lang), icon="🛡️")
    pdf = policies_df(lang, results)
    status_label = {"compliant": t("p_compliant", lang),
                    "partial": t("p_partial", lang),
                    "noncompliant": t("p_noncompliant", lang)}
    pdf["status"] = pdf["status"].map(status_label)
    st.dataframe(pdf.rename(columns={
        "policy_id": "ID", "policy": t("p_policy", lang),
        "category": t("p_category", lang), "status": t("p_compliance", lang),
        "evidence": t("p_evidence", lang),
    }), width="stretch", hide_index=True)

# --------------------------------------------------------------- Mis datos
def _render_profile(user_df):
    """Perfila y muestra un DataFrame (venga de archivo o de base de datos)."""
    if user_df is None or not len(user_df):
        return
    info = summary(user_df)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("col_rows", lang), f"{info['rows']:,}")
    c2.metric(t("col_column", lang), info["columns"])
    c3.metric(t("pr_dupes", lang), info["duplicate_rows"])
    c4.metric(t("pr_nulls", lang), f"{info['null_cells_pct']}%")
    st.subheader(t("pr_col_profile", lang))
    st.dataframe(profile_table(user_df).rename(columns={
        "column": t("col_column", lang), "dtype": t("col_type", lang),
        "null_pct": t("pr_nulls", lang), "unique_values": t("pr_unique", lang),
        "possible_pii": t("col_pii", lang),
    }), width="stretch", hide_index=True)
    if info["pii_columns"]:
        st.warning(t("pr_pii_hint", lang), icon="🔐")
    st.subheader(t("pr_suggestions", lang))
    for s in suggest_rules(user_df, lang):
        st.markdown(f"- {s}")


with tab_pr:
    st.info(t("pr_intro", lang), icon="🔎")
    _SRC_LABEL = {"example": t("pr_src_example", lang),
                  "file": t("pr_src_file", lang), "db": t("pr_src_db", lang)}
    source = st.radio(t("pr_source", lang),
                      ["example", "file", "db"], horizontal=True, key="pr_source",
                      format_func=lambda k: _SRC_LABEL[k])

    if source == "example":
        st.caption(t("pr_example_intro", lang))
        skeys = ext_samples.sample_keys()
        skey = st.selectbox(t("pr_example_pick", lang), skeys, key="pr_example_key",
                            format_func=lambda k: ext_samples.sample_meta(k, lang)["name"])
        meta = ext_samples.sample_meta(skey, lang)

        # --- 1. Ficha del dataset (catálogo: dueño, steward, clasificación) ---
        st.subheader(f"📇 {t('pr_example_card', lang)}")
        st.markdown(f"**{meta['name']}** — {meta['description']}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(t("cat_domain", lang), meta["domain"])
        c2.metric(t("col_owner", lang), meta["owner"])
        c3.metric(t("col_steward", lang), meta["steward"])
        c4.metric(t("col_classification", lang), meta["classification"])
        c5, c6 = st.columns(2)
        c5.markdown(f"**{t('pr_example_source_lbl', lang)}:** {meta['source']}" +
                   (f" — [{meta['source_url']}]({meta['source_url']})" if meta["source_url"] else ""))
        c6.markdown(f"**{t('pr_example_license_lbl', lang)}:** {meta['license']} · "
                   f"**{t('col_freshness', lang)}:** {meta['refresh']}")
        if meta.get("classification_note"):
            st.caption(f"ℹ️ {meta['classification_note']}")
        with st.expander("👁️ " + t("pr_example_data", lang), expanded=False):
            st.dataframe(ext_samples.load_sample_table(skey).head(20), width="stretch", hide_index=True)

        # --- 2. Métricas: reglas de calidad con umbral/estado (no perfilado genérico) ---
        st.subheader(f"✅ {t('pr_example_metrics', lang)}")
        sres = ext_samples.sample_quality_results(skey, lang)
        s_show = sres.copy()
        s_show["dimension"] = s_show["dimension"].map(lambda d: _DIM_LABEL.get(d, d))
        s_show["status"] = s_show["status"].map(_STATUS_LABEL)
        k1, k2, k3 = st.columns(3)
        k1.metric(t("kpi_quality", lang), f"{overall_index(sres)} / 100")
        k2.metric(t("kpi_rules_pass", lang), f"{int((sres['status']=='pass').sum())} / {len(sres)}")
        k3.metric(t("col_rows", lang), f"{len(ext_samples.load_sample_table(skey)):,}")
        st.dataframe(s_show.rename(columns={
            "rule_id": "ID", "dataset": t("col_dataset", lang), "column": t("col_column", lang),
            "dimension": t("q_dimension", lang), "description": t("q_rule", lang),
            "score": t("q_score", lang), "threshold": t("q_threshold", lang),
            "status": t("q_status", lang), "affected_rows": t("q_affected", lang),
        }), width="stretch", hide_index=True)
        sdim = quality_by_dimension(sres)
        sdim["dimension"] = sdim["dimension"].map(lambda d: _DIM_LABEL.get(d, d))
        fig = px.bar(sdim, x="dimension", y="quality_index", text="quality_index",
                    color_discrete_sequence=[BRAND["amber"]])
        fig.update_traces(texttemplate="%{text:.1f}")
        fig.update_layout(**_PLOTLY_LAYOUT, yaxis_range=[0, 101], xaxis_title=None,
                          yaxis_title=None, height=300)
        st.plotly_chart(fig, width="stretch", key=f"pr_example_dims_{skey}")

        _render_fixes(sres, lang)

        # --- 3. Definiciones (glosario) ---
        st.subheader(f"📖 {t('pr_example_glossary_title', lang)}")
        sgloss = ext_samples.sample_glossary_df(skey, lang)
        st.dataframe(sgloss.drop(columns=["term_id"]).rename(columns={
            "term": t("g_term", lang), "definition": t("g_definition", lang),
            "owner": t("col_owner", lang), "linked_datasets": t("g_linked", lang),
        }), width="stretch", hide_index=True)

        # --- 4. Exportar / conectar a BI (Power BI, Tableau, API) ---
        st.subheader(f"📤 {t('pr_example_bi_title', lang)}")
        st.caption(t("pr_example_bi_note", lang))
        gov_s = ext_samples.sample_governance_tables(skey, lang)
        bt_labels = {"data": t("pr_example_data", lang), "dictionary": t("tbl_dictionary", lang),
                    "quality_results": t("tbl_quality", lang), "glossary": t("tbl_glossary", lang)}
        bpick = st.selectbox(t("bi_pick_table", lang), list(gov_s.keys()),
                             format_func=lambda k: bt_labels.get(k, k), key=f"pr_example_bt_{skey}")
        bdf = gov_s[bpick]
        e1, e2, e3, e4 = st.columns(4)
        e1.download_button(t("bi_download_csv", lang), to_csv_bytes(bdf),
                           f"mvdg_sample_{skey}_{bpick}_{lang}.csv", "text/csv", width="stretch")
        e2.download_button(t("bi_download_xlsx", lang), to_excel_bytes(bdf, bpick),
                           f"mvdg_sample_{skey}_{bpick}_{lang}.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           width="stretch")
        e3.download_button(t("bi_download_json", lang), to_json_bytes(bdf),
                           f"mvdg_sample_{skey}_{bpick}_{lang}.json", "application/json", width="stretch")
        bpq = to_parquet_bytes(bdf)
        if bpq is not None:
            e4.download_button(t("bi_download_parquet", lang), bpq,
                               f"mvdg_sample_{skey}_{bpick}_{lang}.parquet",
                               "application/octet-stream", width="stretch")
        base = "http://127.0.0.1:8600"
        st.code("\n".join(f"GET {base}/api/samples/{skey}/{name}?lang={lang}" for name in gov_s) +
               f"\nGET {base}/api/samples/{skey}/data?lang={lang}&format=csv", language="http")
        st.caption(t("bi_guide", lang))

        # --- 5. Comparar con el perfilado genérico (opcional) ---
        with st.expander(t("pr_example_generic_toggle", lang), expanded=False):
            _render_profile(ext_samples.load_sample_table(skey))
    elif source == "file":
        up = st.file_uploader(t("pr_upload", lang), type=["csv", "xlsx", "xls"])
        if up is not None:
            try:
                user_df = (pd.read_csv(up) if up.name.lower().endswith(".csv")
                           else pd.read_excel(up))
            except Exception as exc:  # archivo corrupto / formato raro
                st.error(f"⚠️ {exc}")
                user_df = None
            _render_profile(user_df)
    else:
        st.markdown(t("db_intro", lang))
        existing = load_connections()
        opts = [t("db_new_conn", lang)] + [
            f"{c.get('name') or c.get('host')} ({ENGINES.get(c.get('engine'), {}).get('label', c.get('engine'))})"
            for c in existing]
        pick = st.selectbox(t("db_saved_conns", lang), opts)
        editing = existing[opts.index(pick) - 1] if pick != t("db_new_conn", lang) else None

        engine_keys = list(ENGINES.keys())
        e1, e2, e3 = st.columns(3)
        engine = e1.selectbox(t("db_engine", lang), engine_keys,
                              index=engine_keys.index((editing or {}).get("engine", "postgresql"))
                              if (editing or {}).get("engine") in engine_keys else 0,
                              format_func=lambda k: ENGINES[k]["label"])
        conn_name = e2.text_input(t("db_name", lang), (editing or {}).get("name", ""))
        is_sqlite = engine == "sqlite"
        if is_sqlite:
            database = st.text_input(t("db_sqlite_path", lang), (editing or {}).get("database", ""))
            host = ""; port = None; user = ""; pwd = ""
        else:
            port = e3.text_input(t("db_port", lang),
                                 str((editing or {}).get("port") or ENGINES[engine]["port"]))
            h1, h2 = st.columns([2, 1])
            host = h1.text_input(t("db_host", lang), (editing or {}).get("host", ""))
            database = h2.text_input(t("db_database", lang), (editing or {}).get("database", ""))
            u1, u2 = st.columns(2)
            user = u1.text_input(t("db_user", lang), (editing or {}).get("user", ""))
            _has_pwd = bool((editing or {}).get("save_password"))
            pwd = u2.text_input(t("db_password", lang),
                                value=stored_password(editing) if editing else "",
                                type="password")
        save_pwd = st.checkbox(t("db_save_pwd", lang), value=bool((editing or {}).get("save_password", True)))

        profile = {"conn_id": (editing or {}).get("conn_id"), "name": conn_name,
                   "engine": engine, "host": host,
                   "port": (port if not is_sqlite else None),
                   "database": database, "user": user, "password": pwd}

        b1, b2, b3 = st.columns(3)
        if b1.button(t("db_test", lang)):
            ok, msg = test_connection(profile, password=pwd)
            (st.success if ok else st.error)(msg)
        if b2.button(t("db_save", lang)):
            if not conn_name.strip():
                st.error(t("db_need_name", lang))
            else:
                save_connection(profile, save_password=save_pwd)
                st.success(t("db_saved_ok", lang))
        if editing is not None and b3.button(t("db_delete", lang)):
            delete_connection(editing["conn_id"])
            st.success(t("cl_deleted", lang))
        st.caption(t("db_local_note", lang))

        # Traer tablas: usa la conexión guardada (o la que se está probando)
        active = editing or (profile if (database or host) else None)
        if active is not None:
            try:
                tables = list_tables(active, password=pwd or None)
            except Exception as exc:  # noqa: BLE001
                tables = []
                st.warning(f"⚠️ {exc}")
            if tables:
                lim = st.number_input(t("db_limit", lang), 100, 100000, 10000, step=100)
                p1, p2 = st.columns([2, 1])
                table = p1.selectbox(t("db_pick_table", lang), tables)
                if p2.button(t("db_load", lang)):
                    try:
                        _render_profile(load_table(active, table, int(lim), password=pwd or None))
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"⚠️ {exc}")
                sql = st.text_area(t("db_query", lang), "")
                if sql.strip() and st.button(t("db_run_query", lang)):
                    try:
                        _render_profile(run_query(active, sql, int(lim), password=pwd or None))
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"⚠️ {exc}")
            else:
                st.caption(t("db_connect_first", lang))

# ---------------------------------------------------------------- BI & API
with tab_bi:
    st.info(t("bi_intro", lang), icon="📤")
    gov = governance_tables(lang)

    st.subheader(t("bi_files", lang))
    table_labels = {
        "catalog": t("tbl_catalog", lang),
        "dictionary": t("tbl_dictionary", lang),
        "quality_results": t("tbl_quality", lang),
        "lineage": t("tbl_lineage", lang),
        "glossary": t("tbl_glossary", lang),
        "policies": t("tbl_policies", lang),
        "kpis": t("tbl_kpis", lang),
    }
    pick = st.selectbox(t("bi_pick_table", lang), list(gov.keys()),
                        format_func=lambda k: table_labels.get(k, k))
    df = gov[pick]
    st.dataframe(df.head(8), width="stretch", hide_index=True)
    d1, d2, d3, d4 = st.columns(4)
    d1.download_button(t("bi_download_csv", lang), to_csv_bytes(df),
                       f"mvdg_{pick}_{lang}.csv", "text/csv",
                       width="stretch")
    d2.download_button(t("bi_download_xlsx", lang), to_excel_bytes(df, pick),
                       f"mvdg_{pick}_{lang}.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       width="stretch")
    d3.download_button(t("bi_download_json", lang), to_json_bytes(df),
                       f"mvdg_{pick}_{lang}.json", "application/json",
                       width="stretch")
    pq = to_parquet_bytes(df)
    if pq is not None:
        d4.download_button(t("bi_download_parquet", lang), pq,
                           f"mvdg_{pick}_{lang}.parquet",
                           "application/octet-stream", width="stretch")
    st.download_button(t("bi_export_all", lang), bi_bundle_xlsx(lang),
                       f"mvdg_bi_bundle_{lang}.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.subheader(t("bi_api", lang))
    st.markdown(t("bi_api_help", lang))
    base = "http://127.0.0.1:8600"
    st.code("\n".join([f"GET {base}/api/{name}?lang={lang}" for name in gov]) +
            f"\nGET {base}/api/catalog?lang={lang}&format=csv", language="http")
    st.caption(t("bi_guide", lang))

# ---------------------------------------------------------------- Empresas
with tab_cl:
    st.info(t("cl_intro", lang), icon="🏢")

    _R_LABEL = {"exe_ok": t("cl_r_exe", lang),
                "no_exe_python_ok": t("cl_r_noexe", lang),
                "solo_web": t("cl_r_web", lang)}
    _PACK_LABEL = {"A": t("cl_pack_a", lang), "B": t("cl_pack_b", lang),
                   "Web": t("cl_pack_web", lang)}

    existing = load_clients()
    options = [t("cl_new_option", lang)] + [
        f"{c.get('company', '?')} ({c.get('client_id', '')[:6]})" for c in existing]
    pick_cl = st.selectbox(t("cl_pick_edit", lang), options)
    editing = None
    if pick_cl != t("cl_new_option", lang):
        editing = existing[options.index(pick_cl) - 1]

    with st.form("client_form"):
        c1, c2, c3 = st.columns(3)
        company = c1.text_input(t("cl_company", lang),
                                (editing or {}).get("company", ""))
        country = c2.text_input(t("cl_country", lang),
                                (editing or {}).get("country", ""))
        industry = c3.text_input(t("cl_industry", lang),
                                 (editing or {}).get("industry", ""))
        c4, c5 = st.columns(2)
        contact_name = c4.text_input(t("cl_contact", lang),
                                     (editing or {}).get("contact_name", ""))
        contact_email = c5.text_input(t("cl_email", lang),
                                      (editing or {}).get("contact_email", ""))
        bi_default = (editing or {}).get("bi_tools", [])
        if isinstance(bi_default, str):
            bi_default = [b for b in bi_default.split(", ") if b in BI_TOOLS]
        bi_tools = st.multiselect(t("cl_bi", lang), BI_TOOLS, default=bi_default)
        c6, c7, c8 = st.columns(3)
        restr_current = (editing or {}).get("it_restriction", "no_exe_python_ok")
        restriction = c6.selectbox(
            t("cl_restriction", lang), IT_RESTRICTIONS,
            index=IT_RESTRICTIONS.index(restr_current)
            if restr_current in IT_RESTRICTIONS else 1,
            format_func=lambda k: _R_LABEL[k])
        maturity = c7.slider(t("cl_maturity", lang), 1, 5,
                             int((editing or {}).get("maturity", 2)))
        status_current = (editing or {}).get("status", "lead")
        status = c8.selectbox(t("cl_status", lang), STATUSES,
                              index=STATUSES.index(status_current)
                              if status_current in STATUSES else 0)
        notes = st.text_area(t("cl_notes", lang),
                             (editing or {}).get("notes", ""))
        submitted = st.form_submit_button(t("cl_save", lang))

    if submitted:
        if not company.strip():
            st.error(t("cl_need_name", lang))
        else:
            pack = recommended_pack(restriction)
            save_client({
                "client_id": (editing or {}).get("client_id"),
                "company": company.strip(), "country": country.strip(),
                "industry": industry.strip(),
                "contact_name": contact_name.strip(),
                "contact_email": contact_email.strip(),
                "bi_tools": ", ".join(bi_tools),
                "it_restriction": restriction,
                "recommended_pack": pack,
                "maturity": maturity, "status": status,
                "notes": notes.strip(),
            })
            st.success(f"{t('cl_saved', lang)} · {t('cl_pack', lang)}: "
                       f"{_PACK_LABEL[pack]}")

    if editing is not None:
        if st.button(t("cl_delete", lang)):
            delete_client(editing["client_id"])
            st.success(t("cl_deleted", lang))

    st.subheader(t("cl_list", lang))
    cdf = clients_df()
    if cdf.empty:
        st.caption(t("cl_empty", lang))
    else:
        show_cl = cdf.copy()
        show_cl["it_restriction"] = show_cl["it_restriction"].map(
            lambda k: _R_LABEL.get(k, k))
        show_cl["recommended_pack"] = show_cl["recommended_pack"].map(
            lambda k: _PACK_LABEL.get(k, k))
        st.dataframe(show_cl.rename(columns={
            "company": t("cl_company", lang), "country": t("cl_country", lang),
            "industry": t("cl_industry", lang),
            "contact_name": t("cl_contact", lang),
            "contact_email": t("cl_email", lang), "bi_tools": t("cl_bi", lang),
            "it_restriction": t("cl_restriction", lang),
            "recommended_pack": t("cl_pack", lang),
            "maturity": t("cl_maturity", lang), "status": t("cl_status", lang),
            "notes": t("cl_notes", lang),
        }).drop(columns=["client_id"]), width="stretch", hide_index=True)
        e1, e2 = st.columns(2)
        e1.download_button(t("bi_download_csv", lang), to_csv_bytes(cdf),
                           f"mvdg_empresas_{lang}.csv", "text/csv",
                           width="stretch")
        e2.download_button(t("bi_download_xlsx", lang),
                           to_excel_bytes(cdf, "empresas"),
                           f"mvdg_empresas_{lang}.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           width="stretch")
    st.caption(t("cl_where", lang).format(path=data_dir()))

# ------------------------------------------------------------------- Ayuda
with tab_h:
    st.info(t("h_intro", lang), icon="❓")

    st.subheader(t("h_matrix", lang))
    st.markdown(t("h_matrix_note", lang))
    _LEVEL_LABEL = {"auto": t("h_auto", lang), "partial": t("h_partial", lang),
                    "human": t("h_human", lang)}
    matrix_rows = automation_rows(lang)
    st.dataframe(pd.DataFrame([{
        t("h_area", lang): r["area"],
        t("h_level", lang): _LEVEL_LABEL[r["level"]],
        t("h_detail", lang): r["detail"],
    } for r in matrix_rows]), width="stretch", hide_index=True)

    st.subheader(t("h_speeches", lang))
    st.markdown(t("h_speeches_note", lang))
    for sp in speeches(lang):
        with st.expander(f"🎙️ {sp['title']}"):
            st.caption(f"{t('h_audience', lang)}: {sp['audience']}")
            st.markdown(sp["text"].replace("\n", "  \n"))

    st.subheader(t("h_packs", lang))
    st.markdown(t("h_packs_note", lang))
