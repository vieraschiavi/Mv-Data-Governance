"""
MV Data Governance · Dashboard de escritorio (Streamlit).

Trilingüe (ES/EN/PT), estilo MV Kobra: navy + ámbar. Se ejecuta con el .bat,
con `streamlit run app/app.py` o empaquetado como .exe (PyInstaller).
"""
from __future__ import annotations

import os
import sys

# Permite ejecutar tanto desde la raíz del repo como desde el bundle PyInstaller.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
from mvdg.help_center import automation_rows, speeches
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

(tab_ov, tab_cat, tab_q, tab_lin, tab_g, tab_p, tab_pr, tab_bi,
 tab_cl, tab_h) = st.tabs([
    t("tab_overview", lang), t("tab_catalog", lang), t("tab_quality", lang),
    t("tab_lineage", lang), t("tab_glossary", lang), t("tab_policies", lang),
    t("tab_profiler", lang), t("tab_bi", lang),
    t("tab_clients", lang), t("tab_help", lang),
])

_DIM_LABEL = {d: t(f"dim_{d}", lang) for d in
              ["completeness", "uniqueness", "validity", "consistency",
               "timeliness", "accuracy"]}
_STATUS_LABEL = {"pass": t("q_pass", lang), "warn": t("q_warn", lang),
                 "fail": t("q_fail", lang)}

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
with tab_pr:
    st.info(t("pr_intro", lang), icon="🔎")
    up = st.file_uploader(t("pr_upload", lang), type=["csv", "xlsx", "xls"])
    if up is not None:
        try:
            user_df = (pd.read_csv(up) if up.name.lower().endswith(".csv")
                       else pd.read_excel(up))
        except Exception as exc:  # archivo corrupto / formato raro
            st.error(f"⚠️ {exc}")
            user_df = None
        if user_df is not None and len(user_df):
            info = summary(user_df)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(t("col_rows", lang), f"{info['rows']:,}")
            c2.metric(t("col_column", lang), info["columns"])
            c3.metric(t("pr_dupes", lang), info["duplicate_rows"])
            c4.metric(t("pr_nulls", lang), f"{info['null_cells_pct']}%")
            st.subheader(t("pr_col_profile", lang))
            prof = profile_table(user_df)
            st.dataframe(prof.rename(columns={
                "column": t("col_column", lang), "dtype": t("col_type", lang),
                "null_pct": t("pr_nulls", lang),
                "unique_values": t("pr_unique", lang),
                "possible_pii": t("col_pii", lang),
            }), width="stretch", hide_index=True)
            if info["pii_columns"]:
                st.warning(t("pr_pii_hint", lang), icon="🔐")
            st.subheader(t("pr_suggestions", lang))
            for s in suggest_rules(user_df, lang):
                st.markdown(f"- {s}")

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
