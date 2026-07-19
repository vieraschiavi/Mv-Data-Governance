"""
MV Data Governance · Dashboard de escritorio (Streamlit).

Trilingüe (ES/EN/PT), estilo MV Kobra: navy + ámbar. Se ejecuta con el .bat,
con `streamlit run app/app.py` o empaquetado como .exe (PyInstaller).
"""
from __future__ import annotations

import json
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
from mvdg.connectors import (CLOUD_ENGINES, ENGINES, EXTRA_EXAMPLE,
                             delete_connection, list_tables,
                             load_connections, load_table, run_query,
                             save_connection, scan_all_connections,
                             stored_password, test_connection)
from mvdg.help_center import automation_rows, purview_collibra_faq, speeches
from mvdg.lab_case import lab_measure, lab_steps
from mvdg import azure_discovery
from mvdg import cobit_iso
from mvdg import collibra_export
from mvdg import collibra_pull
from mvdg import curation
from mvdg import enforcement
from mvdg import insights
from mvdg import mip_labels
from mvdg import orgchart
from mvdg import dmbok
from mvdg import mdm
from mvdg import glossary_auto
from mvdg import purview_export
from mvdg import purview_pull
from mvdg import imported as ext_imported
from mvdg import deliverable as case_deliverable
from mvdg import contracts as data_contracts
from mvdg import samples as ext_samples
from mvdg import scope as gov_scope
from mvdg import server as mvdg_server
from mvdg import workspace as ws
from mvdg.remediation import suggest_fix
from mvdg.ai_provider import ai_suggest_fix, configured_provider, provider_label
from mvdg.demo_data import load_demo_tables
from mvdg.exporters import (bi_bundle_xlsx, governance_tables, to_csv_bytes,
                            to_excel_bytes, to_json_bytes, to_parquet_bytes)
from mvdg.glossary import glossary_df, term_count
from mvdg.i18n import LANG_NAMES, LANGS, t
from mvdg.lineage import NODES, graph_from_lineage, lineage_df, lineage_figure
from mvdg import powerbi_meta as pbi
from mvdg import tableau_meta as tabl
from mvdg.ai_provider import (ai_parse_orgchart_image, ai_refactor_calc,
                              ai_refactor_dax)
from mvdg.policies import policies_df
from mvdg.profiler import profile_table, suggest_rules, summary
from mvdg.quality import (open_issues, overall_index, quality_by_dimension,
                          quality_by_dataset, quality_matrix, quality_trend,
                          run_rules)

# ----------------------------------------------------------------- página
st.set_page_config(page_title=APP_NAME, page_icon="🛡️", layout="wide")

# Guardián de integridad: si la carpeta se actualizó a medias (app.py nuevo con
# mvdg/ viejo o al revés), mostramos un cartel claro en vez de un traceback.
from mvdg import integrity as _integrity
_missing = _integrity.check_install()
if _missing:
    _glang = st.session_state.get("lang", "es")
    st.error(_integrity.MESSAGE.get(_glang, _integrity.MESSAGE["es"]))
    st.code("\n".join(_missing))
    st.stop()

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
    incl_samples = st.toggle(t("scope_toggle", lang), value=True, key="scope_samples")
    st.caption(t("scope_hint", lang))
    st.divider()
    st.caption(f"v{__version__} · {t('demo_note', lang)}")

if mvdg_server.auth_required() and not st.session_state.get("_mvdg_authed"):
    # Calienta el cache de datos ANTES del gate (no expone nada: son los
    # datasets sintéticos de demo, sin PII). Si no se calienta acá, la
    # primera vez que se calculan (justo en el rerun forzado por
    # st.rerun() al validar la contraseña) coincide con la reconstrucción
    # completa del script — con pyarrow en este entorno, esa combinación
    # puntual disparaba un segfault nativo reproducible en las pruebas.
    _tables()
    _results(lang)
    st.markdown(f"<span class='mv-badge'>MV · Data Governance Suite</span>", unsafe_allow_html=True)
    st.title(f"🔒 {t('auth_title', lang)}")
    st.caption(t("auth_intro", lang))
    _auth_pwd = st.text_input(t("auth_prompt", lang), type="password", key="auth_pwd_input")
    if st.button(t("auth_button", lang), type="primary"):
        if mvdg_server.check_password(_auth_pwd):
            st.session_state["_mvdg_authed"] = True
            st.rerun()
        else:
            st.error(t("auth_wrong", lang))
    st.stop()

st.markdown(f"<span class='mv-badge'>MV · Data Governance Suite</span>", unsafe_allow_html=True)
st.title(APP_NAME)
st.caption(t("app_tagline", lang))


@st.cache_data(show_spinner=False)
def _results_combined(lang: str):
    return gov_scope.combined_results(lang, _results(lang))


results = _results_combined(lang) if incl_samples else _results(lang)
tables = _tables()

