# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
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
from mvdg import dataeng
from mvdg.catalog import catalog_df, dictionary_df, dataset_names, pii_columns
from mvdg.clients import (BI_TOOLS, IT_RESTRICTIONS, STATUSES, clients_df,
                          data_dir, delete_client, load_clients,
                          recommended_pack, save_client)
from mvdg.connectors import (CLOUD_ENGINES, ENGINES, EXTRA_EXAMPLE,
                             delete_connection, list_tables,
                             load_connections, load_table, run_query,
                             save_connection, scan_all_connections,
                             stored_password, test_connection)
from mvdg.errors import friendly_error
from mvdg.help_center import automation_rows, purview_collibra_faq, speeches
from mvdg import licensing
from mvdg.lab_case import lab_measure, lab_steps
from mvdg import azure_discovery
from mvdg import cobit_iso
from mvdg import collibra_export
from mvdg import collibra_pull
from mvdg import curation
from mvdg import enforcement
from mvdg import insights
from mvdg import install_mode
from mvdg import interview
from mvdg import meetings
from mvdg import mip_labels
from mvdg import orgchart
from mvdg import dmbok
from mvdg import doc_export
from mvdg import mdm
from mvdg import pipeline_doc
from mvdg import transcribe
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
from mvdg import ai_settings, mcp_presets
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
from mvdg.auto_rules import auto_quality_results
from mvdg.profiler import profile_table, suggest_rules, summary
from mvdg.quality import (open_issues, overall_index, quality_by_dimension,
                          quality_by_dataset, quality_matrix, quality_trend,
                          run_rules)

# ----------------------------------------------------------------- página
st.set_page_config(page_title=APP_NAME, page_icon="", layout="wide")

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
/* --- Que parezca un PROGRAMA, no una app de Streamlit -----------------
   El cliente compra software de gobierno de datos, no una demo. Tres cosas
   delataban el framework: la barra blanca del header (que encima rompía el
   tema oscuro), el menú ⋮ con opciones de desarrollo ("Rerun", "Record a
   screencast", "Report a bug" al repo de Streamlit) y el pie "Made with
   Streamlit". El botón Deploy lo saca --client.toolbarMode; el resto no se
   puede apagar por configuración, así que va por CSS.
   El header se hace TRANSPARENTE en vez de display:none a propósito: ahí
   vive el botón que despliega la barra lateral cuando está colapsada, y
   ocultarlo dejaría al usuario sin forma de recuperarla. */
header[data-testid="stHeader"] {{ background: transparent !important; }}
[data-testid="stToolbar"], [data-testid="stMainMenu"], #MainMenu,
[data-testid="stStatusWidget"], [data-testid="stDecoration"],
footer {{ display: none !important; visibility: hidden !important; }}
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


# ------------------------------------------ los datasets que carga el usuario
# Antes, lo que el usuario subía en "Mis datos" se guardaba en
# ``current_dataset`` y lo leía UNA sola pestaña (Proyecto, para guardarlo).
# El resto del programa seguía mostrando la demo, así que quien probaba el
# producto con su propio Excel veía su archivo perfilado en una pestaña y
# datos ajenos en las otras diecinueve. Esto lo convierte en un registro que
# se acumula y que alimenta a todas.
def _mis_datasets() -> dict:
    return st.session_state.setdefault("mvdg_user_datasets", {})


def _registrar_dataset(nombre: str, df) -> None:
    """Deja el dataset disponible para TODO el programa, no solo para la
    pestaña donde se cargó.

    El ``st.rerun()`` no es un detalle: Streamlit ejecuta el script de arriba
    abajo, y el sidebar y las demás pestañas se dibujan ANTES de que llegue
    el turno de "Mis datos". Sin volver a correr, el dataset queda guardado
    pero nadie lo ve hasta la próxima interacción del usuario — que es
    exactamente el síntoma que se reportó: el archivo cargaba y el resto del
    programa seguía mostrando la demo.

    El registro de vistos evita el bucle: cada archivo dispara UN rerun. Se
    indexa por (nombre, filas, columnas) y no por identidad del DataFrame,
    porque ``pd.read_csv`` devuelve un objeto nuevo en cada pasada — comparar
    objetos haría que el rerun se dispare siempre.
    """
    if df is None or not len(df) or not nombre:
        return
    _mis_datasets()[nombre] = df
    # Se mantiene ``current_dataset`` porque la pestaña Proyecto lo usa para
    # guardar "el último": son dos cosas distintas y las dos hacen falta.
    st.session_state["current_dataset"] = df
    st.session_state["current_dataset_name"] = nombre

    vistos = st.session_state.setdefault("_mvdg_user_vistos", set())
    clave = (nombre, len(df), len(df.columns))
    if clave not in vistos:
        vistos.add(clave)
        st.rerun()


def _firma_datasets(lang: str) -> tuple:
    """Identidad barata de lo cargado, para no recalcular en cada rerun.

    Streamlit vuelve a ejecutar el script entero ante cualquier interacción
    (cambiar de pestaña incluido). Correr las reglas de calidad de un archivo
    grande en cada una de esas pasadas se nota; el nombre y la forma alcanzan
    para saber si cambió algo.
    """
    return (lang,) + tuple(sorted((n, len(d), len(d.columns))
                                  for n, d in _mis_datasets().items()))


def _tablas_usuario(lang: str) -> dict:
    """Catálogo, diccionario, calidad y linaje de lo que cargó el usuario."""
    firma = _firma_datasets(lang)
    if st.session_state.get("_mvdg_user_firma") == firma:
        return st.session_state["_mvdg_user_tablas"]
    ud = _mis_datasets()
    tablas = {
        "catalog": gov_scope.user_catalog(ud, lang),
        "dictionary": gov_scope.user_dictionary(ud, lang),
        "results": gov_scope.user_results(ud, lang),
    }
    st.session_state["_mvdg_user_firma"] = firma
    st.session_state["_mvdg_user_tablas"] = tablas
    return tablas


def _con_usuario(base, clave: str, lang: str):
    """Le suma al DataFrame base las filas de los datasets del usuario."""
    extra = _tablas_usuario(lang)[clave]
    if extra.empty:
        return base
    if clave == "catalog":
        extra = gov_scope.user_catalog(_mis_datasets(), lang, columnas=base.columns)
    return pd.concat([base, extra], ignore_index=True)


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown(f"## {APP_NAME}")
    lang = st.radio(
        f"{t('language', 'es')} / Language / Idioma",
        LANGS, format_func=lambda code: LANG_NAMES[code], horizontal=True,
        key="lang",
    )
    st.caption(t("sidebar_help", lang))
    st.divider()
    incl_samples = st.toggle(t("scope_toggle", lang), value=True, key="scope_samples")
    st.caption(t("scope_hint", lang))
    # Qué datasets propios están alimentando al programa ahora mismo. Sin
    # esto no hay forma de saber, mirando una pestaña cualquiera, si lo que
    # se está viendo incluye lo que uno cargó o sigue siendo la demo.
    if _mis_datasets():
        st.divider()
        st.success(t("scope_user_badge", lang).format(
            n=len(_mis_datasets()), nombres=", ".join(_mis_datasets())))
        if st.button(t("scope_user_clear", lang), key="scope_user_clear_btn"):
            st.session_state["mvdg_user_datasets"] = {}
            # También el registro de "ya lo vi": si no, volver a subir el
            # mismo archivo no refrescaría las otras pestañas.
            for _k in ("_mvdg_user_firma", "_mvdg_user_vistos",
                       "current_dataset", "current_dataset_name"):
                st.session_state.pop(_k, None)
            st.rerun()
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
    st.markdown("<span class='mv-badge'>MV · Data Governance Suite</span>", unsafe_allow_html=True)
    st.title(f"{t('auth_title', lang)}")
    st.caption(t("auth_intro", lang))
    _auth_pwd = st.text_input(t("auth_prompt", lang), type="password", key="auth_pwd_input")
    if st.button(t("auth_button", lang), type="primary"):
        if mvdg_server.check_password(_auth_pwd):
            st.session_state["_mvdg_authed"] = True
            st.rerun()
        else:
            st.error(t("auth_wrong", lang))
    st.stop()

st.markdown("<span class='mv-badge'>MV · Data Governance Suite</span>", unsafe_allow_html=True)
st.title(APP_NAME)
st.caption(t("app_tagline", lang))


@st.cache_data(show_spinner=False)
def _results_combined(lang: str):
    return gov_scope.combined_results(lang, _results(lang))


# Los datasets del usuario NO dependen del toggle "incluir casos de ejemplo":
# ese toggle decide si se muestran los 4 casos que trae el programa. Lo que
# cargó el usuario es suyo y va siempre.
results = _con_usuario(_results_combined(lang) if incl_samples else _results(lang),
                       "results", lang)
tables = dict(_tables())
tables.update(_mis_datasets())

