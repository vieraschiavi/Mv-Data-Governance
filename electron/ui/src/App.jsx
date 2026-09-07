// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
/*
 * MV Data Governance · interfaz de escritorio (React).
 *
 * Reemplaza a Streamlit en la versión .exe: consume la API REST del motor
 * (bi_api) y dibuja el gobierno de datos con componentes propios. El .bat
 * portable sigue usando Streamlit — son dos formas de ver EL MISMO motor,
 * no dos productos.
 *
 * Por qué no hay librería de gráficos: las dos vistas que la necesitarían
 * (calidad por dimensión y por dataset) son barras horizontales de 0 a 100.
 * Un <div> con un ancho porcentual las resuelve, y evita sumarle ~500 KB al
 * bundle de un instalador que ya pesa cientos de MB.
 */
import { useCallback, useEffect, useState } from "react";
import {
  activarLicencia, conectores, desactivarLicencia, escanearTenant,
  ingenieriaArchivo, ingenieriaSqlAnalizar, ingenieriaSqlBorrarConexion,
  ingenieriaSqlConexiones, ingenieriaSqlGuardarConexion, ingenieriaSqlProbar,
  ingenieriaSqlTablas, instalacion, licencia, migrar, perfilar,
  renovarLicencia, todo,
} from "./api";
import { t } from "./i18n";
import { Relevamiento, Reuniones } from "./consultoria";
import { num, Tabla } from "./tabla";

const VISTAS = ["panorama", "catalogo", "calidad", "linaje", "glosario",
                "politicas", "misdatos", "ingenieria", "relevamiento",
                "reuniones", "licencia"];

/* ---------------------------------------------------------- componentes */

function Barras({ filas, clave, lang, traducirNombre }) {
  if (!filas.length) return <p className="sub">{t("sin_datos", lang)}</p>;
  return (
    <>
      {filas.map((f, i) => {
        const v = Number(f.quality_index) || 0;
        const nombre = traducirNombre ? traducirNombre(f[clave]) : f[clave];
        return (
          <div className="barra" key={i}>
            <div className="n" title={nombre}>{nombre}</div>
            <div className="pista"><div className="relleno" style={{ width: `${Math.max(0, Math.min(100, v))}%` }} /></div>
            <div className="v">{num(v, 1)}</div>
          </div>
        );
      })}
    </>
  );
}

function Panorama({ d, lang }) {
  const kpi = Object.fromEntries((d.kpis || []).map((k) => [k.kpi, k.value]));
  const columnas = (d.dictionary || []).length;
  const pii = (d.dictionary || []).filter(
    (c) => c.pii === true || String(c.pii).toLowerCase() === "true" || c.pii === "Sí" || c.pii === "Yes").length;
  const dimNombre = (k) => t(`dim_${k}`, lang);

  const tarjetas = [
    ["kpi_datasets", num((d.catalog || []).length)],
    ["kpi_columnas", num(columnas)],
    ["kpi_calidad", `${num(kpi.quality_index, 2)} / 100`],
    ["kpi_reglas", `${num(kpi.rules_pass)} / ${num(kpi.rules_total)}`],
    ["kpi_pii", num(pii)],
    ["kpi_terminos", num((d.glossary || []).length)],
  ];

  return (
    <>
      <h1>{t("panorama", lang)}</h1>
      <p className="sub">{t("local", lang)}</p>
      <div className="kpis">
        {tarjetas.map(([clave, valor]) => (
          <div className="kpi" key={clave}>
            <div className="et">{t(clave, lang)}</div>
            <div className="val">{valor}</div>
          </div>
        ))}
      </div>
      <div className="panel">
        <h2>{t("por_dimension", lang)}</h2>
        <Barras filas={d.quality_by_dimension || []} clave="dimension" lang={lang}
                traducirNombre={dimNombre} />
      </div>
      <div className="panel">
        <h2>{t("por_dataset", lang)}</h2>
        <Barras filas={d.quality_by_dataset || []} clave="dataset" lang={lang} />
      </div>
    </>
  );
}

function Catalogo({ d, lang }) {
  const cols = [
    { clave: "dataset", etiqueta: t("col_dataset", lang),
      render: (f) => <code>{f.dataset}</code> },
    { clave: "domain", etiqueta: t("col_domain", lang) },
    { clave: "description", etiqueta: t("col_description", lang) },
    { clave: "owner", etiqueta: t("col_owner", lang) },
    { clave: "steward", etiqueta: t("col_steward", lang) },
    { clave: "classification", etiqueta: t("col_classification", lang) },
    { clave: "rows", etiqueta: t("col_rows", lang), tipo: "num",
      render: (f) => num(f.rows) },
    { clave: "columns", etiqueta: t("col_columns", lang), tipo: "num",
      render: (f) => num(f.columns) },
  ];
  return (
    <>
      <h1>{t("catalogo", lang)}</h1>
      <p className="sub">{t("col_dataset", lang)} · {t("col_owner", lang)} · {t("col_steward", lang)}</p>
      <Tabla filas={d.catalog || []} columnas={cols} lang={lang} />
      <div className="panel">
        <h2>{t("col_column", lang)}</h2>
        <Tabla
          filas={d.dictionary || []} lang={lang}
          columnas={[
            { clave: "dataset", etiqueta: t("col_dataset", lang), render: (f) => <code>{f.dataset}</code> },
            { clave: "column", etiqueta: t("col_column", lang), render: (f) => <code>{f.column}</code> },
            { clave: "type", etiqueta: t("col_type", lang) },
            { clave: "pii", etiqueta: t("col_pii", lang),
              render: (f) => {
                const es = f.pii === true || String(f.pii).toLowerCase() === "true";
                return <span className={es ? "si" : "no"}>{es ? "" : "—"}</span>;
              } },
            { clave: "business_term", etiqueta: t("col_term", lang) },
            { clave: "description", etiqueta: t("col_description", lang) },
          ]}
        />
      </div>
    </>
  );
}