(tab_ov, tab_lab, tab_dk, tab_cat, tab_mdm, tab_q, tab_lin, tab_con, tab_g, tab_cu, tab_resp,
 tab_p, tab_pr, tab_bi, tab_del, tab_pbi, tab_tab, tab_cl, tab_ws, tab_h) = st.tabs([
    t("tab_overview", lang), t("tab_lab", lang), t("tab_dmbok", lang),
    t("tab_catalog", lang), t("tab_mdm", lang), t("tab_quality", lang),
    t("tab_lineage", lang), t("tab_contracts", lang), t("tab_glossary", lang), t("tab_curation", lang),
    t("tab_responsibles", lang), t("tab_policies", lang), t("tab_profiler", lang),
    t("tab_bi", lang), t("tab_deliverable", lang), t("tab_pbi", lang), t("tab_tableau", lang),
    t("tab_clients", lang), t("tab_workspace", lang), t("tab_help", lang),
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
    cat = gov_scope.combined_catalog(lang, tables) if incl_samples else catalog_df(lang, tables)
    dic = gov_scope.combined_dictionary(lang) if incl_samples else dictionary_df(lang)
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

    # --- Insights del estado de gobierno (estilo Purview, 100% local) ---
    st.divider()
    st.subheader(t("gi_title", lang))
    st.caption(t("gi_caption", lang))
    _gi = insights.governance_summary(lang)
    g1, g2, g3, g4, g5, g6 = st.columns(6)
    g1.metric(t("gi_index", lang), f"{_gi['governance_index']} / 100")
    g2.metric(t("gi_owner", lang), f"{_gi['owner_pct']}%")
    g3.metric(t("gi_steward", lang), f"{_gi['steward_pct']}%")
    g4.metric(t("gi_classified", lang), f"{_gi['classified_pct']}%")
    g5.metric(t("gi_rules", lang), f"{_gi['rules_pct']}%")
    g6.metric(t("gi_curation", lang), f"{_gi['curation_pct']}%")
    with st.expander(t("gi_detail", lang), expanded=False):
        _gi_df = insights.governance_coverage(lang)
        _B = {True: "✅", False: "—"}
        st.dataframe(
            _gi_df.assign(owner_named=_gi_df["owner_named"].map(_B),
                          steward_named=_gi_df["steward_named"].map(_B),
                          classified=_gi_df["classified"].map(_B),
                          has_rules=_gi_df["has_rules"].map(_B))
            .rename(columns={
                "dataset": t("col_dataset", lang),
                "owner_named": t("gi_col_owner", lang),
                "steward_named": t("gi_col_steward", lang),
                "classified": t("gi_col_classified", lang),
                "has_rules": t("gi_col_rules", lang),
                "curation_pct": t("gi_col_curation", lang)}),
            width="stretch", hide_index=True)
        st.caption(t("gi_how_to_improve", lang))

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
    dk_sub1, dk_sub2, dk_sub3 = st.tabs([
        t("dk_subtab_dmbok", lang), t("dk_subtab_cobit", lang), t("dk_subtab_iso", lang)])

    with dk_sub1:
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

    with dk_sub2:
        st.info(t("co_intro", lang), icon="🎯")

        st.subheader(t("co_radar", lang))
        ccov = cobit_iso.cobit_coverage_summary()
        k1, k2, k3 = st.columns(3)
        k1.metric(t("co_covered", lang), ccov["covered"])
        k2.metric(t("co_partial", lang), ccov["partial"])
        k3.metric(t("co_out", lang), ccov["out"])
        cradar = cobit_iso.cobit_coverage_scores(lang)
        cr_theta = [name for name, _ in cradar] + [cradar[0][0]]
        cr_r = [score for _, score in cradar] + [cradar[0][1]]
        fig = go.Figure(go.Scatterpolar(r=cr_r, theta=cr_theta, fill="toself",
                                        line={"color": BRAND["amber"]},
                                        fillcolor="rgba(242,180,65,.25)"))
        fig.update_layout(**_PLOTLY_LAYOUT, height=460,
                          polar={"radialaxis": {"range": [0, 100], "color": BRAND["muted"]},
                                 "bgcolor": "rgba(255,255,255,.03)"})
        st.plotly_chart(fig, width="stretch", key="co_radar")

        st.subheader(t("co_objectives", lang))
        _CO_COV_LABEL = {"covered": t("h_dmbok_covered", lang),
                         "partial": t("h_dmbok_partial", lang),
                         "out": t("h_dmbok_out", lang)}
        for ob in cobit_iso.cobit_objectives(lang):
            with st.expander(f"{ob['code']}. {_CO_COV_LABEL[ob['coverage']]} — {ob['name']}"):
                st.markdown(f"**{t('dk_plain', lang)}:** {ob['plain']}")
                st.markdown(f"**{t('dk_tech', lang)}:** {ob['tech']}")
                st.markdown(f"**{t('dk_deliverables', lang)}:** {ob['deliverables']}")
                st.caption(ob["note"])

    with dk_sub3:
        st.info(t("iso_intro", lang), icon="🌐")

        st.subheader(t("iso_radar", lang))
        icov = cobit_iso.iso_coverage_summary()
        k1, k2, k3 = st.columns(3)
        k1.metric(t("iso_covered", lang), icov["covered"])
        k2.metric(t("iso_partial", lang), icov["partial"])
        k3.metric(t("iso_out", lang), icov["out"])
        iradar = cobit_iso.iso_coverage_scores(lang)
        ir_theta = [name for name, _ in iradar] + [iradar[0][0]]
        ir_r = [score for _, score in iradar] + [iradar[0][1]]
        fig = go.Figure(go.Scatterpolar(r=ir_r, theta=ir_theta, fill="toself",
                                        line={"color": BRAND["amber"]},
                                        fillcolor="rgba(242,180,65,.25)"))
        fig.update_layout(**_PLOTLY_LAYOUT, height=460,
                          polar={"radialaxis": {"range": [0, 100], "color": BRAND["muted"]},
                                 "bgcolor": "rgba(255,255,255,.03)"})
        st.plotly_chart(fig, width="stretch", key="iso_radar")

        st.subheader(t("iso_principles", lang))
        _ISO_COV_LABEL = {"covered": t("h_dmbok_covered", lang),
                          "partial": t("h_dmbok_partial", lang),
                          "out": t("h_dmbok_out", lang)}
        for pr in cobit_iso.iso_principles(lang):
            with st.expander(f"{_ISO_COV_LABEL[pr['coverage']]} — {pr['name']}"):
                st.markdown(pr["text"])
                st.caption(pr["note"])

        st.subheader(t("iso_vrc_title", lang))
        vrc_df = pd.DataFrame(cobit_iso.iso_vrc(lang))[["dim", "text", "mapped"]]
        st.dataframe(vrc_df.rename(columns={
            "dim": t("iso_vrc_col_dim", lang), "text": t("iso_vrc_col_text", lang),
            "mapped": t("iso_vrc_col_mapped", lang)}), width="stretch", hide_index=True)

# --------------------------------------------------------------- Catálogo
with tab_cat:
    st.info(t("cat_intro", lang), icon="📚")
    cat = gov_scope.combined_catalog(lang, tables) if incl_samples else catalog_df(lang, tables)
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
    _cat_ds_opts = dataset_names() + (ext_samples.sample_keys() if incl_samples else [])
    ds = st.selectbox(t("cat_pick", lang), _cat_ds_opts)
    dic = gov_scope.combined_dictionary(lang, ds) if incl_samples else dictionary_df(lang, ds)
    st.dataframe(dic.rename(columns={
        "column": t("col_column", lang), "type": t("col_type", lang),
        "pii": t("col_pii", lang), "business_term": t("col_term", lang),
        "description": t("col_description", lang),
    }).drop(columns=["dataset"]), width="stretch", hide_index=True)

# --------------------------------------------------------------------- MDM
with tab_mdm:
    st.info(t("mdm_intro", lang), icon="🔗")
    st.caption(t("mdm_warning", lang))

    _mdm_demo_options = {"dim_customers": tables["dim_customers"]}
    _mdm_sample_keys = ext_samples.sample_keys()
    mdm_source_names = list(_mdm_demo_options.keys()) + list(_mdm_sample_keys)

    def _mdm_label(key):
        if key in _mdm_demo_options:
            return f"🏠 dim_customers ({t('mdm_src_demo', lang)})"
        meta = ext_samples.sample_meta(key, lang)
        return f"🧪 {meta['name']}"

    mdm_pick = st.selectbox(t("mdm_pick_dataset", lang), mdm_source_names,
                            format_func=_mdm_label, key="mdm_pick_dataset")
    mdm_df = _mdm_demo_options[mdm_pick] if mdm_pick in _mdm_demo_options \
        else ext_samples.load_sample_table(mdm_pick)
    st.caption(f"{len(mdm_df):,} {t('mdm_rows_label', lang)} × {len(mdm_df.columns)} {t('mdm_cols_label', lang)}")

    all_cols = mdm_df.columns.tolist()
    _id_hints = ("id", "name", "nombre", "email", "correo", "document", "cedula", "documento")
    default_cols = [c for c in all_cols if any(h in c.lower() for h in _id_hints)][:4] or all_cols[:3]
    mdm_cols = st.multiselect(t("mdm_pick_columns", lang), all_cols, default=default_cols, key="mdm_cols")

    cat_like = [c for c in all_cols if 2 <= mdm_df[c].nunique() <= 30]
    _NO_BLOCK = t("mdm_no_block", lang)
    block_col = st.selectbox(t("mdm_block_column", lang), [_NO_BLOCK] + cat_like, key="mdm_block_col")
    block_col = None if block_col == _NO_BLOCK else block_col

    min_conf_pct = st.slider(t("mdm_min_confidence", lang), 0, 100, 50, step=5, key="mdm_min_conf")

    if st.button(t("mdm_run", lang), key="mdm_run_btn") and mdm_cols:
        try:
            with st.spinner(t("mdm_wait", lang)):
                mdm_rules = mdm.suggest_rules(mdm_df, mdm_cols)
                mdm_report = mdm.dedup_report(mdm_df, mdm_rules, min_confidence=min_conf_pct / 100,
                                              block_column=block_col)
                mdm_clusters = mdm.find_duplicate_clusters(mdm_df, mdm_rules, min_confidence=min_conf_pct / 100,
                                                           block_column=block_col)
            st.session_state["mdm_report"] = mdm_report
            st.session_state["mdm_clusters"] = mdm_clusters
            st.session_state["mdm_df_key"] = mdm_pick
        except ValueError as exc:
            st.error(str(exc), icon="⚠️")

    mdm_report = st.session_state.get("mdm_report")
    mdm_clusters = st.session_state.get("mdm_clusters")
    if mdm_report is not None and st.session_state.get("mdm_df_key") == mdm_pick:
        if mdm_report.empty:
            st.success(t("mdm_none_found", lang), icon="✅")
        else:
            st.subheader(t("mdm_results", lang).format(n=len(mdm_report)))
            st.dataframe(mdm_report.drop(columns="row_indices").rename(columns={
                "cluster_id": t("mdm_col_cluster", lang), "rows": t("mdm_col_rows", lang),
                "confidence": t("mdm_col_confidence", lang), "matched_on": t("mdm_col_matched", lang),
            }), width="stretch", hide_index=True)

            for _mc in mdm_clusters:
                _title = (f"🔗 {len(_mc.row_indices)} {t('mdm_rows_label', lang)} · "
                         f"{round(_mc.confidence * 100, 1)}% · {', '.join(_mc.matched_on) or '—'}")
                with st.expander(_title):
                    st.dataframe(mdm_df.loc[_mc.row_indices], width="stretch")
                    st.markdown(f"**{t('mdm_golden_title', lang)}**")
                    golden = mdm.build_golden_record(mdm_df, _mc)
                    st.dataframe(pd.DataFrame([golden]), width="stretch", hide_index=True)

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
    if incl_samples:
        _lin_nodes, _lin_edges = gov_scope.combined_lineage(lang)
    else:
        _lin_nodes, _lin_edges = NODES, None
    labels = {n["id"]: n["label"] for n in _lin_nodes}
    focus = st.selectbox(t("lin_focus", lang),
                         ["—"] + list(labels.keys()),
                         format_func=lambda k: labels.get(k, k))
    layer_titles = {
        "source": t("lin_layer_source", lang), "raw": t("lin_layer_raw", lang),
        "curated": t("lin_layer_curated", lang), "mart": t("lin_layer_mart", lang),
        "bi": t("lin_layer_bi", lang),
    }
    fig = lineage_figure(None if focus == "—" else focus, layer_titles,
                         nodes=_lin_nodes if incl_samples else None,
                         edges=_lin_edges)
    st.plotly_chart(fig, width="stretch")
    with st.expander(t("tbl_lineage", lang)):
        st.dataframe(gov_scope.combined_lineage_df(lang) if incl_samples else lineage_df(),
                     width="stretch", hide_index=True)

# --------------------------------------------------------------- Glosario
with tab_g:
    st.info(t("g_intro", lang), icon="📖")
    gdf = gov_scope.combined_glossary(lang) if incl_samples else glossary_df(lang)
    gq = st.text_input(t("g_search", lang), "")
    if gq:
        mask = gdf.apply(lambda r: gq.lower() in " ".join(map(str, r)).lower(), axis=1)
        gdf = gdf[mask]
    st.dataframe(gdf.rename(columns={
        "term": t("g_term", lang), "definition": t("g_definition", lang),
        "owner": t("col_owner", lang), "linked_datasets": t("g_linked", lang),
    }).drop(columns=["term_id"]), width="stretch", hide_index=True)

    st.divider()
    st.subheader(t("ga_title", lang))
    st.info(t("ga_intro", lang), icon="🗄️")
    _ga_conns = load_connections()
    if not _ga_conns:
        st.caption(t("ga_no_conn", lang))
    else:
        _ga_opts = [f"{c.get('name') or c.get('host')} ({ENGINES.get(c.get('engine'), {}).get('label', c.get('engine'))})"
                    for c in _ga_conns]
        _ga_pick = st.selectbox(t("ga_pick_conn", lang), _ga_opts)
        _ga_conn = _ga_conns[_ga_opts.index(_ga_pick)]
        if st.button(t("ga_generate", lang), type="primary", key="ga_generate_btn"):
            with st.spinner("…"):
                try:
                    _draft = glossary_auto.build_from_connection(
                        _ga_conn, lang, password=stored_password(_ga_conn) or None)
                    st.session_state["ga_draft"] = pd.DataFrame(_draft)
                except Exception as exc:  # noqa: BLE001
                    st.error(f"⚠️ {exc}")
        _ga_draft = st.session_state.get("ga_draft")
        if _ga_draft is not None and len(_ga_draft):
            n_exp = int(_ga_draft["expanded"].sum())
            st.success(t("ga_generated", lang).format(n=len(_ga_draft), exp=n_exp))
            st.caption(t("ga_edit_hint", lang))
            _ga_edited = st.data_editor(
                _ga_draft[["name", "definition", "table", "column"]],
                column_config={
                    "name": st.column_config.TextColumn(t("g_term", lang)),
                    "definition": st.column_config.TextColumn(t("g_definition", lang), width="large"),
                    "table": st.column_config.TextColumn(t("ga_col_table", lang), disabled=True),
                    "column": st.column_config.TextColumn(t("ga_col_column", lang), disabled=True),
                },
                width="stretch", hide_index=True, key="ga_editor")
            if st.button(t("ga_save", lang), key="ga_save_btn"):
                _records = []
                for i, row in _ga_edited.iterrows():
                    _records.append({
                        "database_id": _ga_draft.iloc[i]["database_id"],
                        "name": str(row["name"]).strip(),
                        "definition": str(row["definition"]).strip(),
                    })
                n = ext_imported.save_terms("database", _records)
                st.success(t("ga_saved_ok", lang).format(n=n))
                st.caption(t("ga_curation_note", lang))
        elif _ga_draft is not None:
            st.caption(t("ga_empty", lang))

# --------------------------------------------------------------- Curaduría
with tab_cu:
    st.info(t("cu_intro", lang), icon="🖊️")
    _cu_sum = curation.summary(lang)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("cu_total", lang), _cu_sum["total"])
    c2.metric(t("cu_pending", lang), _cu_sum["sugerido_ia"])
    c3.metric(t("cu_validated", lang), _cu_sum["validado"])
    c4.metric(t("cu_modified", lang), _cu_sum["modificado"])
    st.progress(_cu_sum["reviewed_pct"] / 100.0,
                text=t("cu_progress", lang).format(pct=_cu_sum["reviewed_pct"]))

    _cu_df = curation.list_items(lang)
    _CU_KIND = {"glossary": t("cu_kind_glossary", lang),
                "catalog": t("cu_kind_catalog", lang),
                "column": t("cu_kind_column", lang)}
    _CU_STATUS = {"sugerido_ia": t("cu_st_ai", lang),
                  "validado": t("cu_st_val", lang),
                  "modificado": t("cu_st_mod", lang)}
    f1, f2, f3 = st.columns(3)
    _cu_kind = f1.selectbox(t("cu_filter_kind", lang), ["(todos)"] + list(_CU_KIND),
                            format_func=lambda k: _CU_KIND.get(k, t("cu_all", lang)))
    _cu_ds = f2.selectbox(t("cu_filter_dataset", lang),
                          ["(todos)"] + sorted(_cu_df["dataset"].unique()))
    _cu_st = f3.selectbox(t("cu_filter_status", lang), ["(todos)"] + list(_CU_STATUS),
                          format_func=lambda k: _CU_STATUS.get(k, t("cu_all", lang)))
    _cu_view = _cu_df
    if _cu_kind != "(todos)":
        _cu_view = _cu_view[_cu_view["kind"] == _cu_kind]
    if _cu_ds != "(todos)":
        _cu_view = _cu_view[_cu_view["dataset"] == _cu_ds]
    if _cu_st != "(todos)":
        _cu_view = _cu_view[_cu_view["status"] == _cu_st]

    st.dataframe(
        _cu_view[["kind", "dataset", "label", "status", "text",
                  "responsible_name", "responsible_role", "validated_at"]]
        .assign(kind=lambda d: d["kind"].map(_CU_KIND),
                status=lambda d: d["status"].map(_CU_STATUS))
        .rename(columns={
            "kind": t("cu_col_kind", lang), "dataset": t("col_dataset", lang),
            "label": t("cu_col_item", lang), "status": t("cu_col_status", lang),
            "text": t("cu_col_text", lang),
            "responsible_name": t("cu_col_resp", lang),
            "responsible_role": t("cu_col_role", lang),
            "validated_at": t("cu_col_date", lang)}),
        width="stretch", hide_index=True, height=280)

    st.divider()
    st.subheader(t("cu_review_one", lang))
    if len(_cu_view):
        _cu_pick = st.selectbox(
            t("cu_pick", lang), _cu_view["item_id"].tolist(),
            format_func=lambda i: (
                f"{_CU_KIND[_cu_view.set_index('item_id').loc[i, 'kind']]} · "
                f"{_cu_view.set_index('item_id').loc[i, 'dataset']} · "
                f"{_cu_view.set_index('item_id').loc[i, 'label']}"))
        _cu_row = _cu_view.set_index("item_id").loc[_cu_pick]
        st.caption(t("cu_proposed", lang))
        st.markdown(f"> {_cu_row['proposed']}")
        if _cu_row["status"] != "sugerido_ia":
            st.success(t("cu_already", lang).format(
                status=_CU_STATUS[_cu_row["status"]], name=_cu_row["responsible_name"],
                role=_cu_row["responsible_role"], date=_cu_row["validated_at"]))
            if _cu_row["status"] == "modificado":
                st.markdown(f"**{t('cu_official_text', lang)}:** {_cu_row['text']}")

        _cu_action = st.radio(t("cu_action", lang), ["validar", "modificar"],
                              horizontal=True,
                              format_func=lambda a: t(f"cu_action_{a}", lang))
        _cu_newtext = ""
        if _cu_action == "modificar":
            _cu_newtext = st.text_area(t("cu_new_text", lang), _cu_row["text"])
        r1, r2 = st.columns(2)
        _cu_name = r1.text_input(t("cu_resp_name", lang),
                                 _cu_row["responsible_name"] or "")
        _cu_role = r2.text_input(t("cu_resp_role", lang),
                                 _cu_row["responsible_role"] or _cu_row["default_owner"])
        _cu_notes = st.text_input(t("cu_notes", lang), _cu_row["notes"] or "")
        b1, b2 = st.columns(2)
        if b1.button(t("cu_save", lang), type="primary"):
            try:
                curation.save_validation(
                    _cu_pick, lang,
                    "modificado" if _cu_action == "modificar" else "validado",
                    _cu_newtext, _cu_name, _cu_role, _cu_notes)
                st.success(t("cu_saved", lang))
                st.rerun()
            except ValueError:
                st.error(t("cu_need_name", lang))
        if _cu_row["status"] != "sugerido_ia" and b2.button(t("cu_reset", lang)):
            curation.reset_item(_cu_pick, lang)
            st.success(t("cu_reset_ok", lang))
            st.rerun()
    st.caption(t("cu_local_note", lang))

    st.divider()
    st.subheader(t("cu_bulk_title", lang))
    st.caption(t("cu_bulk_intro", lang))
    _cub_ds_opts = sorted(_cu_df["dataset"].unique().tolist())
    cb1, cb2, cb3 = st.columns(3)
    _cub_ds = cb1.selectbox(t("cu_bulk_pick", lang), _cub_ds_opts, key="cu_bulk_ds")
    _cub_name = cb2.text_input(t("cu_resp_name", lang), key="cu_bulk_name")
    _cub_role = cb3.text_input(t("cu_resp_role", lang), key="cu_bulk_role")
    _cub_pending = _cu_df[(_cu_df["dataset"] == _cub_ds)
                          & (_cu_df["status"] == "sugerido_ia")]
    if st.button(t("cu_bulk_btn", lang).format(n=len(_cub_pending)),
                 key="cu_bulk_btn", disabled=len(_cub_pending) == 0):
        if not _cub_name.strip():
            st.error(t("cu_need_name", lang))
        else:
            for _, _it in _cub_pending.iterrows():
                curation.save_validation(_it["item_id"], lang, "validado", "",
                                         _cub_name, _cub_role)
            st.success(t("cu_bulk_done", lang).format(
                n=len(_cub_pending), name=_cub_name.strip()))
            st.rerun()
    st.caption(t("cu_bulk_note", lang))

# ------------------------------------------------------------- Responsables
with tab_resp:
    st.info(t("rs_intro", lang), icon="👥")

    _RS_SRC = {"file": t("rs_src_file", lang), "photo": t("rs_src_photo", lang),
               "saved": t("rs_src_saved", lang)}
    rs_src = st.radio(t("rs_source", lang), list(_RS_SRC), horizontal=True,
                      key="rs_source", format_func=lambda k: _RS_SRC[k])

    org_df = st.session_state.get("rs_org")
    if rs_src == "file":
        rs_up = st.file_uploader(t("rs_upload", lang), type=["xlsx", "xls", "csv"],
                                 key="rs_up")
        st.caption(t("rs_upload_hint", lang))
        if rs_up is not None:
            try:
                raw = (pd.read_csv(rs_up) if rs_up.name.lower().endswith(".csv")
                       else pd.read_excel(rs_up))
                org_df = orgchart.parse_org_table(raw)
                st.session_state["rs_org"] = org_df
                st.success(t("rs_parsed", lang).format(n=len(org_df)))
            except ValueError as exc:
                st.error(f"⚠️ {exc}")
            except Exception as exc:  # noqa: BLE001 - archivo corrupto
                st.error(f"⚠️ {exc}")
    elif rs_src == "photo":
        _rs_provider = configured_provider()
        if not _rs_provider:
            st.warning(t("rs_photo_needs_ai", lang))
        else:
            st.warning(t("rs_photo_disclosure", lang).format(
                provider=provider_label(_rs_provider)))
            rs_img = st.file_uploader(t("rs_upload_photo", lang),
                                      type=["png", "jpg", "jpeg", "webp"], key="rs_img")
            if rs_img is not None and st.button(t("rs_extract_photo", lang)):
                _mt = ("image/png" if rs_img.name.lower().endswith(".png")
                       else "image/webp" if rs_img.name.lower().endswith(".webp")
                       else "image/jpeg")
                with st.spinner("…"):
                    people = ai_parse_orgchart_image(rs_img.getvalue(), _mt, lang,
                                                     _rs_provider)
                if people:
                    org_df = pd.DataFrame(people)
                    st.session_state["rs_org"] = org_df
                    st.success(t("rs_parsed", lang).format(n=len(org_df)))
                else:
                    st.error(t("rs_photo_failed", lang))
    else:
        org_df = orgchart.load_org()
        if org_df is None:
            st.caption(t("rs_none_saved", lang))
        else:
            st.session_state["rs_org"] = org_df

    if org_df is not None and len(org_df):
        st.subheader(t("rs_people", lang))
        st.caption(t("rs_people_edit_hint", lang))
        org_edit = st.data_editor(org_df, width="stretch", num_rows="dynamic",
                                  key="rs_org_editor")
        if st.button(t("rs_save_org", lang)):
            orgchart.save_org(org_edit)
            st.session_state["rs_org"] = org_edit
            st.success(t("rs_org_saved", lang))

        st.divider()
        st.subheader(t("rs_assignments", lang))
        saved_asg = orgchart.load_assignments()
        if st.button(t("rs_suggest", lang), type="primary"):
            st.session_state["rs_asg"] = orgchart.suggest_assignments(org_edit)
        asg_df = st.session_state.get("rs_asg")
        if asg_df is None and saved_asg is not None:
            asg_df = saved_asg
        if asg_df is not None:
            st.caption(t("rs_asg_hint", lang))
            asg_edit = st.data_editor(
                asg_df, width="stretch", key="rs_asg_editor",
                column_config={
                    "dataset": st.column_config.TextColumn(t("col_dataset", lang), disabled=True),
                    "domain": st.column_config.TextColumn(t("cat_domain", lang), disabled=True),
                    "owner_name": st.column_config.TextColumn(t("rs_owner_name", lang)),
                    "owner_role": st.column_config.TextColumn(t("rs_owner_role", lang)),
                    "steward_name": st.column_config.TextColumn(t("rs_steward_name", lang)),
                    "steward_role": st.column_config.TextColumn(t("rs_steward_role", lang)),
                    "match": st.column_config.TextColumn(t("rs_match", lang), disabled=True),
                    "estado": st.column_config.TextColumn(t("rs_estado", lang), disabled=True),
                })
            if st.button(t("rs_save_asg", lang)):
                base = st.session_state.get("rs_asg")
                if base is not None and len(base) == len(asg_edit):
                    changed = (asg_edit[["owner_name", "owner_role",
                                         "steward_name", "steward_role"]]
                               != base[["owner_name", "owner_role",
                                        "steward_name", "steward_role"]]).any(axis=1)
                    asg_edit = asg_edit.copy()
                    asg_edit.loc[changed, "estado"] = "editado"
                orgchart.save_assignments(asg_edit)
                st.session_state["rs_asg"] = asg_edit
                st.success(t("rs_asg_saved", lang))
    st.caption(t("rs_local_note", lang))

# --------------------------------------------------------------- Políticas
with tab_p:
    st.info(t("p_intro", lang), icon="🛡️")
    if incl_samples:
        pdf = policies_df(lang, results,
                          catalog=gov_scope.combined_catalog(lang, tables),
                          dictionary=gov_scope.combined_dictionary(lang))
    else:
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
def _render_profile(user_df, dataset_name: str | None = None):
    """Perfila y muestra un DataFrame (venga de archivo o de base de datos).
    Además lo deja disponible en session_state para guardarlo en el proyecto
    del cliente (pestaña 📁 Proyecto), así el trabajo no se pierde."""
    if user_df is None or not len(user_df):
        return
    if dataset_name:
        st.session_state["current_dataset"] = user_df
        st.session_state["current_dataset_name"] = dataset_name
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
            _render_profile(user_df, dataset_name=up.name if up is not None else None)
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
        engine = e1.selectbox(t("db_engine", lang), engine_keys, key="db_engine_pick",
                              index=engine_keys.index((editing or {}).get("engine", "postgresql"))
                              if (editing or {}).get("engine") in engine_keys else 0,
                              format_func=lambda k: ENGINES[k]["label"])
        conn_name = e2.text_input(t("db_name", lang), (editing or {}).get("name", ""))
        is_sqlite = engine == "sqlite"
        is_cloud = engine in CLOUD_ENGINES
        extra_raw = ""
        if is_sqlite:
            database = st.text_input(t("db_sqlite_path", lang), (editing or {}).get("database", ""))
            host = ""; port = None; user = ""; pwd = ""
        else:
            if is_cloud:
                e3.caption(t("db_cloud_no_port", lang))
                port = None
                h1, h2 = st.columns([2, 1])
                host = h1.text_input(t("db_host", lang), (editing or {}).get("host", ""))
                database = h2.text_input(t("db_database", lang), (editing or {}).get("database", ""))
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
            if is_cloud:
                _extra_default = (editing or {}).get("extra") or EXTRA_EXAMPLE.get(engine, {})
                extra_raw = st.text_area(
                    t("db_extra_params", lang),
                    json.dumps(_extra_default, ensure_ascii=False, indent=2),
                    height=130)
                st.caption(t("db_extra_hint", lang).format(
                    example=json.dumps(EXTRA_EXAMPLE.get(engine, {}), ensure_ascii=False)))
        save_pwd = st.checkbox(t("db_save_pwd", lang), value=bool((editing or {}).get("save_password", True)))

        extra_parsed = {}
        if is_cloud and extra_raw.strip():
            try:
                extra_parsed = json.loads(extra_raw)
                if not isinstance(extra_parsed, dict):
                    raise ValueError
            except ValueError:
                st.error(t("db_extra_invalid_json", lang))

        profile = {"conn_id": (editing or {}).get("conn_id"), "name": conn_name,
                   "engine": engine, "host": host,
                   "port": (port if not is_sqlite and not is_cloud else None),
                   "database": database, "user": user, "password": pwd,
                   "extra": extra_parsed}

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
        active = editing or (profile if (database or host or extra_parsed) else None)
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
                        _render_profile(load_table(active, table, int(lim), password=pwd or None),
                                        dataset_name=table)
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"⚠️ {exc}")
                sql = st.text_area(t("db_query", lang), "")
                if sql.strip() and st.button(t("db_run_query", lang)):
                    try:
                        _render_profile(run_query(active, sql, int(lim), password=pwd or None),
                                        dataset_name="query_result")
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"⚠️ {exc}")
            else:
                st.caption(t("db_connect_first", lang))