(tab_ov, tab_lab, tab_dk, tab_cat, tab_mdm, tab_q, tab_lin, tab_con, tab_g, tab_cu, tab_resp,
 tab_p, tab_pr, tab_bi, tab_tz, tab_del, tab_pbi, tab_tab, tab_cl, tab_srv, tab_mtg,
 tab_ws, tab_h) = st.tabs([
    t("tab_overview", lang), t("tab_lab", lang), t("tab_dmbok", lang),
    t("tab_catalog", lang), t("tab_mdm", lang), t("tab_quality", lang),
    t("tab_lineage", lang), t("tab_contracts", lang), t("tab_glossary", lang), t("tab_curation", lang),
    t("tab_responsibles", lang), t("tab_policies", lang), t("tab_profiler", lang),
    t("tab_bi", lang), t("tab_trace", lang), t("tab_deliverable", lang),
    t("tab_pbi", lang), t("tab_tableau", lang),
    t("tab_clients", lang), t("tab_survey", lang), t("tab_meetings", lang),
    t("tab_workspace", lang), t("tab_help", lang),
])

_DIM_LABEL = {d: t(f"dim_{d}", lang) for d in
              ["completeness", "uniqueness", "validity", "consistency",
               "timeliness", "accuracy"]}
_STATUS_LABEL = {"pass": t("q_pass", lang), "warn": t("q_warn", lang),
                 "fail": t("q_fail", lang)}


def _error(exc: Exception, lang: str, contexto: str = "generico",
           prefijo: str = "") -> None:
    """Muestra un error que se entiende y dice qué hacer.

    Antes esto era ``st.error(f"{exc}")`` repartido por toda la pantalla:
    al usuario le llegaba el texto crudo de pandas o de sqlalchemy ("Error
    tokenizing data. C error: Expected 1 fields in line 3, saw 2"), sin
    traducir y sin decirle qué corregir. El detalle técnico sigue disponible,
    plegado, para poder reportarlo."""
    mensaje, detalle = friendly_error(exc, lang, contexto)
    st.error(f"{prefijo}{mensaje}" if prefijo else mensaje)
    with st.expander(t("err_detalle", lang)):
        st.code(detalle, language=None)


def _licencia_ok(funcion: str, lang: str) -> bool:
    """¿Está habilitada esta función para el plan vigente?

    Si no, muestra el aviso y devuelve False para que el llamador NO dibuje el
    botón de la acción real. La política de qué es pago vive en un solo lugar
    (mvdg/licensing.py, FUNCIONES_PAGAS) — acá solo se consulta."""
    if licensing.has_feature(funcion):
        return True
    st.info(t("lic_locked", lang).format(tab=t("tab_help", lang)))
    return False


def _render_fixes(results_df, lang, ns=""):
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
        st.success(t("fix_none", lang))
        return
    # Las keys de los widgets tienen que ser únicas en TODA la corrida, no solo
    # dentro de este bloque: Streamlit ejecuta el script entero en cada rerun y
    # las pestañas NO son perezosas, así que las tres llamadas a _render_fixes
    # conviven en la misma pasada. Con "Mis datos" activado, el mismo dataset y
    # la misma regla aparecen en más de una, y la key chocaba.
    #
    # El error estuvo latente desde siempre: estos botones solo se dibujan si
    # hay un proveedor de IA configurado, y hasta que se pudo configurar uno
    # desde la interfaz nadie los veía. `ns` distingue el bloque; el resto
    # distingue la fila.
    vistas = {}
    for _, row in broken.iterrows():
        icon = "🟡" if row["status"] == "warn" else "🔴"
        with st.expander(f"{icon} {row['rule_id']} — {row['description']}", expanded=False):
            fix = suggest_fix(row["rule_id"], row["dimension"], row["column"],
                              int(row["affected_rows"]), lang)
            st.markdown(f"**{t('fix_local_title', lang)}**")
            st.markdown(f"**{t('fix_root', lang)}:** {fix['root_cause']}")
            st.markdown(f"**{t('fix_short', lang)}:** {fix['short_term']}")
            st.markdown(f"**{t('fix_long', lang)}:** {fix['long_term']}")
            st.caption(f"{t('fix_owner', lang)}: {fix['owner']}")

            if provider:
                # dataset+regla no alcanza: una misma regla puede evaluarse
                # sobre varias columnas. Y si aun asi se repite, se agrega un
                # sufijo — vale mas una key fea que una pantalla que revienta.
                base = (f"ai_fix_{ns}_{row['dataset']}_{row['rule_id']}"
                        f"_{row['column']}_{lang}")
                vistas[base] = vistas.get(base, 0) + 1
                cache_key = base if vistas[base] == 1 else f"{base}#{vistas[base]}"
                if st.button(t("fix_ai_button", lang).format(provider=provider_label(provider)),
                            key=f"btn_{cache_key}"):
                    with st.spinner(t("fix_ai_loading", lang)):
                        st.session_state[cache_key] = ai_suggest_fix(
                            row["dataset"], row["column"], row["dimension"],
                            row["description"], int(row["affected_rows"]),
                            lang, provider) or "error"
                cached = st.session_state.get(cache_key)
                if cached == "error":
                    st.warning(t("fix_ai_error", lang))
                elif cached:
                    st.divider()
                    st.markdown(f"**{t('fix_ai_title', lang).format(provider=provider_label(provider))}**")
                    st.markdown(f"**{t('fix_root', lang)}:** {cached['root_cause']}")
                    st.markdown(f"**{t('fix_short', lang)}:** {cached['short_term']}")
                    st.markdown(f"**{t('fix_long', lang)}:** {cached['long_term']}")
                    st.caption(f"{t('fix_owner', lang)}: {cached['owner']}")

# --------------------------------------------------------------- Panorama
with tab_ov:
    cat = _con_usuario(gov_scope.combined_catalog(lang, tables) if incl_samples
                       else catalog_df(lang, tables), "catalog", lang)
    dic = _con_usuario(gov_scope.combined_dictionary(lang) if incl_samples
                       else dictionary_df(lang), "dictionary", lang)
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
        _B = {True: "", False: "—"}
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
    st.info(t("lab_intro", lang))
    steps = {s["step_id"]: s for s in lab_steps(lang)}
    lab = _lab(lang)

    def _theory(step_id: str):
        s = steps[step_id]
        st.subheader(s["title"])
        tc1, tc2 = st.columns(2)
        tc1.markdown(f"**{t('lab_plain', lang)}**  \n{s['plain']}")
        tc2.markdown(f"**{t('lab_tech', lang)}**  \n{s['tech']}")
        if s["dmbok_area"]:
            st.caption(f"{t('lab_dmbok_tag', lang)}: {s['dmbok_area']}")

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
        st.info(t("dk_intro", lang))

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
        st.info(t("co_intro", lang))

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
        st.info(t("iso_intro", lang))

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
    st.info(t("cat_intro", lang))
    cat = _con_usuario(gov_scope.combined_catalog(lang, tables) if incl_samples
                       else catalog_df(lang, tables), "catalog", lang)
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
    _cat_ds_opts = (list(_mis_datasets()) + dataset_names()
                    + (ext_samples.sample_keys() if incl_samples else []))
    # Los datasets del usuario van PRIMEROS en la lista: si cargó algo, es lo
    # que vino a mirar.
    ds = st.selectbox(t("cat_pick", lang), _cat_ds_opts)
    dic = _con_usuario(gov_scope.combined_dictionary(lang, ds) if incl_samples
                       else dictionary_df(lang, ds), "dictionary", lang)
    if ds:
        dic = dic[dic["dataset"] == ds].reset_index(drop=True)
    st.dataframe(dic.rename(columns={
        "column": t("col_column", lang), "type": t("col_type", lang),
        "pii": t("col_pii", lang), "business_term": t("col_term", lang),
        "description": t("col_description", lang),
    }).drop(columns=["dataset"]), width="stretch", hide_index=True)

# --------------------------------------------------------------------- MDM
with tab_mdm:
    st.info(t("mdm_intro", lang))
    st.caption(t("mdm_warning", lang))

    # Deduplicar es de las cosas más útiles que se le pueden hacer a un
    # archivo propio; que MDM solo ofreciera la demo dejaba afuera justo el
    # caso que le interesa a quien está evaluando el producto.
    _mdm_usuario = dict(_mis_datasets())
    _mdm_demo_options = {"dim_customers": tables["dim_customers"]}
    _mdm_sample_keys = ext_samples.sample_keys()
    mdm_source_names = (list(_mdm_usuario) + list(_mdm_demo_options)
                        + list(_mdm_sample_keys))

    def _mdm_label(key):
        if key in _mdm_usuario:
            return f"{key} ({t('scope_user_domain', lang)})"
        if key in _mdm_demo_options:
            return f"dim_customers ({t('mdm_src_demo', lang)})"
        meta = ext_samples.sample_meta(key, lang)
        return f"{meta['name']}"

    mdm_pick = st.selectbox(t("mdm_pick_dataset", lang), mdm_source_names,
                            format_func=_mdm_label, key="mdm_pick_dataset")
    if mdm_pick in _mdm_usuario:
        mdm_df = _mdm_usuario[mdm_pick]
    elif mdm_pick in _mdm_demo_options:
        mdm_df = _mdm_demo_options[mdm_pick]
    else:
        mdm_df = ext_samples.load_sample_table(mdm_pick)
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
            _error(exc, lang)

    mdm_report = st.session_state.get("mdm_report")
    mdm_clusters = st.session_state.get("mdm_clusters")
    if mdm_report is not None and st.session_state.get("mdm_df_key") == mdm_pick:
        if mdm_report.empty:
            st.success(t("mdm_none_found", lang))
        else:
            st.subheader(t("mdm_results", lang).format(n=len(mdm_report)))
            st.dataframe(mdm_report.drop(columns="row_indices").rename(columns={
                "cluster_id": t("mdm_col_cluster", lang), "rows": t("mdm_col_rows", lang),
                "confidence": t("mdm_col_confidence", lang), "matched_on": t("mdm_col_matched", lang),
            }), width="stretch", hide_index=True)

            for _mc in mdm_clusters:
                _title = (f"{len(_mc.row_indices)} {t('mdm_rows_label', lang)} · "
                         f"{round(_mc.confidence * 100, 1)}% · {', '.join(_mc.matched_on) or '—'}")
                with st.expander(_title):
                    st.dataframe(mdm_df.loc[_mc.row_indices], width="stretch")
                    st.markdown(f"**{t('mdm_golden_title', lang)}**")
                    golden = mdm.build_golden_record(mdm_df, _mc)
                    st.dataframe(pd.DataFrame([golden]), width="stretch", hide_index=True)