function Calidad({ d, lang }) {
  const cols = [
    { clave: "rule_id", etiqueta: "ID", render: (f) => <code>{f.rule_id}</code> },
    { clave: "dataset", etiqueta: t("col_dataset", lang), render: (f) => <code>{f.dataset}</code> },
    { clave: "column", etiqueta: t("col_column", lang) },
    { clave: "dimension", etiqueta: t("col_dimension", lang),
      render: (f) => t(`dim_${f.dimension}`, lang) },
    { clave: "description", etiqueta: t("col_rule", lang) },
    { clave: "score", etiqueta: t("col_score", lang), tipo: "num", render: (f) => num(f.score, 1) },
    { clave: "threshold", etiqueta: t("col_threshold", lang), tipo: "num", render: (f) => num(f.threshold, 1) },
    { clave: "status", etiqueta: t("col_status", lang),
      render: (f) => <Estado valor={f.status} lang={lang} /> },
    { clave: "affected_rows", etiqueta: t("col_affected", lang), tipo: "num",
      render: (f) => num(f.affected_rows) },
  ];
  return (
    <>
      <h1>{t("calidad", lang)}</h1>
      <p className="sub">{t("por_dimension", lang)}</p>
      <Tabla filas={d.quality_results || []} columnas={cols} lang={lang} />
    </>
  );
}

function Linaje({ d, lang }) {
  const cols = [
    { clave: "source", etiqueta: t("col_source", lang), render: (f) => <code>{f.source}</code> },
    { clave: "source_layer", etiqueta: t("col_layer", lang) },
    { clave: "target", etiqueta: t("col_target", lang), render: (f) => <code>{f.target}</code> },
    { clave: "target_layer", etiqueta: t("col_layer", lang) + " " },
  ];
  return (
    <>
      <h1>{t("linaje", lang)}</h1>
      <p className="sub">{t("col_source", lang)} → {t("col_target", lang)}</p>
      <Tabla filas={d.lineage || []} columnas={cols} lang={lang} />
    </>
  );
}

function Glosario({ d, lang }) {
  const cols = [
    { clave: "term_id", etiqueta: "ID", render: (f) => <code>{f.term_id}</code> },
    { clave: "term", etiqueta: t("col_term", lang) },
    { clave: "definition", etiqueta: t("col_definition", lang) },
    { clave: "owner", etiqueta: t("col_owner", lang) },
    { clave: "linked_datasets", etiqueta: t("col_linked", lang) },
  ];
  return (
    <>
      <h1>{t("glosario", lang)}</h1>
      <p className="sub">{t("col_definition", lang)}</p>
      <Tabla filas={d.glossary || []} columnas={cols} lang={lang} />
    </>
  );
}

function Politicas({ d, lang }) {
  const cols = [
    { clave: "policy_id", etiqueta: "ID", render: (f) => <code>{f.policy_id}</code> },
    { clave: "policy", etiqueta: t("col_policy", lang) },
    { clave: "category", etiqueta: t("col_category", lang) },
    { clave: "status", etiqueta: t("col_status", lang) },
    { clave: "evidence", etiqueta: t("col_evidence", lang) },
  ];
  return (
    <>
      <h1>{t("politicas", lang)}</h1>
      <p className="sub">{t("col_evidence", lang)}</p>
      <Tabla filas={d.policies || []} columnas={cols} lang={lang} />
    </>
  );
}


/* ---------------------------------------------------------------- licencia
 *
 * Esta vista existe porque el .exe no tenia NINGUNA: sus seis vistas son
 * funciones gratuitas y no habia donde pegar la clave, asi que un cliente que
 * pagaba veia exactamente lo mismo que uno que no. Podia comprar y no tener
 * como usar lo comprado.
 *
 * No decide nada por su cuenta: todo lo resuelve el motor (mvdg/licensing.py)
 * detras de /api/licencia, que revalida la firma Ed25519 en cada lectura. Si
 * alguien edita el archivo de licencia a mano, deja de validar y vuelve a demo.
 */
/* --- Como esta instalado -------------------------------------------------
   Dos formas de instalar y una sola cosa que cambia entre ellas: donde queda
   guardado lo que el usuario hace. En la VM de un cliente eso decide si el
   trabajo sobrevive al cierre de sesion, asi que tiene que verse sin abrir
   una consola. El motor es el que sabe (mvdg/install_mode.py); aca solo se
   muestra. --- */
function Instalacion({ lang }) {
  const [info, setInfo] = useState(null);

  useEffect(() => {
    let vivo = true;
    instalacion(lang).then((i) => { if (vivo) setInfo(i); }).catch(() => {});
    return () => { vivo = false; };
  }, [lang]);

  if (!info) return null;
  return (
    <>
      <h3>{t("inst_titulo", lang)}</h3>
      <p><b>{info.titulo}</b></p>
      <p className="sub">{info.detalle}</p>
      <p className="sub">{t("inst_donde", lang)}: <code>{info.datos}</code></p>
      {info.datos_fuera_de_la_carpeta ? (
        <p className="malo" role="status">{t("inst_aviso", lang)}</p>
      ) : null}
    </>
  );
}