# ---------------------------------------------------------------- BI & API
with tab_bi:
    st.info(t("bi_intro", lang), icon="📤")
    gov = governance_tables(lang, include_samples=incl_samples)

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

    st.divider()
    st.subheader(t("mig_title", lang))
    st.info(t("mig_intro", lang), icon="🔀")

    def _curation_lookup_factory(prefix):
        def lookup(term_id):
            rec = curation.get_record(f"{prefix}:{term_id}", lang)
            return (rec["status"], rec.get("text") or "") if rec else ("sugerido_ia", "")
        return lookup

    mig_target = st.radio(t("mig_target", lang), ["purview", "collibra"], horizontal=True,
                          format_func=lambda k: "Microsoft Purview" if k == "purview" else "Collibra")
    _mig_cat, _mig_dic, _mig_glo = gov["catalog"], gov["dictionary"], gov["glossary"]
    _mig_lookup = _curation_lookup_factory("glossary:demo")

    if mig_target == "purview":
        _mig_ready = purview_export.configured()
        st.caption(t("mig_purview_env", lang) if not _mig_ready else t("mig_configured", lang))
        if st.button(t("mig_preview", lang), key="mig_prev_pv"):
            st.session_state["mig_result"] = purview_export.push_all(
                _mig_cat, _mig_dic, _mig_glo, curation_lookup=_mig_lookup, dry_run=True)
        if _mig_ready and st.button(t("mig_push", lang), type="primary", key="mig_push_pv"):
            with st.spinner("…"):
                try:
                    st.session_state["mig_result"] = purview_export.push_all(
                        _mig_cat, _mig_dic, _mig_glo, curation_lookup=_mig_lookup, dry_run=False)
                    st.success(t("mig_done", lang))
                except Exception as exc:  # noqa: BLE001
                    st.error(f"⚠️ {exc}")
    else:
        _mig_ready = collibra_export.catalog_configured()
        st.caption(t("mig_collibra_env", lang) if not _mig_ready else t("mig_configured", lang))
        if st.button(t("mig_preview", lang), key="mig_prev_cb"):
            st.session_state["mig_result"] = collibra_export.push_all(
                _mig_cat, _mig_dic, _mig_glo, curation_lookup=_mig_lookup, dry_run=True)
        if _mig_ready and st.button(t("mig_push", lang), type="primary", key="mig_push_cb"):
            with st.spinner("…"):
                try:
                    st.session_state["mig_result"] = collibra_export.push_all(
                        _mig_cat, _mig_dic, _mig_glo, curation_lookup=_mig_lookup, dry_run=False)
                    st.success(t("mig_done", lang))
                except Exception as exc:  # noqa: BLE001
                    st.error(f"⚠️ {exc}")

    _mig_res = st.session_state.get("mig_result")
    if _mig_res is not None:
        c1, c2 = st.columns(2)
        c1.metric(t("mig_entities", lang), _mig_res["catalog"].get(
            "entity_count", _mig_res["catalog"].get("asset_count", 0)))
        c2.metric(t("mig_terms", lang), _mig_res["glossary"]["term_count"])
        with st.expander(t("mig_detail", lang)):
            st.json(_mig_res)
    st.caption(t("mig_local_note", lang))

    st.divider()
    st.subheader(t("enf_title", lang))
    st.warning(t("enf_intro", lang), icon="🔒")
    e1, e2 = st.columns(2)
    enf_engine = e1.selectbox(t("enf_engine", lang), enforcement.SUPPORTED_MASKING_ENGINES,
                              format_func=lambda k: "PostgreSQL" if k == "postgresql" else "SQL Server")
    _CLASS_OPTS = sorted(_mig_cat["classification"].unique().tolist())
    with st.expander(f"❓ {t('enf_roles', lang)}", expanded=False):
        st.markdown(t("enf_roles_explain", lang))
    enf_roles_raw = st.text_area(
        t("enf_roles", lang),
        "\n".join(f"{c}: rol_{c.lower()}" for c in _CLASS_OPTS),
        help=t("enf_roles_help", lang))
    enf_roles = {}
    for line in enf_roles_raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            enf_roles.setdefault(k.strip(), []).append(v.strip())
    if st.button(t("enf_generate", lang)):
        _enf_plan = enforcement.enforcement_plan(_mig_cat, _mig_dic, enf_roles, engine=enf_engine)
        st.session_state["enf_plan"] = _enf_plan
    _enf_plan = st.session_state.get("enf_plan")
    if _enf_plan is not None:
        f1, f2 = st.columns(2)
        f1.metric(t("enf_grants", lang), _enf_plan["grant_statements"])
        f2.metric(t("enf_masks", lang), _enf_plan["masking_statements"])
        st.code(_enf_plan["script"], language="sql")
        st.download_button(t("enf_download", lang), _enf_plan["script"],
                           f"mvdg_enforcement_{enf_engine}.sql", "text/plain")
    st.caption(t("enf_local_note", lang))

    st.divider()
    st.subheader(t("mip_title", lang))
    st.info(t("mip_intro", lang), icon="🏷️")
    _mip_ready = mip_labels.configured()
    st.caption(t("mip_env", lang) if not _mip_ready else t("mig_configured", lang))
    st.caption(t("mip_scope_note", lang))
    mip_map_raw = st.text_area(
        t("mip_file_map", lang), "",
        placeholder="dim_customers: https://empresa.sharepoint.com/:x:/s/team/EjEMPLO",
        help=t("mip_file_map_help", lang))
    _mip_file_map = {}
    for line in mip_map_raw.splitlines():
        if ":" not in line:
            continue
        ds, url = line.split(":", 1)
        ds, url = ds.strip(), url.strip()
        if not ds or not url:
            continue
        try:
            resolved = mip_labels.resolve_share_url(url) if _mip_ready else None
        except Exception as exc:  # noqa: BLE001
            st.error(f"⚠️ {ds}: {exc}")
            resolved = None
        if resolved and resolved.get("itemId"):
            _mip_file_map[ds] = resolved
        elif not _mip_ready:
            st.caption(t("mip_needs_creds_to_resolve", lang).format(dataset=ds))
    if st.button(t("mip_preview", lang), key="mip_prev"):
        st.session_state["mip_result"] = mip_labels.push_labels(_mig_cat, _mip_file_map, dry_run=True)
    if _mip_ready and _mip_file_map and st.button(t("mip_push", lang), type="primary", key="mip_push"):
        with st.spinner("…"):
            try:
                st.session_state["mip_result"] = mip_labels.push_labels(
                    _mig_cat, _mip_file_map, dry_run=False)
                st.success(t("mig_done", lang))
            except Exception as exc:  # noqa: BLE001
                st.error(f"⚠️ {exc}")
    _mip_res = st.session_state.get("mip_result")
    if _mip_res is not None:
        st.dataframe(pd.DataFrame(_mip_res["plan"]) if _mip_res["plan"] else pd.DataFrame(),
                    width="stretch", hide_index=True)
        if _mip_res.get("skipped_no_file"):
            st.caption(t("mip_skipped", lang).format(datasets=", ".join(_mip_res["skipped_no_file"])))
    st.caption(t("mip_local_note", lang))

    st.divider()
    st.subheader(t("scanall_title", lang))
    st.caption(t("scanall_intro", lang))
    if st.button(t("scanall_run", lang)):
        with st.spinner("…"):
            st.session_state["scanall_result"] = scan_all_connections()
    _scanall_res = st.session_state.get("scanall_result")
    if _scanall_res is not None:
        if len(_scanall_res):
            n_ok = int(_scanall_res["error"].isna().sum())
            n_err = int(_scanall_res["error"].notna().sum())
            g1, g2 = st.columns(2)
            g1.metric(t("scanall_tables", lang), n_ok)
            g2.metric(t("scanall_errors", lang), n_err)
            st.dataframe(_scanall_res, width="stretch", hide_index=True)
        else:
            st.caption(t("scanall_none", lang))
    st.caption(t("scanall_local_note", lang))

    st.divider()
    st.subheader(t("azd_title", lang))
    st.info(t("azd_intro", lang), icon="☁️")
    _azd_ready = azure_discovery.configured()
    st.caption(t("azd_env", lang) if not _azd_ready else t("mig_configured", lang))
    if _azd_ready and st.button(t("azd_run", lang), type="primary"):
        with st.spinner("…"):
            try:
                st.session_state["azd_result"] = azure_discovery.discover_data_resources()
            except Exception as exc:  # noqa: BLE001
                st.error(f"⚠️ {exc}")
    _azd_res = st.session_state.get("azd_result")
    if _azd_res is not None:
        if len(_azd_res):
            st.metric(t("azd_found", lang), len(_azd_res))
            st.dataframe(_azd_res, width="stretch", hide_index=True)
        else:
            st.caption(t("azd_none", lang))
    st.caption(t("azd_local_note", lang))

    st.divider()
    st.subheader(t("cbp_title", lang))
    st.info(t("cbp_intro", lang), icon="⬇️")
    _cbp_ready = collibra_export.configured()
    st.caption(t("cbp_env", lang) if not _cbp_ready else t("mig_configured", lang))
    if _cbp_ready and st.button(t("cbp_run", lang), type="primary"):
        with st.spinner("…"):
            try:
                st.session_state["cbp_result"] = collibra_pull.pull_all()
            except Exception as exc:  # noqa: BLE001
                st.error(f"⚠️ {exc}")
    _cbp_res = st.session_state.get("cbp_result")
    if _cbp_res is not None:
        h1, h2 = st.columns(2)
        h1.metric(t("cbp_terms", lang), _cbp_res["glossary"]["term_count"])
        h2.metric(t("cbp_tables", lang), _cbp_res["catalog"]["table_count"])
        if _cbp_res["glossary"]["terms"]:
            _cbp_terms_df = pd.DataFrame(_cbp_res["glossary"]["terms"])
            st.dataframe(_cbp_terms_df, width="stretch", hide_index=True)
            st.download_button(t("cbp_download_terms", lang), to_csv_bytes(_cbp_terms_df),
                               "collibra_terminos.csv", "text/csv")
        if _cbp_res["catalog"].get("skipped_reason"):
            st.caption(f"📚 {t('cbp_catalog_skipped', lang)}: {_cbp_res['catalog']['skipped_reason']}")
        elif _cbp_res["catalog"]["tables"]:
            _cbp_tables_df = pd.DataFrame(_cbp_res["catalog"]["tables"])
            st.dataframe(_cbp_tables_df, width="stretch", hide_index=True)
            st.download_button(t("cbp_download_tables", lang), to_csv_bytes(_cbp_tables_df),
                               "collibra_tablas.csv", "text/csv")
        if st.button(t("imp_save", lang), key="imp_save_cb"):
            n1 = ext_imported.save_terms("collibra", _cbp_res["glossary"]["terms"])
            n2 = ext_imported.save_tables("collibra", _cbp_res["catalog"]["tables"])
            st.success(t("imp_saved_ok", lang).format(n=n1 + n2))
    st.caption(t("cbp_local_note", lang))

    st.divider()
    st.subheader(t("pvp_title", lang))
    st.info(t("pvp_intro", lang), icon="⬇️")
    _pvp_ready = purview_pull.configured()
    st.caption(t("pvp_env", lang) if not _pvp_ready else t("mig_configured", lang))
    if _pvp_ready and st.button(t("pvp_run", lang), type="primary"):
        with st.spinner("…"):
            try:
                st.session_state["pvp_result"] = purview_pull.pull_all()
            except Exception as exc:  # noqa: BLE001
                st.error(f"⚠️ {exc}")
    _pvp_res = st.session_state.get("pvp_result")
    if _pvp_res is not None:
        pv1, pv2 = st.columns(2)
        pv1.metric(t("pvp_terms", lang), _pvp_res["glossary"]["term_count"])
        pv2.metric(t("cbp_tables", lang), _pvp_res["catalog"]["table_count"])
        if _pvp_res["glossary"]["terms"]:
            _pvp_terms_df = pd.DataFrame(_pvp_res["glossary"]["terms"])
            st.dataframe(_pvp_terms_df, width="stretch", hide_index=True)
            st.download_button(t("pvp_download_terms", lang), to_csv_bytes(_pvp_terms_df),
                               "purview_terminos.csv", "text/csv")
        if _pvp_res["catalog"]["tables"]:
            _pvp_tables_df = pd.DataFrame(_pvp_res["catalog"]["tables"])
            st.dataframe(_pvp_tables_df, width="stretch", hide_index=True)
            st.download_button(t("cbp_download_tables", lang), to_csv_bytes(_pvp_tables_df),
                               "purview_tablas.csv", "text/csv")
        if st.button(t("imp_save", lang), key="imp_save_pv"):
            n1 = ext_imported.save_terms("purview", _pvp_res["glossary"]["terms"])
            n2 = ext_imported.save_tables("purview", _pvp_res["catalog"]["tables"])
            st.success(t("imp_saved_ok", lang).format(n=n1 + n2))
    st.caption(t("pvp_local_note", lang))

    _imp_terms, _imp_tables = ext_imported.list_terms(), ext_imported.list_tables()
    if len(_imp_terms) or len(_imp_tables):
        st.divider()
        st.subheader(t("imp_title", lang))
        st.caption(t("imp_intro", lang))
        if len(_imp_terms):
            st.dataframe(_imp_terms, width="stretch", hide_index=True)
        if len(_imp_tables):
            st.dataframe(_imp_tables, width="stretch", hide_index=True)
        st.caption(t("imp_curation_note", lang))

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
        # cada estado se muestra con su significado entre paréntesis (el valor
        # guardado sigue siendo la clave corta: lead, demo, piloto...)
        status = c8.selectbox(t("cl_status", lang), STATUSES,
                              index=STATUSES.index(status_current)
                              if status_current in STATUSES else 0,
                              format_func=lambda k: t(f"cl_st_{k}", lang))
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