# ---------------------------------------------------------------- Calidad
with tab_q:
    st.info(t("q_intro", lang))
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

    _render_fixes(results, lang, ns="calidad")

    matrix = quality_matrix(results)
    matrix.columns = [_DIM_LABEL[c] for c in matrix.columns]
    fig = px.imshow(matrix, text_auto=".1f", aspect="auto",
                    color_continuous_scale=["#e05c5c", "#f2b441", "#00c896"],
                    zmin=90, zmax=100, title=t("q_heatmap", lang))
    fig.update_layout(**_PLOTLY_LAYOUT, height=380)
    st.plotly_chart(fig, width="stretch")

# ----------------------------------------------------------------- Linaje
with tab_lin:
    st.info(t("lin_intro", lang))
    if incl_samples:
        _lin_nodes, _lin_edges = gov_scope.combined_lineage(lang)
    else:
        _lin_nodes, _lin_edges = NODES, None
    # El linaje honesto de lo que cargó el usuario: origen → dataset → BI.
    # Sin esto, su dataset aparecía en el catálogo y en calidad pero el grafo
    # seguía siendo el de la demo, como si su archivo no existiera.
    if _mis_datasets():
        _lin_nodes, _lin_edges = gov_scope.user_lineage(
            _mis_datasets(), lang, nodes=_lin_nodes, edges=_lin_edges)
    _lin_propio = _lin_edges is not None
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
                         nodes=_lin_nodes if _lin_propio else None,
                         edges=_lin_edges)
    st.plotly_chart(fig, width="stretch")
    with st.expander(t("tbl_lineage", lang)):
        # La tabla se arma del MISMO grafo que el dibujo: si se recalculara
        # aparte, el diagrama mostraría el dataset del usuario y la tabla no.
        st.dataframe(gov_scope.lineage_to_df(_lin_nodes, _lin_edges)
                     if _lin_propio else lineage_df(),
                     width="stretch", hide_index=True)

# --------------------------------------------------------------- Glosario
with tab_g:
    st.info(t("g_intro", lang))
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
    st.info(t("ga_intro", lang))
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
                    _error(exc, lang, "generico")
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
    st.info(t("cu_intro", lang))
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
    st.info(t("rs_intro", lang))

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
                _error(exc, lang, "generico")
            except Exception as exc:  # noqa: BLE001 - archivo corrupto
                _error(exc, lang, "generico")
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
    st.info(t("p_intro", lang))
    if incl_samples:
        pdf = policies_df(lang, results,
                          catalog=_con_usuario(gov_scope.combined_catalog(lang, tables),
                                               "catalog", lang),
                          dictionary=_con_usuario(gov_scope.combined_dictionary(lang),
                                                  "dictionary", lang))
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
def _render_dataeng(user_df, dataset_name: str, lang: str):
    """Motor completo de ingeniería de datos (mvdg/dataeng.py) sobre el
    MISMO DataFrame que _render_profile ya perfiló arriba — no arma una
    fuente paralela: reusa lo que el usuario ya cargó, sea archivo o tabla
    de base de datos. Gratis, igual que el resto de esta pestaña: no está
    en FUNCIONES_PAGAS.

    El texto de contenido (issues, roles, fuga, features) sale de
    `dataeng.traducir_resultado()`, el mismo que usa bi_api para el .exe —
    un solo lugar traduce los códigos, no dos que puedan desalinearse.
    """
    with st.expander(t("de_titulo", lang), expanded=False):
        st.caption(t("de_bajada_streamlit", lang))
        cols_disponibles = [""] + [str(c) for c in user_df.columns]
        c1, c2 = st.columns(2)
        target = c1.selectbox(t("de_target", lang), cols_disponibles,
                              key=f"de_target_{dataset_name}")
        columna_tiempo = c2.selectbox(t("de_tiempo_col", lang), cols_disponibles,
                                      key=f"de_tcol_{dataset_name}")
        res_key = f"de_res_{dataset_name}"
        if st.button(t("de_analizar", lang), key=f"de_btn_{dataset_name}"):
            with st.spinner(t("de_leyendo", lang)):
                crudo = dataeng.analizar_tabla(
                    dataset_name, user_df, target=target or None,
                    columna_tiempo=columna_tiempo or None)
                st.session_state[res_key] = dataeng.traducir_resultado(crudo, lang)

        res = st.session_state.get(res_key)
        if not res:
            return

        if res["muestreado"]:
            st.caption(t("de_muestreado", lang))

        cal = res["calidad"]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric(t("de_kpi_filas", lang), res["perfil"]["filas"])
        k2.metric(t("de_kpi_columnas", lang), res["perfil"]["columnas"])
        k3.metric(t("de_kpi_score", lang), cal["score"])
        criticos = sum(1 for i in cal["issues"] if i["severidad"] == "critico")
        k4.metric(t("de_kpi_criticos", lang), criticos)

        st.subheader(t("de_dimensiones_titulo", lang))
        dims = pd.DataFrame([{"dimension": cal["dimensiones_texto"][k], "quality_index": v}
                             for k, v in cal["dimensiones"].items()])
        fig = px.bar(dims, x="dimension", y="quality_index", text="quality_index",
                    color_discrete_sequence=[BRAND["amber"]])
        fig.update_traces(texttemplate="%{text:.1f}")
        fig.update_layout(**_PLOTLY_LAYOUT, yaxis_range=[0, 101], xaxis_title=None,
                          yaxis_title=None, height=260)
        st.plotly_chart(fig, width="stretch", key=f"de_dims_{dataset_name}")

        if res["cambios_tipo"]:
            st.subheader(t("de_tipos_titulo", lang))
            st.dataframe(pd.DataFrame(res["cambios_tipo"]).rename(columns={
                "columna": t("de_tipos_col", lang), "de": t("de_tipos_de", lang),
                "a": t("de_tipos_a", lang)}), width="stretch", hide_index=True)

        st.subheader(t("de_perfil_titulo", lang))
        perfil_df = pd.DataFrame(res["perfil"]["detalle"])
        if not perfil_df.empty:
            cols_mostrar = [c for c in ("columna", "dtype", "rol_texto", "nulos_pct", "unicos")
                            if c in perfil_df.columns]
            st.dataframe(perfil_df[cols_mostrar].rename(columns={
                "columna": t("col_column", lang), "dtype": t("col_type", lang),
                "rol_texto": t("de_perfil_rol", lang), "nulos_pct": t("de_perfil_nulos", lang),
                "unicos": t("de_perfil_unicos", lang)}), width="stretch", hide_index=True)

        st.subheader(t("de_issues_titulo", lang))
        if cal["issues"]:
            issues_df = pd.DataFrame(cal["issues"])
            st.dataframe(issues_df[["severidad_texto", "columna", "detalle", "accion"]].rename(columns={
                "severidad_texto": t("de_issues_severidad", lang),
                "columna": t("de_issues_columna", lang),
                "detalle": t("de_issues_detalle", lang), "accion": t("de_issues_accion", lang)}),
                width="stretch", hide_index=True)
        else:
            st.caption(t("de_issues_sin", lang))

        st.subheader(t("de_claves_titulo", lang))
        if res["claves"]["pk"]:
            pk_df = pd.DataFrame(res["claves"]["pk"])[["columna", "tipo_texto", "confianza_texto"]]
            st.dataframe(pk_df.rename(columns={
                "columna": t("de_pk_columna", lang), "tipo_texto": t("de_pk_tipo", lang),
                "confianza_texto": t("de_pk_confianza", lang)}), width="stretch", hide_index=True)
        else:
            st.caption(t("de_claves_ninguna", lang))

        if res["tiempo"]:
            tiempo = res["tiempo"]
            st.subheader(t("de_tiempo_titulo", lang))
            tc1, tc2, tc3 = st.columns(3)
            tc1.metric(t("de_tiempo_dias_cubiertos", lang), tiempo["dias_cubiertos"])
            tc2.metric(t("de_tiempo_dias_faltantes", lang), tiempo["dias_faltantes"])
            tc3.metric(t("de_tiempo_frescura", lang), tiempo["frescura_dias"])
            if tiempo.get("huecos_texto"):
                st.caption(tiempo["huecos_texto"])
            if tiempo.get("futuras_texto"):
                st.warning(tiempo["futuras_texto"])

        if res["target"]:
            tg = res["target"]
            st.subheader(t("de_target_titulo", lang))
            if tg.get("fugas"):
                st.error(t("de_fuga_titulo", lang))
                for f in tg["fugas"]:
                    st.markdown(f"- **{f['variable']}** — {f['texto']}")
            if tg.get("ranking"):
                st.subheader(t("de_ranking_titulo", lang))
                st.dataframe(pd.DataFrame(tg["ranking"]).rename(columns={
                    "variable": t("de_ranking_variable", lang),
                    "metrica": t("de_ranking_metrica", lang),
                    "valor": t("de_ranking_valor", lang),
                    "fuerza": t("de_ranking_fuerza", lang)}), width="stretch", hide_index=True)

        if res["dicc_features"]:
            st.subheader(t("de_features_titulo", lang))
            feats = pd.DataFrame(res["dicc_features"])
            feats["apto_texto"] = feats["apto_series_temporales"].map(
                lambda v: t("apto_cuidado", lang) if v == "cuidado" else t("apto_si", lang))
            st.dataframe(feats[["feature", "origen", "etiqueta", "apto_texto"]].rename(columns={
                "feature": t("de_features_feature", lang), "origen": t("de_features_origen", lang),
                "etiqueta": t("de_features_calculo", lang),
                "apto_texto": t("de_features_apto", lang)}), width="stretch", hide_index=True)

        if res["ddl"]:
            st.subheader(t("de_ddl_titulo", lang))
            st.code(res["ddl"], language="sql")