function Licencia({ lang }) {
  const [estado, setEstado] = useState(null);
  const [clave, setClave] = useState("");
  const [msg, setMsg] = useState(null);
  const [ocupado, setOcupado] = useState(false);

  const refrescar = useCallback(() => {
    licencia().then(setEstado).catch((e) => setMsg({ mal: true, txt: e.detalle }));
  }, []);

  // Al abrir: si la licencia viene de una suscripcion, se intenta renovar en
  // silencio. Es lo que hace que un vencimiento a 35 dias no deje afuera a
  // quien sigue pagando — el cliente no tiene que acordarse de nada.
  //
  // Si no hay internet no pasa nada: renovar() devuelve "sin_conexion" y la
  // licencia vigente sigue valiendo hasta su fecha. Por eso no se muestra
  // error en el arranque, solo cuando el usuario aprieta el boton.
  useEffect(() => {
    let vivo = true;
    licencia().then((e) => {
      if (!vivo) return;
      setEstado(e);
      if (e && e.suscripcion) {
        renovarLicencia().then((r) => { if (vivo && r.ok) setEstado(r); })
                         .catch(() => {});
      }
    }).catch((e) => setMsg({ mal: true, txt: e.detalle }));
    return () => { vivo = false; };
  }, []);

  const activar = async () => {
    setOcupado(true);
    setMsg(null);
    try {
      setEstado(await activarLicencia(clave.trim()));
      setClave("");
      setMsg({ mal: false, txt: t("lic_ok", lang) });
    } catch (e) {
      // El motor ya dice por que no vale; repetirlo con otras palabras solo
      // agrega ruido cuando el cliente escribe a soporte.
      setMsg({ mal: true, txt: e.detalle || e.message });
    } finally {
      setOcupado(false);
    }
  };

  const renovar = async () => {
    setOcupado(true);
    setMsg(null);
    try {
      const r = await renovarLicencia();
      setEstado(r);
      // Cada motivo tiene su texto: "no se pudo" a secas obliga al cliente a
      // escribir a soporte para saber si es su tarjeta o su wifi.
      const clave = r.ok ? "lic_renovada"
        : r.motivo === "sin_conexion" ? "lic_sin_conexion"
        : "lic_no_autorizada";
      setMsg({ mal: !r.ok, txt: t(clave, lang) });
    } catch (e) {
      setMsg({ mal: true, txt: t("lic_sin_conexion", lang) });
    } finally {
      setOcupado(false);
    }
  };

  const quitar = async () => {
    setOcupado(true);
    try {
      setEstado(await desactivarLicencia());
      setMsg(null);
    } finally {
      setOcupado(false);
    }
  };

  if (!estado) return <div className="centro"><div className="spinner" /></div>;
  const pago = estado.plan !== "demo";
  const vence = estado.vence
    ? new Date(estado.vence * 1000).toLocaleDateString()
    : null;

  return (
    <section>
      <h2>{t("licencia", lang)}</h2>
      <p className="sub">
        {t("lic_plan", lang)}: <b>{estado.plan}</b>
        {estado.email ? ` · ${t("lic_email", lang)} ${estado.email}` : ""}
        {vence ? ` · ${t("lic_vence", lang)} ${vence}` : ""}
      </p>
      <p>{pago ? t("lic_activa_ayuda", lang) : t("lic_demo_ayuda", lang)}</p>

      {estado.suscripcion ? (
        <p className="sub">{t("lic_sus", lang)}</p>
      ) : null}

      {pago ? (
        <div className="fila">
          {estado.suscripcion ? (
            <button className="btn" onClick={renovar} disabled={ocupado}>
              {t("lic_renovar", lang)}
            </button>
          ) : null}
          <button className="btn" onClick={quitar} disabled={ocupado}>
            {t("lic_quitar", lang)}
          </button>
        </div>
      ) : (
        <div className="fila">
          <label htmlFor="lic-clave">{t("lic_clave", lang)}</label>
          <input id="lic-clave" value={clave} spellCheck="false"
                 placeholder="MVDG2..."
                 onChange={(e) => setClave(e.target.value)} />
          <button className="btn" onClick={activar}
                  disabled={ocupado || !clave.trim()}>
            {t("lic_activar", lang)}
          </button>
        </div>
      )}

      {msg ? (
        <p className={msg.mal ? "malo" : "bueno"} role="status">{msg.txt}</p>
      ) : null}

      <h3>{t("lic_funciones", lang)}</h3>
      <ul>
        {(estado.funciones_pagas || []).map((f) => {
          // Si el motor agrega una funcion nueva y todavia no tiene nombre
          // traducido, se muestra la clave: es feo, pero es preferible a una
          // lista que se queda muda justo cuando aparece algo nuevo.
          const nombre = t(`fn_${f}`, lang);
          return <li key={f}>{nombre === `fn_${f}` ? <code>{f}</code> : nombre}</li>;
        })}
      </ul>
      <p className="sub">{t("lic_nota_exe", lang)}</p>

      <Instalacion lang={lang} />

      <Funciones lang={lang} />
    </section>
  );
}

/* --- Las tres funciones que se cobran ------------------------------------
   Antes esta pantalla LISTABA las funciones pagas y no habia forma de
   usarlas: el cliente pagaba, veia "estas 3 estan desbloqueadas" y no tenia
   donde apretar. Vivian solo en la version Streamlit, que el .exe no levanta.

   La vista previa queda libre a proposito —es lo que hace lucir el producto,
   y deja ver exactamente que se enviaria antes de enviar nada—; lo que se
   licencia es el push REAL contra el sistema de la empresa. --- */