# ---------------------------------------------------------------- Proyecto
with tab_ws:
    st.info(t("ws_intro", lang), icon="📁")
    ws_clients = load_clients()
    if not ws_clients:
        st.warning(t("ws_no_clients", lang), icon="🏢")
    else:
        ws_opts = {f"{c.get('company', '?')} ({c.get('client_id', '')[:6]})": c
                   for c in ws_clients}
        ws_pick = st.selectbox(t("ws_pick_client", lang), list(ws_opts.keys()),
                               key="ws_pick_client")
        ws_client = ws_opts[ws_pick]
        ws_cid = ws_client["client_id"]

        summ = ws.project_summary(ws_cid)
        s1, s2, s3, s4 = st.columns(4)
        s1.metric(t("ws_summary_stages", lang), summ["stages"])
        s2.metric(t("ws_summary_tables", lang), summ["tables"])
        s3.metric(t("ws_summary_rows", lang), f"{summ['rows']:,}")
        s4.metric(t("ws_summary_updated", lang), (summ["updated_at"] or "—")[:10])

        # --- Guardar etapa actual ---
        st.subheader(t("ws_save_title", lang))
        st.caption(t("ws_capture_hint", lang))

        # Reúne lo que hay disponible ahora mismo en la sesión para capturar.
        candidates: dict[str, tuple] = {}
        _cur_ds = st.session_state.get("current_dataset")
        if isinstance(_cur_ds, pd.DataFrame) and not _cur_ds.empty:
            _nm = st.session_state.get("current_dataset_name", "dataset")
            candidates["dataset"] = (
                t("ws_include_dataset", lang).format(name=_nm), {"dataset": _cur_ds})
        _mdm_rep = st.session_state.get("mdm_report")
        if isinstance(_mdm_rep, pd.DataFrame) and not _mdm_rep.empty:
            candidates["mdm"] = (
                t("ws_include_mdm", lang),
                {"mdm_report": _mdm_rep.drop(columns="row_indices", errors="ignore")})
        _pbi_res = st.session_state.get("pbi_tenant_result")
        if isinstance(_pbi_res, dict):
            _pt = {f"powerbi_{k}": v for k, v in _pbi_res.items()
                   if isinstance(v, pd.DataFrame) and not v.empty}
            if _pt:
                candidates["powerbi"] = (t("ws_include_powerbi", lang), _pt)
        _tab_res = st.session_state.get("tab_scan_result")
        if isinstance(_tab_res, dict):
            _tt = {f"tableau_{k}": v for k, v in _tab_res.items()
                   if isinstance(v, pd.DataFrame) and not v.empty}
            if _tt:
                candidates["tableau"] = (t("ws_include_tableau", lang), _tt)
        # El paquete de gobierno (9 tablas) siempre está disponible.
        candidates["governance"] = (t("ws_include_governance", lang), None)

        chosen = []
        for _key, (_label, _tbls) in candidates.items():
            if st.checkbox(_label, key=f"ws_inc_{_key}", value=(_key == "dataset")):
                chosen.append(_key)

        ws_name = st.text_input(t("ws_stage_name", lang), key="ws_stage_name_in")
        ws_notes = st.text_area(t("ws_stage_notes", lang), key="ws_stage_notes_in")
        if st.button(t("ws_save_btn", lang), key="ws_save_stage_btn"):
            if not ws_name.strip():
                st.error(t("ws_need_name", lang))
            elif not chosen:
                st.error(t("ws_need_selection", lang))
            else:
                _tables: dict = {}
                for _key in chosen:
                    if _key == "governance":
                        for _gk, _gv in governance_tables(lang).items():
                            _tables[f"gob_{_gk}"] = _gv
                    else:
                        _tables.update(candidates[_key][1])
                _kind = chosen[0] if len(chosen) == 1 else "mixto"
                try:
                    _m = ws.save_stage(ws_cid, ws_name, _tables, kind=_kind,
                                       notes=ws_notes,
                                       meta={"lang": lang, "artifacts": chosen})
                    st.success(t("ws_saved_ok", lang).format(
                        name=_m["name"], n=len(_m["tables"])))
                except ValueError as exc:
                    st.error(str(exc), icon="⚠️")

        # --- Etapas guardadas ---
        st.subheader(t("ws_stages_title", lang))
        _stages = ws.list_stages(ws_cid)
        if not _stages:
            st.caption(t("ws_no_stages", lang))
        for _sm in _stages:
            _sid = _sm["stage_id"]
            _hdr = (f"📌 {_sm['name']} · {_sm.get('kind', '')} · "
                    f"{_sm.get('created_at', '')[:16].replace('T', ' ')}")
            with st.expander(_hdr):
                if _sm.get("notes"):
                    st.caption(_sm["notes"])
                _tinfo = pd.DataFrame([{
                    t("ws_col_table", lang): _e["name"],
                    t("col_rows", lang): _e["rows"],
                    t("col_column", lang): _e["cols"],
                } for _e in _sm.get("tables", [])])
                st.dataframe(_tinfo, hide_index=True, width="stretch")
                _cc1, _cc2 = st.columns(2)
                if _cc1.button(t("ws_reload", lang), key=f"ws_reload_{_sid}"):
                    st.session_state["ws_open_stage"] = _sid
                if _cc2.button(t("ws_delete", lang), key=f"ws_del_{_sid}"):
                    ws.delete_stage(ws_cid, _sid)
                    if st.session_state.get("ws_open_stage") == _sid:
                        st.session_state["ws_open_stage"] = None
                    st.success(t("ws_deleted", lang))
                if st.session_state.get("ws_open_stage") == _sid:
                    _loaded = ws.load_stage(ws_cid, _sid)
                    for _tname, _tdf in _loaded["loaded_tables"].items():
                        st.markdown(f"**{_tname}** — {len(_tdf):,} × {_tdf.shape[1]}")
                        st.dataframe(_tdf.head(50), width="stretch", hide_index=True)
                        st.download_button(
                            t("bi_download_csv", lang), to_csv_bytes(_tdf),
                            f"{_sm['name']}_{_tname}.csv".replace(" ", "_"),
                            "text/csv", key=f"ws_dl_{_sid}_{_tname}")

        # --- Exportar / importar el proyecto completo ---
        st.subheader(t("ws_export_title", lang))
        st.caption(t("ws_export_hint", lang))
        _ex1, _ex2 = st.columns(2)
        _ex1.download_button(t("ws_export_btn", lang), ws.export_project(ws_cid),
                             f"proyecto_{ws_cid[:6]}.zip", "application/zip",
                             width="stretch")
        _up_zip = _ex2.file_uploader(t("ws_import_btn", lang), type=["zip"],
                                     key="ws_import_zip")
        _ws_replace = st.checkbox(t("ws_import_replace", lang), key="ws_import_replace")
        if _up_zip is not None and st.button(t("ws_do_import", lang), key="ws_do_import"):
            try:
                _n = ws.import_project(ws_cid, _up_zip.read(), replace=_ws_replace)
                st.success(t("ws_imported_ok", lang).format(n=_n))
            except Exception as exc:  # noqa: BLE001
                st.error(f"⚠️ {exc}")

        st.caption(t("ws_where", lang).format(path=ws.client_root(ws_cid)))

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

    st.subheader(t("h_pvfaq", lang))
    st.markdown(t("h_pvfaq_note", lang))
    for item in purview_collibra_faq(lang):
        with st.expander(f"❓ {item['q']}"):
            st.markdown(item["a"])