def _render_profile(user_df, dataset_name: str | None = None):
    """Perfila y muestra un DataFrame (venga de archivo o de base de datos).
    Además lo deja disponible en session_state para guardarlo en el proyecto
    del cliente (pestaña Proyecto), así el trabajo no se pierde."""
    if user_df is None or not len(user_df):
        return
    if dataset_name:
        _registrar_dataset(dataset_name, user_df)
    info = summary(user_df)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("col_rows", lang), f"{info['rows']:,}")
    c2.metric(t("col_columns_count", lang), info["columns"])
    c3.metric(t("pr_dupes", lang), info["duplicate_rows"])
    c4.metric(t("pr_nulls", lang), f"{info['null_cells_pct']}%")
    st.subheader(t("pr_col_profile", lang))
    st.dataframe(profile_table(user_df).rename(columns={
        "column": t("col_column", lang), "dtype": t("col_type", lang),
        "null_pct": t("pr_nulls", lang), "unique_values": t("pr_unique", lang),
        "possible_pii": t("col_pii", lang),
    }), width="stretch", hide_index=True)
    if info["pii_columns"]:
        st.warning(t("pr_pii_hint", lang))

    # Catálogo de calidad de verdad, no solo perfilado: las reglas se generan
    # a partir del propio archivo y se CORREN contra los datos (score, umbral,
    # pass/warn/fail) — mismo motor que usan los datasets de demo y ejemplo,
    # via mvdg.auto_rules (completitud + unicidad; el resto de las 6
    # dimensiones DAMA depende de reglas de negocio que no se pueden adivinar
    # de un archivo cualquiera, así que no se fingen).
    st.subheader(f"{t('pr_auto_quality', lang)}")
    ares = auto_quality_results(user_df, dataset_name or t("pr_upload", lang), lang)
    if ares.empty:
        st.caption(t("pr_auto_quality_none", lang))
    else:
        st.caption(t("pr_auto_quality_scope", lang))
        k1, k2, k3 = st.columns(3)
        k1.metric(t("kpi_quality", lang), f"{overall_index(ares)} / 100")
        k2.metric(t("kpi_rules_pass", lang), f"{int((ares['status']=='pass').sum())} / {len(ares)}")
        k3.metric(t("col_rows", lang), f"{info['rows']:,}")
        a_show = ares.copy()
        a_show["dimension"] = a_show["dimension"].map(lambda d: _DIM_LABEL.get(d, d))
        a_show["status"] = a_show["status"].map(_STATUS_LABEL)
        st.dataframe(a_show.rename(columns={
            "rule_id": "ID", "dataset": t("col_dataset", lang), "column": t("col_column", lang),
            "dimension": t("q_dimension", lang), "description": t("q_rule", lang),
            "score": t("q_score", lang), "threshold": t("q_threshold", lang),
            "status": t("q_status", lang), "affected_rows": t("q_affected", lang),
        }), width="stretch", hide_index=True)
        adim = quality_by_dimension(ares)
        adim["dimension"] = adim["dimension"].map(lambda d: _DIM_LABEL.get(d, d))
        fig = px.bar(adim, x="dimension", y="quality_index", text="quality_index",
                    color_discrete_sequence=[BRAND["amber"]])
        fig.update_traces(texttemplate="%{text:.1f}")
        fig.update_layout(**_PLOTLY_LAYOUT, yaxis_range=[0, 101], xaxis_title=None,
                          yaxis_title=None, height=260)
        st.plotly_chart(fig, width="stretch",
                        key=f"pr_auto_dims_{dataset_name or 'sinnombre'}")
        _render_fixes(ares, lang, ns="analisis")

    st.subheader(t("pr_suggestions", lang))
    st.caption(t("pr_suggestions_note", lang))
    for s in suggest_rules(user_df, lang):
        st.markdown(f"- {s}")

    # El motor completo de ingeniería de datos, sobre el mismo DataFrame que
    # ya se perfiló arriba. Solo con dataset_name (archivo o base): la
    # comparación genérica de los ejemplos no lo necesita, y sin nombre no
    # hay bajo qué guardar el resultado en session_state.
    if dataset_name:
        _render_dataeng(user_df, dataset_name, lang)

    # El cierre del recorrido comercial: lo que se ve en pantalla, en un
    # Excel para el cliente del consultor. Solo con dataset_name (archivo o
    # base) — la comparación genérica de los ejemplos no lo necesita.
    if dataset_name:
        from mvdg.file_report import file_report_xlsx
        st.download_button(
            t("frep_btn", lang),
            file_report_xlsx(user_df, dataset_name, lang),
            f"mvdg_informe_{dataset_name.rsplit('.', 1)[0]}_{lang}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"frep_dl_{dataset_name}",
        )
        st.caption(t("frep_caption", lang))


with tab_pr:
    st.info(t("pr_intro", lang))
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
        st.subheader(f"{t('pr_example_card', lang)}")
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
            st.caption(f"ℹ {meta['classification_note']}")
        with st.expander("" + t("pr_example_data", lang), expanded=False):
            st.dataframe(ext_samples.load_sample_table(skey).head(20), width="stretch", hide_index=True)

        # --- 2. Métricas: reglas de calidad con umbral/estado (no perfilado genérico) ---
        st.subheader(f"{t('pr_example_metrics', lang)}")
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

        _render_fixes(sres, lang, ns="misdatos")

        # --- 3. Definiciones (glosario) ---
        st.subheader(f"{t('pr_example_glossary_title', lang)}")
        sgloss = ext_samples.sample_glossary_df(skey, lang)
        st.dataframe(sgloss.drop(columns=["term_id"]).rename(columns={
            "term": t("g_term", lang), "definition": t("g_definition", lang),
            "owner": t("col_owner", lang), "linked_datasets": t("g_linked", lang),
        }), width="stretch", hide_index=True)

        # --- 4. Exportar / conectar a BI (Power BI, Tableau, API) ---
        st.subheader(f"{t('pr_example_bi_title', lang)}")
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
                _error(exc, lang, "generico")
                user_df = None
            # Sin la extensión: ahora este nombre es el del dataset en el
            # catálogo, en el linaje y en el bundle de BI, no una etiqueta
            # suelta de una pestaña. "ventas_2026" es un dataset;
            # "ventas_2026.xlsx" es un archivo.
            _render_profile(user_df, dataset_name=os.path.splitext(up.name)[0])
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
            # SQLite es un archivo, no un servidor: pedir la ruta escrita
            # solo sirve si el .db está en esta misma máquina. Subirlo
            # funciona también desde el navegador y en modo servidor.
            _db_up = st.file_uploader(t("db_sqlite_upload", lang),
                                      type=["db", "sqlite", "sqlite3", "db3"],
                                      key="db_sqlite_up")
            if _db_up is not None:
                import tempfile
                _dbdir = tempfile.mkdtemp(prefix="mvdg_sqlite_")
                _dbpath = os.path.join(_dbdir, _db_up.name)
                with open(_dbpath, "wb") as _fh:
                    _fh.write(_db_up.getbuffer())
                st.session_state["db_sqlite_subida"] = _dbpath
            _subida = st.session_state.get("db_sqlite_subida", "")
            if _subida:
                st.caption(f"{t('db_sqlite_uploaded', lang)}: {os.path.basename(_subida)}")
            with st.expander(t("db_sqlite_expander", lang)):
                _escrita = st.text_input(t("db_sqlite_path", lang),
                                         (editing or {}).get("database", ""))
            database = _escrita.strip() or _subida
            host, port, user, pwd = "", None, "", ""
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
            # Nombre propio: `tables` es el diccionario global de datasets
            # gobernados que usan las otras pestañas. Reusarlo acá lo pisaba
            # con una lista de nombres de tablas de la base para lo que
            # quedara del rerun.
            try:
                _db_tables = list_tables(active, password=pwd or None)
            except Exception as exc:  # noqa: BLE001
                _db_tables = []
                _error(exc, lang, "conexion")
            if _db_tables:
                # El máximo era 100.000 y no se podía subir: quien tenía una
                # tabla de 3 millones de filas no tenía forma de traerlas.
                # 0 = sin límite, que es lo que hay que poner para gobernar
                # la tabla entera; el default sigue siendo chico para que la
                # primera consulta a una base desconocida no traiga todo.
                lim = st.number_input(t("db_limit", lang), 0, 100_000_000, 10000,
                                      step=1000, help=t("db_limit_help", lang))
                p1, p2 = st.columns([2, 1])
                table = p1.selectbox(t("db_pick_table", lang), _db_tables)
                if p2.button(t("db_load", lang)):
                    try:
                        _render_profile(load_table(active, table, int(lim), password=pwd or None),
                                        dataset_name=table)
                    except Exception as exc:  # noqa: BLE001
                        _error(exc, lang, "generico")
                sql = st.text_area(t("db_query", lang), "")
                if sql.strip() and st.button(t("db_run_query", lang)):
                    try:
                        _render_profile(run_query(active, sql, int(lim), password=pwd or None),
                                        dataset_name="query_result")
                    except Exception as exc:  # noqa: BLE001
                        _error(exc, lang, "generico")
            else:
                st.caption(t("db_connect_first", lang))