function Funciones({ lang }) {
  const [estado, setEstado] = useState(null);
  const [ocupado, setOcupado] = useState(null);
  const [msg, setMsg] = useState(null);
  const [salida, setSalida] = useState(null);

  useEffect(() => {
    conectores().then(setEstado).catch(() => setEstado(null));
  }, []);

  async function correr(clave, fn) {
    setOcupado(clave);
    setMsg(null);
    setSalida(null);
    try {
      const r = await fn();
      setSalida(r);
      setMsg({ txt: t("fn_listo", lang), mal: false });
    } catch (e) {
      // Cada motivo dice algo distinto y accionable. Mostrarlos todos como
      // "error" hacia que el que SI pago creyera que su licencia no sirve,
      // cuando lo que falta son las credenciales del conector.
      const texto = e.code === "requiere_licencia" ? t("fn_requiere", lang)
        : e.code === "sin_credenciales" ? t("fn_sin_cred", lang)
        : t("fn_fallo", lang);
      setMsg({ txt: texto, mal: true });
    } finally {
      setOcupado(null);
    }
  }

  if (!estado) return null;

  const destinos = [
    ["purview", "fn_migracion_purview", estado.purview],
    ["collibra", "fn_migracion_collibra", estado.collibra],
  ];

  return (
    <div className="funciones">
      <h3>{t("fn_titulo", lang)}</h3>
      <p className="sub">{t("fn_previa_libre", lang)}</p>

      {destinos.map(([destino, clave, info]) => (
        <div className="fn-fila" key={destino}>
          <span>
            {t(clave, lang)}
            {info && !info.configurado
              ? <em className="sub"> · {t("fn_no_conf", lang)}</em> : null}
          </span>
          <span className="fn-botones">
            <button className="btn btn-sec" disabled={ocupado !== null}
                    onClick={() => correr(`${destino}:previa`,
                                          () => migrar(destino, false, lang))}>
              {t("fn_previa", lang)}
            </button>
            <button className="btn" disabled={ocupado !== null}
                    onClick={() => correr(`${destino}:real`,
                                          () => migrar(destino, true, lang))}>
              {t("fn_aplicar", lang)}
            </button>
          </span>
        </div>
      ))}

      <div className="fn-fila">
        <span>{t("fn_escaneo_tenant_bi", lang)}</span>
        <span className="fn-botones">
          <button className="btn" disabled={ocupado !== null}
                  onClick={() => correr("tenant", () => escanearTenant(25, lang))}>
            {t("fn_escanear", lang)}
          </button>
        </span>
      </div>

      {msg ? (
        <p className={msg.mal ? "malo" : "bueno"} role="status">{msg.txt}</p>
      ) : null}
      {salida ? (
        <pre className="fn-salida">{JSON.stringify(salida, null, 2).slice(0, 4000)}</pre>
      ) : null}
    </div>
  );
}

/* --- Mis datos: perfilar tu propio CSV o Excel ---------------------------
   La landing lo anuncia como la primera funcion del producto —«Subí un CSV o
   Excel y obtené al instante esquema, nulos, duplicados, PII detectada y
   reglas sugeridas»— y el .exe no la tenia. Vivia solo en la version
   Streamlit, que el .exe no levanta: el cliente bajaba el programa, buscaba
   la funcion que vio anunciada, y no existia.

   Es gratis, como en Streamlit: no esta en FUNCIONES_PAGAS. Es lo que hace
   que alguien entienda el producto con SUS datos, que es lo que despues se
   compra. --- */