# ---------------------------------------------------------- Entregable final
with tab_del:
    st.info(t("del_intro", lang), icon="📦")
    _del_keys = case_deliverable.case_keys()
    _del_key = st.selectbox(
        t("del_pick", lang), _del_keys,
        format_func=lambda k: ext_samples.sample_meta(k, lang)["name"])
    _del = case_deliverable.build_deliverable(_del_key, lang)
    _dm, _dk, _dmig = _del["meta"], _del["kpis"], _del["migration"]

    st.subheader(f"📦 {_dm['name']}")
    st.caption(f"{_dm['domain']} · {_dm['classification']} · "
               f"{t('del_owner', lang)}: {_dm['owner']} · "
               f"{t('col_steward', lang)}: {_dm['steward']}")
    st.caption(f"{t('del_source', lang)}: {_dm['source']}")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(t("del_kpi_rows", lang), f"{_dk['rows']:,} × {_dk['columns']}")
    k2.metric(t("kpi_quality", lang), f"{_dk['quality_index']} / 100")
    k3.metric(t("del_kpi_rules", lang), f"{_dk['rules_pass']} / {_dk['rules_total']}")
    k4.metric(t("del_kpi_curation", lang),
              f"{_dk['curation_pct']}% ({_dk['curation_reviewed']}/{_dk['curation_total']})")
    k5, k6, k7 = st.columns(3)
    k5.metric(t("del_kpi_documented", lang), f"{_dk['documented_pct']}%")
    k6.metric(t("del_kpi_pii", lang), _dk["pii_columns"])
    k7.metric(t("del_kpi_fails", lang), len(_del["findings"]))

    if len(_del["findings"]):
        with st.expander(t("del_findings", lang), expanded=True):
            st.caption(t("del_findings_note", lang))
            st.dataframe(_del["findings"], width="stretch", hide_index=True)

    with st.expander(t("tbl_dictionary", lang)):
        st.dataframe(_del["dictionary"], width="stretch", hide_index=True)
    with st.expander(t("tbl_quality", lang)):
        st.dataframe(_del["quality_results"], width="stretch", hide_index=True)
    with st.expander(t("tbl_glossary", lang)):
        st.dataframe(_del["glossary"], width="stretch", hide_index=True)
    with st.expander(t("tbl_lineage", lang)):
        st.dataframe(_del["lineage"], width="stretch", hide_index=True)

    st.subheader(t("del_mig_title", lang))
    st.caption(t("del_mig_note", lang))
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Purview · entidades", _dmig["purview_entities"])
    g2.metric("Purview · términos",
              f"{_dmig['purview_terms']} ({_dmig['purview_terms_approved']} Approved)")
    g3.metric("Collibra · assets", _dmig["collibra_assets"])
    g4.metric("Collibra · términos", _dmig["collibra_terms"])

    st.subheader(t("del_download", lang))
    dd1, dd2 = st.columns(2)
    dd1.download_button(
        t("del_download_xlsx", lang),
        case_deliverable.deliverable_xlsx_bytes(_del_key, lang),
        f"entregable_{_del_key}_{lang}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch")
    dd2.download_button(
        t("del_download_md", lang),
        case_deliverable.executive_summary_md(_del_key, lang).encode("utf-8"),
        f"entregable_{_del_key}_{lang}.md", "text/markdown",
        width="stretch")
    st.caption(t("del_honest_note", lang))