# ---------------------------------------------------------------- BI & API
with tab_bi:
    st.info(t("bi_intro", lang))
    gov = governance_tables(lang, include_samples=incl_samples,
                            user_datasets=_mis_datasets())

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
    st.info(t("mig_intro", lang))

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
        # La vista previa queda libre (es lo que hace lucir el producto); el
        # push REAL contra el Purview de la empresa es lo que se licencia.
        if _mig_ready and _licencia_ok("migracion_purview", lang) and \
                st.button(t("mig_push", lang), type="primary", key="mig_push_pv"):
            with st.spinner("…"):
                try:
                    st.session_state["mig_result"] = purview_export.push_all(
                        _mig_cat, _mig_dic, _mig_glo, curation_lookup=_mig_lookup, dry_run=False)
                    st.success(t("mig_done", lang))
                except Exception as exc:  # noqa: BLE001
                    _error(exc, lang, "generico")
    else:
        _mig_ready = collibra_export.catalog_configured()
        st.caption(t("mig_collibra_env", lang) if not _mig_ready else t("mig_configured", lang))
        if st.button(t("mig_preview", lang), key="mig_prev_cb"):
            st.session_state["mig_result"] = collibra_export.push_all(
                _mig_cat, _mig_dic, _mig_glo, curation_lookup=_mig_lookup, dry_run=True)
        if _mig_ready and _licencia_ok("migracion_collibra", lang) and \
                st.button(t("mig_push", lang), type="primary", key="mig_push_cb"):
            with st.spinner("…"):
                try:
                    st.session_state["mig_result"] = collibra_export.push_all(
                        _mig_cat, _mig_dic, _mig_glo, curation_lookup=_mig_lookup, dry_run=False)
                    st.success(t("mig_done", lang))
                except Exception as exc:  # noqa: BLE001
                    _error(exc, lang, "generico")

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
    st.warning(t("enf_intro", lang))
    e1, e2 = st.columns(2)
    enf_engine = e1.selectbox(t("enf_engine", lang), enforcement.SUPPORTED_MASKING_ENGINES,
                              format_func=lambda k: "PostgreSQL" if k == "postgresql" else "SQL Server")
    _CLASS_OPTS = sorted(_mig_cat["classification"].unique().tolist())
    with st.expander(f"{t('enf_roles', lang)}", expanded=False):
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
    st.info(t("mip_intro", lang))
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
            _error(exc, lang, "archivo", prefijo=f"{ds}: ")
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
                _error(exc, lang, "generico")
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
    st.info(t("azd_intro", lang))
    _azd_ready = azure_discovery.configured()
    st.caption(t("azd_env", lang) if not _azd_ready else t("mig_configured", lang))
    if _azd_ready and st.button(t("azd_run", lang), type="primary"):
        with st.spinner("…"):
            try:
                st.session_state["azd_result"] = azure_discovery.discover_data_resources()
            except Exception as exc:  # noqa: BLE001
                _error(exc, lang, "generico")
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
    st.info(t("cbp_intro", lang))
    _cbp_ready = collibra_export.configured()
    st.caption(t("cbp_env", lang) if not _cbp_ready else t("mig_configured", lang))
    if _cbp_ready and st.button(t("cbp_run", lang), type="primary"):
        with st.spinner("…"):
            try:
                st.session_state["cbp_result"] = collibra_pull.pull_all()
            except Exception as exc:  # noqa: BLE001
                _error(exc, lang, "generico")
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
            st.caption(f"{t('cbp_catalog_skipped', lang)}: {_cbp_res['catalog']['skipped_reason']}")
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
    st.info(t("pvp_intro", lang))
    _pvp_ready = purview_pull.configured()
    st.caption(t("pvp_env", lang) if not _pvp_ready else t("mig_configured", lang))
    if _pvp_ready and st.button(t("pvp_run", lang), type="primary"):
        with st.spinner("…"):
            try:
                st.session_state["pvp_result"] = purview_pull.pull_all()
            except Exception as exc:  # noqa: BLE001
                _error(exc, lang, "generico")
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
    st.info(t("cl_intro", lang))

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