function MisDatos({ lang }) {
  const [datos, setDatos] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  async function elegido(ev) {
    const archivo = ev.target.files && ev.target.files[0];
    if (!archivo) return;
    setCargando(true);
    setError(null);
    setDatos(null);
    try {
      setDatos(await perfilar(archivo, lang));
    } catch (e) {
      setError(e.code === "archivo_muy_grande" ? t("md_grande", lang)
                                               : t("md_malo", lang));
    } finally {
      setCargando(false);
      // Se limpia el input para que elegir DE NUEVO el mismo archivo vuelva a
      // disparar el evento: sin esto, corregir el archivo y reintentar con el
      // mismo nombre no hace nada y parece que el programa se colgo.
      ev.target.value = "";
    }
  }

  const r = datos && datos.resumen;
  return (
    <section>
      <h2>{t("md_titulo", lang)}</h2>
      <p className="sub">{t("md_bajada", lang)}</p>
      <p className="sub">{t("md_privado", lang)}</p>

      <label className="btn md-elegir">
        {cargando ? t("md_leyendo", lang) : t("md_elegir", lang)}
        <input type="file" accept=".csv,.tsv,.txt,.xlsx,.xlsm,.xls"
               onChange={elegido} disabled={cargando} hidden />
      </label>

      {error ? <p className="malo" role="status">{error}</p> : null}
      {!datos && !error && !cargando
        ? <p className="sub md-vacio">{t("md_vacio", lang)}</p> : null}

      {r ? (
        <>
          <div className="md-cifras">
            <div><b>{r.rows}</b><span>{t("md_filas", lang)}</span></div>
            <div><b>{r.columns}</b><span>{t("md_columnas", lang)}</span></div>
            <div><b>{r.duplicate_rows}</b><span>{t("md_duplicados", lang)}</span></div>
            <div><b>{r.null_cells_pct}%</b><span>{t("md_nulos", lang)}</span></div>
            <div><b>{r.pii_columns}</b><span>{t("md_pii", lang)}</span></div>
          </div>
          {datos.truncado
            ? <p className="sub md-truncado">{t("md_truncado", lang)}</p> : null}

          <table className="tabla">
            <thead><tr>
              <th>{t("md_col", lang)}</th><th>{t("md_tipo", lang)}</th>
              <th>{t("md_nulos_pct", lang)}</th><th>{t("md_unicos", lang)}</th>
              <th>{t("md_ejemplo", lang)}</th><th>{t("md_espii", lang)}</th>
            </tr></thead>
            <tbody>
              {datos.perfil.map((c) => (
                <tr key={c.column}>
                  <td>{c.column}</td>
                  <td>{c.dtype}</td>
                  <td>{c.null_pct}</td>
                  <td>{c.unique_values}</td>
                  <td>{String(c.sample === null ? "" : c.sample)}</td>
                  <td>{c.possible_pii ? "PII" : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {datos.reglas && datos.reglas.length ? (
            <>
              <h3>{t("md_reglas", lang)}</h3>
              <ul className="md-reglas">
                {datos.reglas.map((regla, i) => <li key={i}>{regla}</li>)}
              </ul>
            </>
          ) : null}
        </>
      ) : null}
    </section>
  );
}

/* --- Ingeniería de datos: el motor completo (mvdg/dataeng.py) sobre un
   archivo o una base de datos SQL. Gratis, igual que Mis datos: es la
   versión avanzada del mismo perfilador — calidad por 6 dimensiones,
   claves y joins entre tablas, análisis temporal, fuga de información
   contra un target y features listas para modelar, más DDL sugerido.

   El texto de contenido (detalle de issues, rol de columna, riesgo de
   join, motivo de fuga) llega YA TRADUCIDO desde bi_api — el mismo motor
   de idioma que resuelve el resto de la API. Acá no se arma ninguna
   oración, solo se muestra lo que llegó. --- */

const MOTORES_SQL = [
  ["postgresql", "PostgreSQL"], ["mysql", "MySQL / MariaDB"], ["sqlserver", "SQL Server"],
  ["oracle", "Oracle"], ["sqlite", "SQLite (archivo)"], ["synapse", "Azure Synapse"],
  ["snowflake", "Snowflake"], ["bigquery", "Google BigQuery"], ["databricks", "Databricks"],
];

function DimensionesBarras({ dimensiones, dimensionesTexto, lang }) {
  const filas = Object.entries(dimensiones || {}).map(([dim, quality_index]) => ({ dim, quality_index }));
  return <Barras filas={filas} clave="dim" lang={lang}
                 traducirNombre={(k) => (dimensionesTexto || {})[k] || k} />;
}

function ResultadoTabla({ nombre, res, lang }) {
  const cal = res.calidad;
  const criticos = (cal.issues || []).filter((i) => i.severidad === "critico").length;

  return (
    <div className="panel">
      <h3><code>{nombre}</code></h3>
      {res.muestreado ? <p className="sub">{t("de_muestreado", lang)}</p> : null}

      <div className="md-cifras">
        <div><b>{res.perfil.filas}</b><span>{t("de_kpi_filas", lang)}</span></div>
        <div><b>{res.perfil.columnas}</b><span>{t("de_kpi_columnas", lang)}</span></div>
        <div><b>{cal.score}</b><span>{t("de_kpi_score", lang)}</span></div>
        <div><b>{criticos}</b><span>{t("de_kpi_criticos", lang)}</span></div>
      </div>

      <h4>{t("de_dimensiones_titulo", lang)}</h4>
      <DimensionesBarras dimensiones={cal.dimensiones} dimensionesTexto={cal.dimensiones_texto} lang={lang} />

      {res.cambios_tipo && res.cambios_tipo.length ? (
        <>
          <h4>{t("de_tipos_titulo", lang)}</h4>
          <Tabla lang={lang} filas={res.cambios_tipo} columnas={[
            { clave: "columna", etiqueta: t("de_tipos_col", lang), render: (f) => <code>{f.columna}</code> },
            { clave: "de", etiqueta: t("de_tipos_de", lang) },
            { clave: "a", etiqueta: t("de_tipos_a", lang) },
          ]} />
        </>
      ) : null}

      <h4>{t("de_perfil_titulo", lang)}</h4>
      <Tabla lang={lang} filas={res.perfil.detalle || []} columnas={[
        { clave: "columna", etiqueta: t("col_column", lang), render: (f) => <code>{f.columna}</code> },
        { clave: "dtype", etiqueta: t("col_type", lang) },
        { clave: "rol_texto", etiqueta: t("de_perfil_rol", lang) },
        { clave: "nulos_pct", etiqueta: t("de_perfil_nulos", lang), tipo: "num" },
        { clave: "unicos", etiqueta: t("de_perfil_unicos", lang), tipo: "num" },
      ]} />

      <h4>{t("de_issues_titulo", lang)}</h4>
      {cal.issues && cal.issues.length ? (
        <Tabla lang={lang} filas={cal.issues} columnas={[
          { clave: "severidad_texto", etiqueta: "·",
            render: (f) => <span className={`pill sev-${f.severidad}`}>{f.severidad_texto}</span> },
          { clave: "columna", etiqueta: t("de_issues_columna", lang),
            render: (f) => (f.columna ? <code>{f.columna}</code> : "—") },
          { clave: "detalle", etiqueta: t("de_issues_detalle", lang) },
          { clave: "accion", etiqueta: t("de_issues_accion", lang) },
        ]} />
      ) : <p className="sub">{t("de_issues_sin", lang)}</p>}

      <h4>{t("de_claves_titulo", lang)}</h4>
      {res.claves.pk && res.claves.pk.length ? (
        <Tabla lang={lang} filas={res.claves.pk} columnas={[
          { clave: "columna", etiqueta: t("de_pk_columna", lang), render: (f) => <code>{f.columna}</code> },
          { clave: "tipo_texto", etiqueta: t("de_pk_tipo", lang) },
          { clave: "confianza_texto", etiqueta: t("de_pk_confianza", lang) },
        ]} />
      ) : <p className="sub">{t("de_claves_ninguna", lang)}</p>}

      {res.tiempo ? (
        <>
          <h4>{t("de_tiempo_titulo", lang)}</h4>
          <div className="md-cifras">
            <div><b>{res.tiempo.desde && res.tiempo.desde.slice(0, 10)}</b><span>{t("de_tiempo_desde", lang)}</span></div>
            <div><b>{res.tiempo.hasta && res.tiempo.hasta.slice(0, 10)}</b><span>{t("de_tiempo_hasta", lang)}</span></div>
            <div><b>{res.tiempo.dias_cubiertos}</b><span>{t("de_tiempo_dias_cubiertos", lang)}</span></div>
            <div><b>{res.tiempo.dias_faltantes}</b><span>{t("de_tiempo_dias_faltantes", lang)}</span></div>
            <div><b>{res.tiempo.frescura_dias}</b><span>{t("de_tiempo_frescura", lang)}</span></div>
            {res.tiempo.tendencia_texto ? (
              <div><b>{res.tiempo.tendencia_texto}</b><span>{t("de_tiempo_tendencia", lang)}</span></div>
            ) : null}
          </div>
          {res.tiempo.huecos_texto ? <p className="sub">{res.tiempo.huecos_texto}</p> : null}
          {res.tiempo.futuras_texto ? <p className="malo">{res.tiempo.futuras_texto}</p> : null}
        </>
      ) : null}

      {res.target ? (
        <>
          <h4>{t("de_target_titulo", lang)}</h4>
          <div className="md-cifras">
            {res.target.tasa_positivos_pct !== undefined ? (
              <div><b>{res.target.tasa_positivos_pct}%</b><span>{t("de_target_tasa", lang)}</span></div>
            ) : null}
            {res.target.balance_texto ? (
              <div><b>{res.target.balance_texto}</b><span>{t("de_target_balance", lang)}</span></div>
            ) : null}
          </div>

          {res.target.fugas && res.target.fugas.length ? (
            <>
              <h4 className="malo">{t("de_fuga_titulo", lang)}</h4>
              <ul>
                {res.target.fugas.map((f, i) => <li key={i}><code>{f.variable}</code> — {f.texto}</li>)}
              </ul>
            </>
          ) : null}

          {res.target.ranking && res.target.ranking.length ? (
            <>
              <h4>{t("de_ranking_titulo", lang)}</h4>
              <Tabla lang={lang} filas={res.target.ranking} columnas={[
                { clave: "variable", etiqueta: t("de_ranking_variable", lang), render: (f) => <code>{f.variable}</code> },
                { clave: "metrica", etiqueta: t("de_ranking_metrica", lang) },
                { clave: "valor", etiqueta: t("de_ranking_valor", lang), tipo: "num" },
                { clave: "fuerza", etiqueta: t("de_ranking_fuerza", lang), tipo: "num" },
              ]} />
            </>
          ) : null}
        </>
      ) : null}

      {res.dicc_features && res.dicc_features.length ? (
        <>
          <h4>{t("de_features_titulo", lang)}</h4>
          <Tabla lang={lang} filas={res.dicc_features} columnas={[
            { clave: "feature", etiqueta: t("de_features_feature", lang), render: (f) => <code>{f.feature}</code> },
            { clave: "origen", etiqueta: t("de_features_origen", lang) },
            { clave: "etiqueta", etiqueta: t("de_features_calculo", lang),
              render: (f) => (
                <>
                  {f.etiqueta}
                  {f.cuidado_texto ? <em className="sub"> · {f.cuidado_texto}</em> : null}
                </>
              ) },
            { clave: "apto_series_temporales", etiqueta: t("de_features_apto", lang),
              render: (f) => t(f.apto_series_temporales === "cuidado" ? "apto_cuidado" : "apto_si", lang) },
          ]} />
        </>
      ) : null}

      {res.ddl ? (
        <>
          <h4>{t("de_ddl_titulo", lang)}</h4>
          <pre className="fn-salida">{res.ddl}</pre>
        </>
      ) : null}
    </div>
  );
}

function ResultadoAnalisis({ resultado, lang }) {
  if (!resultado) return null;
  const nombres = Object.keys(resultado.tablas || {});
  return (
    <>
      {resultado.truncado_tablas ? <p className="sub">{t("de_truncado_tablas", lang)}</p> : null}
      {resultado.joins && resultado.joins.length ? (
        <div className="panel">
          <h3>{t("de_joins_titulo", lang)}</h3>
          <p className="sub">{t("de_joins_explicacion", lang)}</p>
          <Tabla lang={lang} filas={resultado.joins} columnas={[
            { clave: "izquierda", etiqueta: t("de_joins_izquierda", lang), render: (f) => <code>{f.izquierda}</code> },
            { clave: "derecha", etiqueta: t("de_joins_derecha", lang), render: (f) => <code>{f.derecha}</code> },
            { clave: "columna", etiqueta: t("de_joins_columna", lang), render: (f) => <code>{f.columna}</code> },
            { clave: "solape_pct", etiqueta: t("de_joins_solape", lang), tipo: "num", render: (f) => `${f.solape_pct}%` },
            { clave: "cardinalidad", etiqueta: t("de_joins_cardinalidad", lang) },
            { clave: "riesgo_texto", etiqueta: t("de_joins_riesgo", lang) },
          ]} />
        </div>
      ) : null}
      {nombres.map((n) => <ResultadoTabla key={n} nombre={n} res={resultado.tablas[n]} lang={lang} />)}
    </>
  );
}

function FuenteArchivo({ lang, onAnalizado, target, setTarget, columnaTiempo, setColumnaTiempo }) {
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  async function elegidos(ev) {
    const archivos = Array.from(ev.target.files || []);
    if (!archivos.length) return;
    setCargando(true);
    setError(null);
    try {
      onAnalizado(await ingenieriaArchivo(archivos, { target, columnaTiempo, lang }));
    } catch (e) {
      setError(e.detalle || e.message);
    } finally {
      setCargando(false);
      // mismo motivo que en Mis datos: sin esto, reintentar con el mismo
      // nombre de archivo no dispara el evento onChange.
      ev.target.value = "";
    }
  }

  return (
    <>
      <div className="fila">
        <div>
          <label htmlFor="de-target">{t("de_target", lang)}</label>
          <input id="de-target" value={target} placeholder={t("de_target_ph", lang)}
                 onChange={(e) => setTarget(e.target.value)} />
        </div>
        <div>
          <label htmlFor="de-tcol">{t("de_tiempo_col", lang)}</label>
          <input id="de-tcol" value={columnaTiempo} placeholder={t("de_tiempo_col_ph", lang)}
                 onChange={(e) => setColumnaTiempo(e.target.value)} />
        </div>
      </div>
      <label className="btn md-elegir">
        {cargando ? t("de_leyendo", lang) : t("de_elegir_archivos", lang)}
        <input type="file" multiple
               accept=".csv,.tsv,.txt,.xlsx,.xlsm,.xls,.parquet,.json,.jsonl,.ndjson,.db,.sqlite,.sqlite3,.db3"
               onChange={elegidos} disabled={cargando} hidden />
      </label>
      {error ? <p className="malo" role="status">{error}</p> : null}
    </>
  );
}

function FuenteDb({ lang, onAnalizado, target, setTarget, columnaTiempo, setColumnaTiempo }) {
  const [conexiones, setConexiones] = useState([]);
  const [connId, setConnId] = useState("");
  const [motor, setMotor] = useState("postgresql");
  const [nombre, setNombre] = useState("");
  const [host, setHost] = useState("");
  const [puerto, setPuerto] = useState("");
  const [base, setBase] = useState("");
  const [usuario, setUsuario] = useState("");
  const [clave, setClave] = useState("");
  const [probando, setProbando] = useState(false);
  const [msg, setMsg] = useState(null);
  const [tablasDisponibles, setTablasDisponibles] = useState([]);
  const [tablasElegidas, setTablasElegidas] = useState([]);
  const [query, setQuery] = useState("");
  const [limite, setLimite] = useState(10000);
  const [analizando, setAnalizando] = useState(false);

  const esSqlite = motor === "sqlite";

  useEffect(() => {
    ingenieriaSqlConexiones().then(setConexiones).catch(() => setConexiones([]));
  }, []);

  function perfilActual() {
    return {
      conn_id: connId || undefined, name: nombre, engine: motor,
      host: esSqlite ? "" : host, port: esSqlite ? null : (puerto || null),
      database: base, user: esSqlite ? "" : usuario, password: esSqlite ? "" : clave,
    };
  }

  function elegirGuardada(id) {
    setConnId(id);
    setTablasDisponibles([]);
    setTablasElegidas([]);
    setMsg(null);
    const c = conexiones.find((x) => x.conn_id === id);
    if (!c) return;
    setMotor(c.engine || "postgresql");
    setNombre(c.name || "");
    setHost(c.host || "");
    setPuerto(c.port ? String(c.port) : "");
    setBase(c.database || "");
    setUsuario(c.user || "");
    setClave("");
  }

  async function probar() {
    setProbando(true);
    setMsg(null);
    setTablasDisponibles([]);
    try {
      const r = await ingenieriaSqlProbar(perfilActual());
      setMsg({ mal: !r.ok, txt: r.mensaje });
      if (r.ok) {
        const rt = await ingenieriaSqlTablas(perfilActual());
        setTablasDisponibles(rt.tablas || []);
      }
    } catch (e) {
      setMsg({ mal: true, txt: e.detalle || e.message });
    } finally {
      setProbando(false);
    }
  }

  async function guardar() {
    try {
      const guardada = await ingenieriaSqlGuardarConexion({ ...perfilActual(), save_password: true });
      setConnId(guardada.conn_id);
      setMsg({ mal: false, txt: t("de_db_guardada", lang) });
      setConexiones(await ingenieriaSqlConexiones());
    } catch (e) {
      setMsg({ mal: true, txt: e.detalle || e.message });
    }
  }

  async function borrar(id) {
    await ingenieriaSqlBorrarConexion(id).catch(() => {});
    if (id === connId) setConnId("");
    setConexiones(await ingenieriaSqlConexiones().catch(() => []));
  }

  function alternarTabla(tabla) {
    setTablasElegidas((prev) => (prev.includes(tabla) ? prev.filter((x) => x !== tabla) : [...prev, tabla]));
  }

  async function analizar() {
    setAnalizando(true);
    setMsg(null);
    try {
      const cuerpo = {
        ...perfilActual(), tablas: tablasElegidas, query: query.trim(),
        limite: Number(limite) || undefined, target, columna_tiempo: columnaTiempo,
      };
      onAnalizado(await ingenieriaSqlAnalizar(cuerpo, lang));
    } catch (e) {
      setMsg({ mal: true, txt: e.detalle || e.message });
    } finally {
      setAnalizando(false);
    }
  }

  return (
    <>
      {conexiones.length ? (
        <div className="fila">
          <div>
            <label htmlFor="de-conn">{t("de_db_guardadas", lang)}</label>
            <select id="de-conn" value={connId} onChange={(e) => elegirGuardada(e.target.value)}>
              <option value="">{t("de_db_nueva", lang)}</option>
              {conexiones.map((c) => (
                <option key={c.conn_id} value={c.conn_id}>
                  {c.name || c.host || c.conn_id} ({c.engine})
                </option>
              ))}
            </select>
          </div>
          {connId ? (
            <button type="button" className="btn btn-sec" onClick={() => borrar(connId)}>
              {t("de_db_borrar", lang)}
            </button>
          ) : null}
        </div>
      ) : null}

      <div className="fila">
        <div>
          <label htmlFor="de-motor">{t("de_db_motor", lang)}</label>
          <select id="de-motor" value={motor} onChange={(e) => setMotor(e.target.value)}>
            {MOTORES_SQL.map(([k, etq]) => <option key={k} value={k}>{etq}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="de-nombre">{t("de_db_nombre", lang)}</label>
          <input id="de-nombre" value={nombre} onChange={(e) => setNombre(e.target.value)} />
        </div>
      </div>

      {esSqlite ? (
        <div className="fila">
          <div>
            <label htmlFor="de-base">{t("de_db_ruta_sqlite", lang)}</label>
            <input id="de-base" value={base} onChange={(e) => setBase(e.target.value)} />
          </div>
        </div>
      ) : (
        <>
          <div className="fila">
            <div><label htmlFor="de-host">{t("de_db_host", lang)}</label>
              <input id="de-host" value={host} onChange={(e) => setHost(e.target.value)} /></div>
            <div><label htmlFor="de-puerto">{t("de_db_puerto", lang)}</label>
              <input id="de-puerto" value={puerto} onChange={(e) => setPuerto(e.target.value)} /></div>
            <div><label htmlFor="de-base2">{t("de_db_base", lang)}</label>
              <input id="de-base2" value={base} onChange={(e) => setBase(e.target.value)} /></div>
          </div>
          <div className="fila">
            <div><label htmlFor="de-user">{t("de_db_usuario", lang)}</label>
              <input id="de-user" value={usuario} onChange={(e) => setUsuario(e.target.value)} /></div>
            <div><label htmlFor="de-pass">{t("de_db_clave", lang)}</label>
              <input id="de-pass" type="password" value={clave} onChange={(e) => setClave(e.target.value)} /></div>
          </div>
        </>
      )}

      <div className="fila">
        <button type="button" className="btn" disabled={probando} onClick={probar}>
          {probando ? t("de_db_probando", lang) : t("de_db_probar", lang)}
        </button>
        <button type="button" className="btn btn-sec" onClick={guardar}>
          {t("de_db_guardar", lang)}
        </button>
      </div>
      {msg ? <p className={msg.mal ? "malo" : "bueno"} role="status">{msg.txt}</p> : null}

      {tablasDisponibles.length ? (
        <>
          <p className="sub">{t("de_db_elegir_tablas", lang)}</p>
          <div className="de-tablas-check">
            {tablasDisponibles.map((tb) => (
              <label key={tb}>
                <input type="checkbox" checked={tablasElegidas.includes(tb)}
                       onChange={() => alternarTabla(tb)} /> {tb}
              </label>
            ))}
          </div>
        </>
      ) : (msg && !msg.mal ? <p className="sub">{t("de_db_sin_tablas", lang)}</p> : null)}

      <div className="fila">
        <div className="ancho">
          <label htmlFor="de-query">{t("de_db_o_query", lang)}</label>
          <textarea id="de-query" rows={2} placeholder={t("de_db_query_ph", lang)}
                    value={query} onChange={(e) => setQuery(e.target.value)} />
        </div>
      </div>
      <div className="fila">
        <div><label htmlFor="de-target-db">{t("de_target", lang)}</label>
          <input id="de-target-db" value={target} placeholder={t("de_target_ph", lang)}
                 onChange={(e) => setTarget(e.target.value)} /></div>
        <div><label htmlFor="de-tcol-db">{t("de_tiempo_col", lang)}</label>
          <input id="de-tcol-db" value={columnaTiempo} placeholder={t("de_tiempo_col_ph", lang)}
                 onChange={(e) => setColumnaTiempo(e.target.value)} /></div>
        <div><label htmlFor="de-limite">{t("de_db_limite", lang)}</label>
          <input id="de-limite" type="number" min="1" value={limite}
                 onChange={(e) => setLimite(e.target.value)} /></div>
      </div>

      <button type="button" className="btn" disabled={analizando || (!tablasElegidas.length && !query.trim())}
              onClick={analizar}>
        {analizando ? t("de_leyendo", lang) : t("de_analizar", lang)}
      </button>
    </>
  );
}

function Ingenieria({ lang }) {
  const [fuente, setFuente] = useState("archivo");
  const [target, setTarget] = useState("");
  const [columnaTiempo, setColumnaTiempo] = useState("");
  const [resultado, setResultado] = useState(null);

  return (
    <section>
      <h2>{t("de_titulo", lang)}</h2>
      <p className="sub">{t("de_bajada", lang)}</p>
      <p className="sub">{t("de_privado", lang)}</p>

      <div className="idiomas" role="group" aria-label={t("de_fuente", lang)}>
        <button className={fuente === "archivo" ? "on" : ""} onClick={() => setFuente("archivo")}>
          {t("de_fuente_archivo", lang)}
        </button>
        <button className={fuente === "db" ? "on" : ""} onClick={() => setFuente("db")}>
          {t("de_fuente_db", lang)}
        </button>
      </div>

      {fuente === "archivo" ? (
        <FuenteArchivo lang={lang} onAnalizado={setResultado}
                       target={target} setTarget={setTarget}
                       columnaTiempo={columnaTiempo} setColumnaTiempo={setColumnaTiempo} />
      ) : (
        <FuenteDb lang={lang} onAnalizado={setResultado}
                  target={target} setTarget={setTarget}
                  columnaTiempo={columnaTiempo} setColumnaTiempo={setColumnaTiempo} />
      )}

      {!resultado ? <p className="sub md-vacio">{t("de_vacio", lang)}</p> : null}
      <ResultadoAnalisis resultado={resultado} lang={lang} />
    </section>
  );
}

const RENDER = { panorama: Panorama, catalogo: Catalogo, calidad: Calidad,
                 linaje: Linaje, glosario: Glosario, politicas: Politicas,
                 misdatos: MisDatos, ingenieria: Ingenieria,
                 relevamiento: Relevamiento, reuniones: Reuniones,
                 licencia: Licencia };

/* ----------------------------------------------------------------- app */

export default function App() {
  const [lang, setLang] = useState("es");
  const [vista, setVista] = useState("panorama");
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState(null);

  const cargar = useCallback(async (idioma) => {
    setError(null);
    setDatos(null);
    try {
      setDatos(await todo(idioma));
    } catch (e) {
      setError(e);
    }
  }, []);

  useEffect(() => { cargar(lang); }, [lang, cargar]);
  useEffect(() => { document.documentElement.lang = lang; }, [lang]);

  const Vista = RENDER[vista];

  return (
    <div className="app">
      <header className="top">
        <div className="marca">
          <span className="escudo" aria-hidden="true"></span>
          <span>
            <b>MV Data Governance</b>
            <small>Catálogo · Calidad · Linaje · Glosario · Políticas</small>
          </span>
        </div>
        <div className="der">
          <div className="idiomas" role="group" aria-label="Idioma">
            {["es", "en", "pt"].map((l) => (
              <button key={l} className={l === lang ? "on" : ""}
                      aria-pressed={l === lang}
                      onClick={() => setLang(l)}>{l.toUpperCase()}</button>
            ))}
          </div>
        </div>
      </header>

      <nav className="tabs">
        {VISTAS.map((v) => (
          <button key={v} className={v === vista ? "on" : ""}
                  aria-current={v === vista ? "page" : undefined}
                  onClick={() => setVista(v)}>{t(v, lang)}</button>
        ))}
      </nav>

      <main className="cuerpo">
        {error ? (
          <div className="centro">
            <h2>{t("error_titulo", lang)}</h2>
            <p>{t("error_ayuda", lang)}</p>
            <div className="detalle">{error.detalle || error.message}</div>
            <button className="btn" onClick={() => cargar(lang)}>{t("reintentar", lang)}</button>
          </div>
        ) : !datos ? (
          <div className="centro">
            <div className="spinner" />
            <p>{t("cargando", lang)}</p>
          </div>
        ) : (
          <Vista d={datos} lang={lang} />
        )}
      </main>

      <footer className="pie">
        <span>{t("local", lang)}</span>
        <span className="der">MV Data Governance</span>
      </footer>
    </div>
  );
}