# --------------------------------------------------------------- Power BI
with tab_con:
    st.info(t("con_intro", lang), icon="🤝")

    with st.expander(t("con_theory", lang)):
        st.caption(t("con_theory_note", lang))
        for _th in data_contracts.theory(lang):
            st.markdown(f"**{_th['concept']}** — {_th['plain']}")
            st.caption(f"🛠️ {_th['practice']}")

    # Siempre sobre el alcance combinado completo (demo + casos): un contrato
    # por cada producto gobernado, evaluado con la última corrida real.
    _con_res = _results_combined(lang)
    _kp = data_contracts.kpis(lang, _con_res)
    _c1, _c2, _c3, _c4, _c5, _c6 = st.columns(6)
    _c1.metric(t("con_kpi_products", lang), _kp["products"])
    _c2.metric(t("con_kpi_ok", lang), _kp["ok"])
    _c3.metric(t("con_kpi_risk", lang), _kp["at_risk"])
    _c4.metric(t("con_kpi_breach", lang), _kp["breached"])
    _c5.metric(t("con_kpi_alerts", lang), _kp["alerts"])
    _c6.metric(t("con_kpi_signed", lang), _kp["signed"])

    st.subheader(t("con_table_title", lang))
    st.caption(t("con_table_note", lang))
    _con_df = data_contracts.contracts_df(lang, _con_res)
    _con_show = _con_df.copy()
    _con_show["compliance"] = _con_show["compliance"].map(
        lambda v: t(f"con_st_{v}", lang))
    _con_show["agreement"] = _con_show["agreement"].map(
        lambda v: t(f"con_agr_{v}", lang))
    st.dataframe(_con_show[["dataset", "domain", "domain_owner",
                            "product_owner", "producer", "sla_refresh",
                            "rules", "compliance_pct", "compliance",
                            "agreement", "signed_by"]],
                 width="stretch", hide_index=True)

    _con_key = st.selectbox(t("con_pick", lang),
                            _con_df["dataset"].tolist(), key="con_pick")
    _con_row = _con_df[_con_df["dataset"] == _con_key].iloc[0]
    st.caption(f'{t("con_role_do", lang)}: {_con_row["domain_owner"]} · '
               f'{t("con_role_po", lang)}: {_con_row["product_owner"]} · '
               f'{t("con_sla", lang)}: {_con_row["sla_refresh"]}')
    st.caption(f'{t("con_role_prod", lang)}: {_con_row["producer"]}')
    st.caption(f'{t("con_role_cons", lang)}: {_con_row["consumers"]}')

    st.markdown(f'**{t("con_rules_title", lang)}**')
    _con_rules = _con_res[_con_res["dataset"] == _con_key]
    st.dataframe(_con_rules[["rule_id", "column", "dimension", "description",
                             "score", "threshold", "status"]],
                 width="stretch", hide_index=True)
    st.markdown(f'**{t("con_esc_title", lang)}**')
    st.markdown(f'- {t("con_esc_warn", lang)}')
    st.markdown(f'- {t("con_esc_fail", lang)}')

    st.markdown(f'**{t("con_sign_title", lang)}**')
    st.caption(t("con_sign_note", lang))
    _agr = data_contracts.agreement_for(_con_key)
    if _agr:
        st.success(t("con_signed_info", lang).format(
            name=_agr["signed_by"], role=_agr["role"], date=_agr["date"]))
    _cs1, _cs2 = st.columns(2)
    _con_name = _cs1.text_input(t("con_sign_name", lang), key="con_sign_name")
    _con_role = _cs2.text_input(t("con_sign_role", lang), key="con_sign_role")
    if st.button(t("con_sign_btn", lang), key="con_sign_btn"):
        if not _con_name.strip():
            st.error(t("con_need_name", lang))
        else:
            data_contracts.save_agreement(_con_key, _con_name, _con_role)
            st.rerun()

    st.subheader(t("con_alerts_title", lang))
    st.caption(t("con_alerts_note", lang))
    _con_ale = data_contracts.alerts_df(lang, _con_res)
    if len(_con_ale):
        st.dataframe(_con_ale, width="stretch", hide_index=True)
    else:
        st.success(t("con_alerts_none", lang))

    st.download_button(t("con_dl_xlsx", lang),
                       data_contracts.contracts_xlsx_bytes(lang, _con_res),
                       file_name="contratos_datos.xlsx",
                       mime=("application/vnd.openxmlformats-officedocument"
                             ".spreadsheetml.sheet"),
                       key="con_dl_xlsx")