# ------------------------------------------------------------ Relevamiento
with tab_srv:
    # Las preguntas que hay que hacerle al cliente, partidas por área del
    # pipeline. Lo que se responde queda guardado en la carpeta de ESE
    # cliente: las respuestas de una empresa no viajan con las de otra.
    st.info(t("srv_intro", lang))
    _srv_clients = load_clients()
    if not _srv_clients:
        st.warning(t("srv_no_client", lang).format(tab=t("tab_clients", lang)))
    else:
        _srv_opts = {f"{c.get('company', '?')} ({c.get('client_id', '')[:6]})": c
                     for c in _srv_clients}
        _srv_pick = st.selectbox(t("srv_client", lang), list(_srv_opts.keys()),
                                 key="srv_pick_client")
        _srv_cli = _srv_opts[_srv_pick]
        _srv_cid = _srv_cli["client_id"]
        _srv_nombre = _srv_cli.get("company", _srv_cid)

        # Cobertura: qué área quedó sin tocar. Es lo que se mira antes de
        # cerrar una reunión — un 90% en ingesta y 0% en políticas no es la
        # mitad del relevamiento, es todo el riesgo todavía adelante.
        _srv_prog = interview.progress(_srv_cid, lang)
        v1, v2, v3 = st.columns(3)
        v1.metric(t("srv_coverage", lang), f"{interview.overall_coverage(_srv_cid)}%")
        v2.metric(t("srv_kpi_questions", lang), len(interview.questions(lang)))
        v3.metric(t("srv_kpi_areas", lang), len(interview.areas(lang)))
        st.dataframe(_srv_prog, width="stretch", hide_index=True)

        _srv_areas = interview.areas(lang)
        _srv_labels = {a["key"]: f"{a['n']}. {a['titulo']} ({a['preguntas']})"
                       for a in _srv_areas}
        _srv_area = st.selectbox(t("srv_area", lang), list(_srv_labels),
                                 format_func=lambda k: _srv_labels[k],
                                 key="srv_pick_area")

        _srv_guardadas = interview.load_answers(_srv_cid)
        _SRV_ESTADO = {"pendiente": t("srv_st_pending", lang),
                       "respondida": t("srv_st_answered", lang),
                       "no_aplica": t("srv_st_na", lang)}

        for _q in interview.questions(lang, _srv_area):
            _prev = _srv_guardadas.get(_q["id"], {})
            _hecho = _prev.get("estado") == "respondida"
            with st.expander(f"{_q['id']} · {_q['pregunta']}", expanded=not _hecho):
                st.caption(f"**{t('srv_why', lang)}:** {_q['porque']}")
                st.caption(f"**{t('srv_ask_whom', lang)}:** {_q['a_quien']}")
                q1, q2 = st.columns(2)
                _resp_nom = q1.text_input(t("srv_who", lang),
                                          value=_prev.get("responsable", ""),
                                          key=f"srv_who_{_q['id']}")
                _resp_area = q2.text_input(t("srv_who_area", lang),
                                           value=_prev.get("area_responsable", ""),
                                           key=f"srv_area_{_q['id']}")
                _resp = st.text_area(t("srv_answer", lang),
                                     value=_prev.get("respuesta", ""),
                                     key=f"srv_ans_{_q['id']}", height=90)
                _estado = st.radio(
                    t("srv_state", lang), list(_SRV_ESTADO),
                    format_func=lambda k: _SRV_ESTADO[k], horizontal=True,
                    index=list(_SRV_ESTADO).index(_prev.get("estado", "pendiente")),
                    key=f"srv_st_{_q['id']}")

                b1, b2 = st.columns(2)
                if b1.button(t("srv_save", lang), key=f"srv_save_{_q['id']}",
                             type="primary", width="stretch"):
                    interview.save_answer(_srv_cid, _q["id"], respuesta=_resp,
                                          responsable=_resp_nom,
                                          area_responsable=_resp_area,
                                          estado=_estado)
                    st.success(t("srv_saved", lang))
                    st.rerun()

                # El casillero de repreguntas. Las locales salen SIEMPRE — se
                # calculan mirando qué le falta a esta respuesta y no
                # necesitan ni internet ni clave, que es la situación normal
                # en la sala de reuniones de un cliente.
                st.markdown(f"**{t('srv_followups', lang)}**")
                for _r in interview.follow_ups(_q["id"], _resp, lang):
                    st.markdown(f"- {_r}")

                _prov = configured_provider()
                if not _prov:
                    st.caption(t("srv_no_ai", lang))
                elif b2.button(t("srv_ask_ai", lang), key=f"srv_ai_{_q['id']}",
                               width="stretch",
                               help=t("srv_ai_warning", lang)):
                    _extra = interview.ai_follow_ups(_q["id"], _resp, lang)
                    if _extra:
                        st.markdown(f"**{t('srv_followups_ai', lang)}** "
                                    f"({provider_label(_prov)})")
                        for _r in _extra:
                            st.markdown(f"- {_r}")
                    else:
                        st.info(t("srv_ai_failed", lang))

        st.divider()
        st.subheader(t("srv_export", lang))
        _srv_doc = interview.to_document(_srv_cid, lang, _srv_nombre)
        _srv_base = f"relevamiento_{_srv_cid[:8]}_{lang}"
        s1, s2, s3, s4 = st.columns(4)
        s1.download_button(t("tz_dl_html", lang),
                           doc_export.a_html(_srv_doc).encode("utf-8"),
                           f"{_srv_base}.html", "text/html", width="stretch")
        s2.download_button(
            t("tz_dl_docx", lang), doc_export.a_docx(_srv_doc), f"{_srv_base}.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            width="stretch")
        s3.download_button(t("tz_dl_pdf", lang), doc_export.a_pdf(_srv_doc),
                           f"{_srv_base}.pdf", "application/pdf", width="stretch")
        s4.download_button(t("srv_dl_xlsx", lang),
                           to_excel_bytes(interview.answers_df(_srv_cid, lang),
                                          "relevamiento"),
                           f"{_srv_base}.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           width="stretch")

# --------------------------------------------------------------- Reuniones
with tab_mtg:
    st.info(t("mtg_intro", lang))
    _MTG_FUENTES = {"transcripcion": t("mtg_src_transcript", lang),
                    "grabar": t("mtg_src_record", lang),
                    "audio": t("mtg_src_audio", lang),
                    "pegar": t("mtg_src_paste", lang)}
    _mtg_fuente = st.radio(t("mtg_source", lang), list(_MTG_FUENTES),
                           format_func=lambda k: _MTG_FUENTES[k], horizontal=True,
                           key="mtg_fuente")
    _mtg_texto = ""
    _mtg_audio = None
    _mtg_nombre = "reunion.wav"

    if _mtg_fuente == "transcripcion":
        # El camino recomendado: la transcripción que YA generó la
        # plataforma. Ahí el orador viene identificado por el sistema que
        # sabía quién tenía el micrófono abierto, y el audio nunca sale de
        # donde ya estaba.
        st.caption(t("mtg_transcript_help", lang))
        _mtg_up = st.file_uploader(t("mtg_upload_tr", lang),
                                   type=["vtt", "srt", "txt", "json", "csv"],
                                   key="mtg_up_tr")
        if _mtg_up is not None:
            _mtg_texto = _mtg_up.getvalue().decode("utf-8", "replace")
    elif _mtg_fuente == "grabar":
        st.caption(t("mtg_record_help", lang))
        _mtg_rec = st.audio_input(t("mtg_record", lang), key="mtg_rec")
        if _mtg_rec is not None:
            _mtg_audio = _mtg_rec.getvalue()
    elif _mtg_fuente == "audio":
        _mtg_up = st.file_uploader(
            t("mtg_upload_audio", lang),
            type=[e.lstrip(".") for e in transcribe.EXTENSIONES], key="mtg_up_au")
        if _mtg_up is not None:
            _mtg_audio = _mtg_up.getvalue()
            _mtg_nombre = _mtg_up.name
    else:
        _mtg_texto = st.text_area(t("mtg_paste", lang), height=200, key="mtg_paste_in")

    # Transcribir manda el audio a un tercero. Se pide permiso ACÁ, cada vez,
    # y no con una casilla en Configuración que alguien marcó hace meses: el
    # audio de una reunión de un cliente no es un archivo cualquiera.
    if _mtg_audio:
        st.audio(_mtg_audio)
        _mtg_prov = transcribe.proveedor_disponible()
        if not _mtg_prov:
            st.warning(transcribe.motivo("sin_proveedor", lang))
        else:
            st.warning(t("mtg_ai_warning", lang).format(
                proveedor=provider_label(_mtg_prov)))
            if st.checkbox(t("mtg_ai_confirm", lang), key="mtg_ai_ok") and \
                    st.button(t("mtg_transcribe", lang), type="primary",
                              key="mtg_do_tr"):
                with st.spinner(t("mtg_transcribing", lang)):
                    _mtg_res = transcribe.transcribir(_mtg_audio, _mtg_nombre, lang)
                if _mtg_res["ok"]:
                    st.session_state["mtg_texto"] = _mtg_res["texto"]
                    st.success(t("mtg_transcribed", lang))
                else:
                    st.error(_mtg_res["mensaje"])
    _mtg_texto = _mtg_texto or st.session_state.get("mtg_texto", "")

    _mtg_inter = meetings.parse_transcript(_mtg_texto)
    if not _mtg_inter:
        st.caption(t("mtg_empty", lang))
    else:
        m1, m2, m3 = st.columns(3)
        _mtg_tit = m1.text_input(t("mtg_title", lang), key="mtg_titulo")
        _mtg_fec = m2.text_input(t("mtg_date", lang), key="mtg_fecha")
        _mtg_par = m3.text_input(t("mtg_people", lang), key="mtg_participantes")
        _mtg_min = meetings.minutes(_mtg_inter, lang, titulo=_mtg_tit,
                                    fecha=_mtg_fec, participantes=_mtg_par)

        k1, k2, k3 = st.columns(3)
        k1.metric(t("mtg_kpi_turns", lang), _mtg_min["intervenciones"])
        k2.metric(t("mtg_kpi_min", lang), _mtg_min["duracion_min"])
        k3.metric(t("mtg_kpi_findings", lang), len(_mtg_min["hallazgos"]))

        st.subheader(t("mtg_speakers", lang))
        st.caption(t("mtg_speakers_note", lang))
        st.dataframe(_mtg_min["oradores"], width="stretch", hide_index=True)

        st.subheader(t("mtg_findings", lang))
        _mtg_h = _mtg_min["hallazgos"]
        if len(_mtg_h):
            _tipos = sorted(_mtg_h["tipo"].unique().tolist())
            _sel = st.multiselect(t("mtg_filter_type", lang), _tipos, default=_tipos,
                                  key="mtg_filtro_tipo")
            st.dataframe(_mtg_h[_mtg_h["tipo"].isin(_sel)]
                         [["tipo", "minuto", "orador", "cita"]],
                         width="stretch", hide_index=True)
        else:
            st.caption(t("mtg_no_findings", lang))

        st.subheader(t("mtg_pipeline", lang))
        st.caption(t("mtg_pipeline_note", lang))
        _mtg_p = _mtg_min["pipeline"]
        if len(_mtg_p):
            st.dataframe(_mtg_p[["n", "etapa", "minuto", "orador", "cita", "pistas"]],
                         width="stretch", hide_index=True)
        else:
            st.caption(t("mtg_no_pipeline", lang))

        with st.expander(t("mtg_transcript", lang)):
            st.caption(t("mtg_assign_note", lang))
            st.dataframe(_mtg_min["transcripcion"], width="stretch", hide_index=True)

        st.subheader(t("mtg_export", lang))
        _mtg_doc = meetings.to_document(_mtg_min, lang)
        _mtg_base = f"minuta_{lang}"
        g1, g2, g3, g4 = st.columns(4)
        g1.download_button(t("tz_dl_html", lang),
                           doc_export.a_html(_mtg_doc).encode("utf-8"),
                           f"{_mtg_base}.html", "text/html", width="stretch")
        g2.download_button(
            t("tz_dl_docx", lang), doc_export.a_docx(_mtg_doc), f"{_mtg_base}.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            width="stretch")
        g3.download_button(t("tz_dl_pdf", lang), doc_export.a_pdf(_mtg_doc),
                           f"{_mtg_base}.pdf", "application/pdf", width="stretch")
        g4.download_button(t("mtg_dl_xlsx", lang),
                           to_excel_bytes(_mtg_min["transcripcion"], "transcripcion"),
                           f"{_mtg_base}.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           width="stretch")

# ---------------------------------------------------------------- Proyecto
with tab_ws:
    st.info(t("ws_intro", lang))
    ws_clients = load_clients()
    if not ws_clients:
        st.warning(t("ws_no_clients", lang))
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
                        # Guardar en el proyecto del cliente el gobierno que
                        # está viendo, no el de la demo pelada.
                        for _gk, _gv in governance_tables(
                                lang, include_samples=incl_samples,
                                user_datasets=_mis_datasets()).items():
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
                    _error(exc, lang)

        # --- Etapas guardadas ---
        st.subheader(t("ws_stages_title", lang))
        _stages = ws.list_stages(ws_cid)
        if not _stages:
            st.caption(t("ws_no_stages", lang))
        for _sm in _stages:
            _sid = _sm["stage_id"]
            _hdr = (f"{_sm['name']} · {_sm.get('kind', '')} · "
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
                _error(exc, lang, "generico")

        st.caption(t("ws_where", lang).format(path=ws.client_root(ws_cid)))

# ------------------------------------------------------------------- Ayuda
with tab_h:
    st.info(t("h_intro", lang))

    # --- Configuración de IA ------------------------------------------------
    # Antes esto solo se podía hacer con variables de entorno, que para alguien
    # que abre un .exe significa cerrar el programa, tocar el sistema y volver
    # a abrirlo. Y no había forma de elegir el MODELO, que es lo que decide
    # cuánto gasta el usuario en su propia cuenta.
    st.subheader(t("ia_title", lang))
    st.caption(t("ia_intro", lang))

    _ia_prov = st.selectbox(
        t("ia_provider", lang), list(ai_settings.PROVEEDORES),
        format_func=lambda p: ai_settings.PROVEEDORES[p]["etiqueta"],
        key="ia_prov")

    _ia_c1, _ia_c2 = st.columns([2, 1])
    with _ia_c1:
        _ia_key = st.text_input(t("ia_key", lang), type="password",
                                value="", placeholder="••••••••",
                                help=t("ia_key_help", lang), key="ia_key_in")
        if _ia_key:
            _donde = ai_settings.guardar_key(_ia_prov, _ia_key)
            if _donde == "ofuscada":
                st.warning(t("ia_saved_obf", lang))
            else:
                st.success(t("ia_saved", lang))

        # Solo "compatible" necesita que le digan a dónde apuntar; para los
        # demás la URL es fija y preguntarla sería ruido.
        if _ia_prov == "compatible":
            _ia_base = st.text_input(t("ia_base_url", lang),
                                     value=ai_settings.base_url("compatible"),
                                     help=t("ia_base_help", lang), key="ia_base_in")
            if _ia_base != ai_settings.base_url("compatible"):
                ai_settings.guardar_base_url(_ia_base)

    with _ia_c2:
        st.write("")
        if st.button(t("ia_refresh", lang), help=t("ia_refresh_help", lang),
                     key="ia_refresh_btn", use_container_width=True):
            if not ai_settings.leer_key(_ia_prov):
                st.warning(t("ia_need_key", lang))
            else:
                _antes = ai_settings.modelos_conocidos(_ia_prov)
                _lista = ai_settings.refrescar_modelos(_ia_prov)
                # refrescar_modelos conserva la lista anterior si falla, así que
                # "no cambió nada" es la señal de que no se pudo traer.
                if _lista == _antes and not ai_settings.actualizado_en(_ia_prov):
                    st.warning(t("ia_refresh_fail", lang))
                else:
                    st.success(t("ia_refresh_ok", lang).format(n=len(_lista)))

    _ia_modelos = ai_settings.modelos_conocidos(_ia_prov)
    if _ia_modelos:
        _actual = ai_settings.modelo_elegido(_ia_prov)
        _idx = _ia_modelos.index(_actual) if _actual in _ia_modelos else 0
        _elegido = st.selectbox(t("ia_model", lang), _ia_modelos, index=_idx,
                                help=t("ia_model_help", lang), key="ia_model_sel")
        if _elegido != _actual:
            ai_settings.guardar_modelo(_ia_prov, _elegido)

    _ia_activo = configured_provider()
    if _ia_activo:
        st.caption(t("ia_active", lang).format(
            prov=provider_label(_ia_activo),
            model=ai_settings.modelo_elegido(_ia_activo) or "—"))
    else:
        st.caption(t("ia_none", lang))
    st.caption(t("ia_copilot", lang))
    st.divider()

    # --- Cómo está instalado ------------------------------------------------
    # Lo único que cambia entre las dos formas de instalar es DÓNDE queda
    # guardado lo que el usuario hace, y eso no se puede adivinar mirando la
    # pantalla. En la VM de un cliente es la diferencia entre llevarse el
    # trabajo y perderlo al cerrar sesión.
    st.subheader(t("inst_title", lang))
    _inst = install_mode.descripcion(lang)
    st.markdown(f"**{_inst['titulo']}**")
    st.caption(_inst["detalle"])
    st.caption(f"{t('inst_where', lang)}: `{_inst['datos']}`")
    if _inst["datos_fuera_de_la_carpeta"]:
        st.warning(t("inst_fallback", lang))
    st.divider()

    # --- Licencia -----------------------------------------------------------
    st.subheader(t("lic_title", lang))
    _lic = licensing.status()
    st.caption(t("lic_intro", lang))
    if not _lic["emisor_configurado"]:
        st.warning(t("lic_no_issuer", lang))
    _lc1, _lc2 = st.columns([1, 2])
    _lc1.metric(t("lic_plan", lang),
                _lic["plan"] if _lic["licenciado"] else t("lic_demo", lang))
    if _lic["licenciado"]:
        with _lc2:
            st.write(f"**{t('lic_email', lang)}:** {_lic['email'] or '—'}")
            if _lic["vence"]:
                import datetime as _dt
                st.write(f"**{t('lic_expires', lang)}:** "
                         f"{_dt.datetime.fromtimestamp(_lic['vence']):%Y-%m-%d}")
            else:
                st.write(f"**{t('lic_expires', lang)}:** {t('lic_never', lang)}")
        if st.button(t("lic_remove", lang), key="lic_remove_btn"):
            licensing.clear()
            st.success(t("lic_removed", lang))
            st.rerun()
    else:
        _lic_key = st.text_input(t("lic_input", lang), key="lic_key_input",
                                 placeholder="MVDG2.…")
        if st.button(t("lic_activate", lang), type="primary", key="lic_activate_btn"):
            _payload = licensing.save(_lic_key)
            if _payload:
                st.success(t("lic_ok", lang).format(plan=_payload.get("plan")))
                st.rerun()
            else:
                st.error(t("lic_bad", lang))
    st.caption(f"**{t('lic_paid_features', lang)}:** "
               + ", ".join(_lic["funciones_pagas"]))
    st.divider()

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
        with st.expander(f"{sp['title']}"):
            st.caption(f"{t('h_audience', lang)}: {sp['audience']}")
            st.markdown(sp["text"].replace("\n", "  \n"))

    st.subheader(t("h_packs", lang))
    st.markdown(t("h_packs_note", lang))

    st.subheader(t("h_pvfaq", lang))
    st.markdown(t("h_pvfaq_note", lang))
    for item in purview_collibra_faq(lang):
        with st.expander(f"{item['q']}"):
            st.markdown(item["a"])

# ---------------------------------------------------------- Entregable final
with tab_tz:
    # El recorrido completo del dato, contado dos veces: en criollo para quien
    # firma la compra y en técnico para quien mantiene el código. La evidencia
    # de cada etapa sale de ESTA corrida — con lo que el usuario tenga cargado
    # en este momento, no con números de folleto.
    st.info(t("tz_intro", lang))
    _tz_gov = governance_tables(lang, include_samples=incl_samples,
                                user_datasets=_mis_datasets())
    _tz_ctx = dict(
        datasets=_mis_datasets(),
        catalog=_tz_gov["catalog"], dictionary=_tz_gov["dictionary"],
        results=_tz_gov["quality_results"], lineage=_tz_gov["lineage"],
        glossary=_tz_gov["glossary"], policies=_tz_gov["policies"],
        indice=overall_index(results), tablas_bi=sorted(_tz_gov),
    )
    _TZ_VISTAS = {"ambos": t("tz_view_both", lang),
                  "criollo": t("tz_view_plain", lang),
                  "tecnico": t("tz_view_tech", lang)}
    _tz_vista = st.radio(t("tz_view", lang), list(_TZ_VISTAS),
                         format_func=lambda k: _TZ_VISTAS[k], horizontal=True)
    _tz_campos = {"ambos": ("criollo", "tecnico", "porque", "impacto"),
                  "criollo": ("criollo", "impacto"),
                  "tecnico": ("tecnico", "porque")}[_tz_vista]

    _tz_etapas = pipeline_doc.documentar(lang, **_tz_ctx)
    _tz_rot = pipeline_doc.etiquetas(lang)
    _tz_medidas = sum(1 for e in _tz_etapas if e["evidencia"])
    z1, z2, z3 = st.columns(3)
    z1.metric(t("tz_kpi_stages", lang), len(_tz_etapas))
    z2.metric(t("tz_kpi_measured", lang), f"{_tz_medidas} / {len(_tz_etapas)}")
    z3.metric(t("kpi_quality", lang), f"{_tz_ctx['indice']} / 100")

    for _tz_e in _tz_etapas:
        st.markdown(f"##### {_tz_e['n']}. {_tz_e['titulo']}")
        st.caption(f"`{_tz_e['modulo']}`")
        for _tz_campo in _tz_campos:
            st.markdown(f"**{_tz_rot[_tz_campo]}** — {_tz_e[_tz_campo]}")
        if _tz_e["evidencia"]:
            st.success(f"**{_tz_rot['evidencia']}** · {_tz_e['evidencia']}")
        st.divider()

    st.subheader(t("tz_export", lang))
    st.caption(t("tz_export_note", lang))
    _tz_doc = pipeline_doc.documento(lang, **_tz_ctx)
    _tz_nombre = f"mvdg_pipeline_{lang}"
    e1, e2, e3 = st.columns(3)
    e1.download_button(t("tz_dl_html", lang), doc_export.a_html(_tz_doc).encode("utf-8"),
                       f"{_tz_nombre}.html", "text/html", width="stretch")
    e2.download_button(
        t("tz_dl_docx", lang), doc_export.a_docx(_tz_doc), f"{_tz_nombre}.docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        width="stretch")
    e3.download_button(t("tz_dl_pdf", lang), doc_export.a_pdf(_tz_doc),
                       f"{_tz_nombre}.pdf", "application/pdf", width="stretch")

with tab_del:
    st.info(t("del_intro", lang))
    _del_keys = case_deliverable.case_keys()
    _del_key = st.selectbox(
        t("del_pick", lang), _del_keys,
        format_func=lambda k: ext_samples.sample_meta(k, lang)["name"])
    _del = case_deliverable.build_deliverable(_del_key, lang)
    _dm, _dk, _dmig = _del["meta"], _del["kpis"], _del["migration"]

    st.subheader(f"{_dm['name']}")
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
    st.info(t("con_intro", lang))

    with st.expander(t("con_theory", lang)):
        st.caption(t("con_theory_note", lang))
        for _th in data_contracts.theory(lang):
            st.markdown(f"**{_th['concept']}** — {_th['plain']}")
            st.caption(f"{_th['practice']}")

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
    st.info(t("pbi_intro", lang))
    st.caption("" + t("pbi_secure_note", lang))

    _PBI_MODE = {"offline": t("pbi_mode_offline", lang), "tenant": t("pbi_mode_tenant", lang),
                "example": t("pbi_mode_example", lang)}
    pbi_mode = st.radio(t("pbi_mode", lang), ["offline", "tenant", "example"], horizontal=True,
                        key="pbi_mode", format_func=lambda k: _PBI_MODE[k])

    model_out = None
    pbi_err = None
    pbi_single_model = None   # PowerBIModel único (modo offline)
    pbi_models = None         # list[PowerBIModel] (modo tenant)

    if pbi_mode == "offline":
        # Subir el archivo va PRIMERO y es el valor por defecto: escribir una
        # ruta a mano solo funciona si el archivo está en esta misma máquina,
        # cosa que no pasa ni en el modo servidor ni cuando el cliente prueba
        # la demo desde otra computadora. Antes la ruta era lo único visible
        # y además solo aceptaba la CARPETA .pbip, así que quien tenía un
        # .pbit —el caso normal— no tenía por dónde entrar.
        _PBI_SRC = {"zip": t("pbi_src_zip", lang), "path": t("pbi_src_path", lang)}
        pbi_source = st.radio(t("pbi_source", lang), ["zip", "path"], horizontal=True,
                              key="pbi_source", format_func=lambda k: _PBI_SRC[k])
        if pbi_source == "zip":
            up = st.file_uploader(t("pbi_zip", lang), type=["pbit", "pbix", "zip"],
                                  key="pbi_zip")
            st.caption(t("pbi_zip_hint", lang))
            if up is not None:
                import tempfile
                try:
                    with st.spinner(t("pbi_wait", lang)):
                        tmpdir = tempfile.mkdtemp(prefix="mvdg_pbi_")
                        fpath = os.path.join(tmpdir, up.name)
                        with open(fpath, "wb") as fh:
                            fh.write(up.getbuffer())
                        model_out = pbi.ingest_powerbi_file(fpath, lang)
                except Exception as exc:  # noqa: BLE001
                    pbi_err = exc
        else:
            folder = st.text_input(t("pbi_path", lang), key="pbi_path")
            st.caption(t("pbi_path_hint", lang))
            if st.button(t("pbi_load", lang), key="pbi_load_path") and folder.strip():
                try:
                    with st.spinner(t("pbi_wait", lang)):
                        model_out = pbi.ingest_powerbi_file(folder.strip(), lang)
                except Exception as exc:  # noqa: BLE001
                    pbi_err = exc
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
            st.warning(t("pbi_example_tenant_note", lang))
            model_out = pbi.ingest_example_tenant(lang)
            pbi_models = model_out["_models"]
    else:
        if not pbi.tenant_configured():
            st.warning(t("pbi_tenant_off", lang))
        else:
            st.caption(t("pbi_tenant_hint", lang))
            pbi_max_ws = st.number_input(t("pbi_tenant_max_ws", lang), min_value=1, max_value=1000,
                                         value=25, step=5, key="pbi_tenant_max_ws")
            if _licencia_ok("escaneo_tenant_bi", lang) and \
                    st.button(t("pbi_tenant_scan", lang), key="pbi_tenant_scan_btn"):
                try:
                    with st.spinner(t("pbi_wait", lang)):
                        model_out = pbi.ingest_tenant(lang, max_workspaces=int(pbi_max_ws))
                except Exception as exc:  # noqa: BLE001
                    pbi_err = exc
            cached = st.session_state.get("pbi_tenant_result")
            if model_out is not None:
                st.session_state["pbi_tenant_result"] = model_out
            elif cached is not None and not pbi_err:
                model_out = cached
        if model_out is not None:
            pbi_models = model_out["_models"]

    if pbi_err:
        # Traducido y con el "qué hacer" adelante, no el texto crudo de la
        # excepción: para un .pbix el mensaje útil es "guardalo como .pbit",
        # y así se ve en los 3 idiomas.
        _error(pbi_err, lang, "archivo", prefijo=f"{t('pbi_err', lang)}: ")
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
            with st.expander(f"{_m.name}" + (f" · {_m.table}" if _m.table else "")):
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

    # Los servidores MCP oficiales de cada plataforma, con su configuración
    # generada del registro (mvdg/mcp_presets.py) y no escrita a mano acá: si
    # cambia un nombre de paquete, cambia en un solo lugar.
    st.markdown(f'**{t("mcp_bi_title", lang)}**')
    st.caption(t("mcp_bi_intro", lang))
    for _plat in ("Power BI", "Tableau"):
        _srv = mcp_presets.por_plataforma(_plat)
        with st.expander(f"{_plat} — {len(_srv)}"):
            for _pid, _cfg in _srv.items():
                st.markdown(f"**{_cfg['etiqueta']}**")
                st.caption(_cfg["para_que"])
                _c1, _c2 = st.columns(2)
                _c1.caption(f"{_cfg['auth']}")
                _c2.caption(f"{_cfg['requisitos']}")
                if mcp_presets.lanzable_localmente(_pid):
                    st.caption(t("mcp_bi_stdio", lang))
                else:
                    st.caption(t("mcp_bi_http", lang))
                st.code(mcp_presets.config_json(_pid), language="json")
                st.caption(f"[{t('mcp_bi_docs', lang)}]({_cfg['docs']})")
                st.divider()

    st.markdown(f'**{t("mcp_expose_title", lang)}**')
    st.markdown(t("mcp_expose_body", lang))
    import importlib.util as _ilu
    _mcp_ok = _ilu.find_spec("mcp") is not None
    if _mcp_ok:
        st.success(t("mcp_expose_status_ok", lang))
    else:
        st.warning(t("mcp_expose_status_missing", lang))
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

    st.info(t("mcp_honest_note", lang))

with tab_tab:
    st.info(t("tab_intro", lang))

    _TAB_MODE = {"offline": t("tab_mode_offline", lang), "site": t("tab_mode_site", lang),
                "example": t("tab_mode_example", lang)}
    tab_mode = st.radio(t("tab_mode", lang), ["offline", "site", "example"], horizontal=True,
                        key="tab_mode", format_func=lambda k: _TAB_MODE[k])

    if tab_mode == "offline":
        # Igual que en Power BI: primero subir el archivo, que anda siempre;
        # la ruta escrita queda plegada, para cuando el programa corre en la
        # misma máquina donde está el workbook.
        up = st.file_uploader(t("tab_upload", lang), type=["twb", "twbx"], key="tab_upload")
        with st.expander(t("tab_src_path", lang)):
            tpath = st.text_input(t("tab_path", lang), key="tab_path")
            st.caption(t("tab_path_hint", lang))
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
                _error(exc, lang, "archivo", prefijo=f"{t('tab_err', lang)}: ")
    elif tab_mode == "example":
        st.caption(t("tab_example_note", lang))
        st.session_state["tab_scan_result"] = tabl.ingest_example(lang)
    else:
        if not tabl.configured():
            st.warning(t("tab_off", lang))
        else:
            if st.button(t("tab_scan", lang), key="tab_scan_btn"):
                try:
                    with st.spinner(t("tab_wait", lang)):
                        tab_out = tabl.ingest_site(lang)
                    st.session_state["tab_scan_result"] = tab_out
                except Exception as exc:  # noqa: BLE001
                    st.session_state["tab_scan_result"] = None
                    _error(exc, lang, "archivo", prefijo=f"{t('tab_err', lang)}: ")

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
            with st.expander(f"{_f.name}" + (f" · {_f.datasource}" if _f.datasource else "")):
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
    st.warning(t("mcp_tab_caveats", lang))
    st.info(t("mcp_tab_verified", lang))
    st.caption(t("mcp_tab_gov", lang))