with tab_pbi:
    st.info(t("pbi_intro", lang), icon="🔷")
    st.caption("🔐 " + t("pbi_secure_note", lang))

    _PBI_MODE = {"offline": t("pbi_mode_offline", lang), "tenant": t("pbi_mode_tenant", lang),
                "example": t("pbi_mode_example", lang)}
    pbi_mode = st.radio(t("pbi_mode", lang), ["offline", "tenant", "example"], horizontal=True,
                        key="pbi_mode", format_func=lambda k: _PBI_MODE[k])

    model_out = None
    pbi_err = None
    pbi_single_model = None   # PowerBIModel único (modo offline)
    pbi_models = None         # list[PowerBIModel] (modo tenant)

    if pbi_mode == "offline":
        _PBI_SRC = {"path": t("pbi_src_path", lang), "zip": t("pbi_src_zip", lang)}
        pbi_source = st.radio(t("pbi_source", lang), ["path", "zip"], horizontal=True,
                              key="pbi_source", format_func=lambda k: _PBI_SRC[k])
        if pbi_source == "path":
            folder = st.text_input(t("pbi_path", lang), key="pbi_path")
            st.caption(t("pbi_path_hint", lang))
            if st.button(t("pbi_load", lang), key="pbi_load_path") and folder.strip():
                try:
                    with st.spinner(t("pbi_wait", lang)):
                        model_out = pbi.ingest_pbip(folder.strip(), lang)
                except Exception as exc:  # noqa: BLE001
                    pbi_err = str(exc)
        else:
            up = st.file_uploader(t("pbi_zip", lang), type=["zip"], key="pbi_zip")
            if up is not None:
                import tempfile
                import zipfile
                try:
                    with st.spinner(t("pbi_wait", lang)):
                        tmpdir = tempfile.mkdtemp(prefix="mvdg_pbip_")
                        zpath = os.path.join(tmpdir, "proj.zip")
                        with open(zpath, "wb") as fh:
                            fh.write(up.getbuffer())
                        with zipfile.ZipFile(zpath) as zf:
                            zf.extractall(tmpdir)
                        model_out = pbi.ingest_pbip(tmpdir, lang)
                except Exception as exc:  # noqa: BLE001
                    pbi_err = str(exc)
        if model_out is not None:
            pbi_single_model = model_out["_model"]
    elif pbi_mode == "example":
        _PBI_EX_KIND = {"single": t("pbi_example_single", lang), "tenant": t("pbi_example_tenant", lang)}
        pbi_ex_kind = st.radio(t("pbi_example_kind", lang), ["single", "tenant"], horizontal=True,
                               key="pbi_example_kind", format_func=lambda k: _PBI_EX_KIND[k])
        if pbi_ex_kind == "single":
            st.caption(t("pbi_example_single_note", lang))
            model_out = pbi.ingest_example(lang)
            pbi_single_model = model_out["_model"]
        else:
            st.warning(t("pbi_example_tenant_note", lang), icon="⚠️")
            model_out = pbi.ingest_example_tenant(lang)
            pbi_models = model_out["_models"]
    else:
        if not pbi.tenant_configured():
            st.warning(t("pbi_tenant_off", lang), icon="🔒")
        else:
            st.caption(t("pbi_tenant_hint", lang))
            pbi_max_ws = st.number_input(t("pbi_tenant_max_ws", lang), min_value=1, max_value=1000,
                                         value=25, step=5, key="pbi_tenant_max_ws")
            if st.button(t("pbi_tenant_scan", lang), key="pbi_tenant_scan_btn"):
                try:
                    with st.spinner(t("pbi_wait", lang)):
                        model_out = pbi.ingest_tenant(lang, max_workspaces=int(pbi_max_ws))
                except Exception as exc:  # noqa: BLE001
                    pbi_err = str(exc)
            cached = st.session_state.get("pbi_tenant_result")
            if model_out is not None:
                st.session_state["pbi_tenant_result"] = model_out
            elif cached is not None and not pbi_err:
                model_out = cached
        if model_out is not None:
            pbi_models = model_out["_models"]

    if pbi_err:
        st.error(f"{t('pbi_err', lang)}: {pbi_err}", icon="⚠️")
    elif model_out is None:
        st.caption(t("pbi_no_model", lang))
    else:
        k1, k2, k3, k4, k5 = st.columns(5)
        if pbi_single_model is not None:
            k1.metric(t("pbi_model", lang), pbi_single_model.name)
            k2.metric(t("pbi_tables", lang), len(pbi_single_model.tables))
            k3.metric(t("pbi_measures", lang), len(pbi_single_model.measures))
            k4.metric(t("pbi_columns", lang), len(pbi_single_model.columns))
            k5.metric(t("pbi_roles", lang), len(pbi_single_model.roles))
        else:
            k1.metric(t("pbi_datasets", lang), len(pbi_models))
            k2.metric(t("pbi_tables", lang), sum(len(m.tables) for m in pbi_models))
            k3.metric(t("pbi_measures", lang), sum(len(m.measures) for m in pbi_models))
            k4.metric(t("pbi_columns", lang), sum(len(m.columns) for m in pbi_models))
            k5.metric(t("pbi_roles", lang), sum(len(m.roles) for m in pbi_models))

        st.subheader(t("pbi_catalog_title", lang))
        st.dataframe(model_out["catalog"], width="stretch", hide_index=True)

        st.subheader(t("pbi_health_title", lang))
        q = model_out["quality"]
        st.metric(t("pbi_health_overall", lang), f"{round(q['score'].mean(), 1)} / 100")
        q_show = q.copy()
        q_show["dimension"] = q_show["dimension"].map(lambda d: _DIM_LABEL.get(d, d))
        q_show["status"] = q_show["status"].map(lambda s: _STATUS_LABEL.get(s, s))
        st.dataframe(q_show, width="stretch", hide_index=True)

        st.subheader(t("pbi_sources_title", lang))
        st.caption(t("pbi_sources_hint", lang))
        srcs_show = model_out["sources"].copy()
        srcs_show["source"] = srcs_show["source"].replace("", t("pbi_source_none", lang))
        srcs_show.columns = [t("pbi_source_col_table", lang), t("pbi_source_col_src", lang)]
        st.dataframe(srcs_show, width="stretch", hide_index=True)

        st.subheader(t("pbi_lineage_title", lang))
        st.caption(t("pbi_lineage_hint", lang))
        nodes, edges = graph_from_lineage(model_out["lineage"])
        _pbi_layer_titles = {
            "source": t("lin_layer_source", lang), "raw": t("lin_layer_raw", lang),
            "curated": t("lin_layer_curated", lang), "mart": t("lin_layer_mart", lang),
            "bi": t("lin_layer_bi", lang),
        }
        st.plotly_chart(
            lineage_figure(nodes=nodes, edges=edges, layer_titles=_pbi_layer_titles),
            width="stretch")

        st.subheader(t("pbi_measures_title", lang))
        _pbi_provider = configured_provider()
        if _pbi_provider:
            st.caption(t("pbi_refactor_hint", lang))
        if pbi_single_model is not None:
            _pbi_measures_show = [(pbi_single_model.name, m) for m in pbi_single_model.measures]
        else:
            _pbi_ds_names = [m.name for m in pbi_models]
            _pbi_picked = st.selectbox(t("pbi_tenant_pick_dataset", lang), _pbi_ds_names,
                                       key="pbi_tenant_pick")
            _pbi_picked_model = next(m for m in pbi_models if m.name == _pbi_picked)
            _pbi_measures_show = [(_pbi_picked_model.name, m) for m in _pbi_picked_model.measures]
        for _i, (_mname, _m) in enumerate(_pbi_measures_show):
            with st.expander(f"📐 {_m.name}" + (f" · {_m.table}" if _m.table else "")):
                st.code(_m.dax or "—", language="text")
                if _m.description:
                    st.caption(_m.description)
                if _pbi_provider and st.button(
                        t("pbi_refactor", lang).format(provider=provider_label(_pbi_provider)),
                        key=f"pbi_dax_{_mname}_{_i}"):
                    with st.spinner(t("pbi_wait", lang)):
                        _res = ai_refactor_dax(_m.name, _m.dax, _m.table, lang, _pbi_provider)
                    if _res:
                        st.markdown(f"**{t('pbi_r_assessment', lang)}:** {_res['assessment']}")
                        st.markdown(f"**{t('pbi_r_issues', lang)}:** {_res['issues']}")
                        st.markdown(f"**{t('pbi_r_dax', lang)}:**")
                        st.code(_res["refactored_dax"], language="text")
                        st.caption(f"{t('pbi_r_expl', lang)}: {_res['explanation']}")
                    else:
                        st.info(t("fix_note", lang))

# ---------------------------------------------------------------- Tableau
    # ------------------------------------------------------------- MCP
    st.divider()
    st.subheader(t("mcp_title", lang))
    st.caption(t("mcp_intro", lang))

    with st.expander(t("mcp_local_title", lang)):
        st.markdown(t("mcp_local_body", lang))
    with st.expander(t("mcp_remote_title", lang)):
        st.markdown(t("mcp_remote_body", lang))
        st.caption(t("mcp_docs_note", lang))

    st.markdown(f'**{t("mcp_expose_title", lang)}**')
    st.markdown(t("mcp_expose_body", lang))
    import importlib.util as _ilu
    _mcp_ok = _ilu.find_spec("mcp") is not None
    if _mcp_ok:
        st.success(t("mcp_expose_status_ok", lang), icon="🔌")
    else:
        st.warning(t("mcp_expose_status_missing", lang), icon="⚠️")
    st.caption(t("mcp_cfg_claude", lang))
    st.code("claude mcp add mvdg -- python -m mvdg.mcp_server", language="bash")
    st.caption(t("mcp_cfg_vscode", lang))
    st.code('{\n  "servers": {\n    "mvdg": {"type": "stdio", "command": "python",\n             "args": ["-m", "mvdg.mcp_server"]}\n  }\n}', language="json")
    st.caption(t("mcp_cfg_pbi_local", lang))
    st.code('{\n  "powerbi-modeling-mcp": {\n    "type": "stdio", "command": "npx",\n    "args": ["-y", "@microsoft/powerbi-modeling-mcp@latest", "--start"]\n  }\n}', language="json")

    st.caption(t("mcp_try_note", lang))
    if st.button(t("mcp_try_btn", lang), key="mcp_try_btn", disabled=not _mcp_ok):
        from mvdg import mcp_client as _mcp_cli
        _mcp_tools = _mcp_cli.list_tools(
            sys.executable, ["-m", "mvdg.mcp_server"],
            env={**os.environ, "PYTHONPATH": os.path.dirname(os.path.dirname(os.path.abspath(__file__)))})
        st.success(t("mcp_try_ok", lang).format(n=len(_mcp_tools)))
        st.json({tl["name"]: tl["description"].split("\n")[0] for tl in _mcp_tools})

    st.info(t("mcp_honest_note", lang), icon="🧭")

with tab_tab:
    st.info(t("tab_intro", lang), icon="📊")

    _TAB_MODE = {"offline": t("tab_mode_offline", lang), "site": t("tab_mode_site", lang),
                "example": t("tab_mode_example", lang)}
    tab_mode = st.radio(t("tab_mode", lang), ["offline", "site", "example"], horizontal=True,
                        key="tab_mode", format_func=lambda k: _TAB_MODE[k])

    if tab_mode == "offline":
        tpath = st.text_input(t("tab_path", lang), key="tab_path")
        st.caption(t("tab_path_hint", lang))
        up = st.file_uploader(t("tab_upload", lang), type=["twb", "twbx"], key="tab_upload")
        if st.button(t("tab_load", lang), key="tab_load_btn"):
            try:
                with st.spinner(t("tab_wait", lang)):
                    if up is not None:
                        import tempfile
                        tmpdir = tempfile.mkdtemp(prefix="mvdg_twb_")
                        fpath = os.path.join(tmpdir, up.name)
                        with open(fpath, "wb") as fh:
                            fh.write(up.getbuffer())
                        tab_out = tabl.ingest_twb(fpath, lang)
                    elif tpath.strip():
                        tab_out = tabl.ingest_twb(tpath.strip(), lang)
                    else:
                        tab_out = None
                if tab_out is not None:
                    st.session_state["tab_scan_result"] = tab_out
            except Exception as exc:  # noqa: BLE001
                st.session_state["tab_scan_result"] = None
                st.error(f"{t('tab_err', lang)}: {exc}", icon="⚠️")
    elif tab_mode == "example":
        st.caption(t("tab_example_note", lang))
        st.session_state["tab_scan_result"] = tabl.ingest_example(lang)
    else:
        if not tabl.configured():
            st.warning(t("tab_off", lang), icon="🔒")
        else:
            if st.button(t("tab_scan", lang), key="tab_scan_btn"):
                try:
                    with st.spinner(t("tab_wait", lang)):
                        tab_out = tabl.ingest_site(lang)
                    st.session_state["tab_scan_result"] = tab_out
                except Exception as exc:  # noqa: BLE001
                    st.session_state["tab_scan_result"] = None
                    st.error(f"{t('tab_err', lang)}: {exc}", icon="⚠️")

    tab_out = st.session_state.get("tab_scan_result")
    if tab_out is None:
        st.caption(t("tab_no_model", lang))
    else:
        tab_model = tab_out["_model"]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric(t("tab_workbooks", lang), len(tab_model.workbooks))
        k2.metric(t("tab_datasources", lang), len(tab_model.datasources))
        k3.metric(t("tab_fields", lang), len(tab_model.fields))
        k4.metric(t("tab_calc_fields", lang), sum(1 for f in tab_model.fields if f.is_calculated))

        st.subheader(t("tab_catalog_title", lang))
        st.dataframe(tab_out["catalog"], width="stretch", hide_index=True)

        st.subheader(t("tab_health_title", lang))
        tq = tab_out["quality"]
        st.metric(t("tab_health_overall", lang), f"{round(tq['score'].mean(), 1)} / 100")
        tq_show = tq.copy()
        tq_show["dimension"] = tq_show["dimension"].map(lambda d: _DIM_LABEL.get(d, d))
        tq_show["status"] = tq_show["status"].map(lambda s: _STATUS_LABEL.get(s, s))
        st.dataframe(tq_show, width="stretch", hide_index=True)

        st.subheader(t("tab_sources_title", lang))
        st.caption(t("tab_sources_hint", lang))
        tsrcs_show = tab_out["sources"].copy()
        tsrcs_show["source"] = tsrcs_show["source"].replace("", t("pbi_source_none", lang))
        tsrcs_show.columns = [t("tab_datasources", lang), t("pbi_source_col_src", lang)]
        st.dataframe(tsrcs_show, width="stretch", hide_index=True)

        st.subheader(t("tab_lineage_title", lang))
        st.caption(t("tab_lineage_hint", lang))
        tnodes, tedges = graph_from_lineage(tab_out["lineage"])
        _tab_layer_titles = {
            "source": t("lin_layer_source", lang), "raw": t("lin_layer_raw", lang),
            "curated": t("lin_layer_curated", lang), "mart": t("lin_layer_mart", lang),
            "bi": t("lin_layer_bi", lang),
        }
        st.plotly_chart(
            lineage_figure(nodes=tnodes, edges=tedges, layer_titles=_tab_layer_titles),
            width="stretch")

        st.subheader(t("tab_calc_title", lang))
        _tab_provider = configured_provider()
        if _tab_provider:
            st.caption(t("tab_refactor_hint", lang))
        _tab_calc_fields = [f for f in tab_model.fields if f.is_calculated]
        for _i, _f in enumerate(_tab_calc_fields):
            with st.expander(f"📐 {_f.name}" + (f" · {_f.datasource}" if _f.datasource else "")):
                st.code(_f.formula or "—", language="text")
                if _f.description:
                    st.caption(_f.description)
                if _tab_provider and st.button(
                        t("tab_refactor", lang).format(provider=provider_label(_tab_provider)),
                        key=f"tab_calc_{_i}"):
                    with st.spinner(t("tab_wait", lang)):
                        _tres = ai_refactor_calc(_f.name, _f.formula, _f.datasource, lang, _tab_provider)
                    if _tres:
                        st.markdown(f"**{t('pbi_r_assessment', lang)}:** {_tres['assessment']}")
                        st.markdown(f"**{t('pbi_r_issues', lang)}:** {_tres['issues']}")
                        st.markdown(f"**{t('tab_r_formula', lang)}:**")
                        st.code(_tres["refactored_formula"], language="text")
                        st.caption(f"{t('pbi_r_expl', lang)}: {_tres['explanation']}")
                    else:
                        st.info(t("fix_note", lang))

    # ------------------------------------------------------------- MCP Tableau
    st.divider()
    st.subheader(t("mcp_tab_title", lang))
    st.markdown(t("mcp_tab_body", lang))
    st.caption(t("mcp_tab_cfg", lang))
    st.code('{\n  "mcpServers": {\n    "tableau": {\n      "command": "npx",\n      "args": ["-y", "@tableau/mcp-server@3.0.0"],\n      "env": {\n        "SERVER": "https://mi-servidor-tableau",\n        "SITE_NAME": "mi_sitio",\n        "PAT_NAME": "mi_pat",\n        "PAT_VALUE": "<valor-del-PAT>",\n        "PRODUCT_TELEMETRY_ENABLED": "false"\n      }\n    }\n  }\n}', language="json")
    st.warning(t("mcp_tab_caveats", lang), icon="⚠️")
    st.info(t("mcp_tab_verified", lang), icon="🧪")
    st.caption(t("mcp_tab_gov", lang))
