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
import { useCallback, useEffect, useMemo, useState } from "react";
import { activarLicencia, conectores, desactivarLicencia, escanearTenant, licencia, migrar, renovarLicencia, todo } from "./api";
import { t } from "./i18n";

const VISTAS = ["panorama", "catalogo", "calidad", "linaje", "glosario",
                "politicas", "licencia"];

/* ------------------------------------------------------------- helpers */

const num = (v, dec = 0) =>
  v === null || v === undefined || v === "" || Number.isNaN(Number(v))
    ? "—"
    : Number(v).toLocaleString(undefined, {
        minimumFractionDigits: dec, maximumFractionDigits: dec });

/** Texto plano de una fila, para el buscador. */
const textoDe = (fila) => Object.values(fila).map((v) => String(v ?? "")).join(" ").toLowerCase();

function useBusqueda(filas) {
  const [q, setQ] = useState("");
  const filtradas = useMemo(() => {
    const t = q.trim().toLowerCase();
    if (!t) return filas;
    return filas.filter((f) => textoDe(f).includes(t));
  }, [filas, q]);
  return { q, setQ, filtradas };
}

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

/**
 * Tabla con buscador. `columnas` = [{clave, etiqueta, tipo?, render?}].
 * El buscador filtra sobre la fila COMPLETA y no solo sobre las columnas
 * visibles: buscar "PII" o el nombre de un steward tiene que encontrar algo
 * aunque esa columna no se esté mostrando.
 */
function Tabla({ filas, columnas, lang }) {
  const { q, setQ, filtradas } = useBusqueda(filas);
  return (
    <>
      <div className="herramientas">
        <input
          className="buscador" type="search" value={q}
          placeholder={t("buscar", lang)}
          aria-label={t("buscar", lang)}
          onChange={(e) => setQ(e.target.value)}
        />
        <span className="conteo">{filtradas.length} {t("filas", lang)}</span>
      </div>
      {filtradas.length === 0 ? (
        <p className="sub">{t("sin_datos", lang)}</p>
      ) : (
        <div className="tabla-wrap">
          <table>
            <thead>
              <tr>{columnas.map((c) => <th key={c.clave}>{c.etiqueta}</th>)}</tr>
            </thead>
            <tbody>
              {filtradas.map((f, i) => (
                <tr key={i}>
                  {columnas.map((c) => (
                    <td key={c.clave} className={c.tipo === "num" ? "num" : undefined}>
                      {c.render ? c.render(f) : (f[c.clave] ?? "—")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

const Estado = ({ valor, lang }) => (
  <span className={`pill ${valor}`}>{t(`est_${valor}`, lang) || valor}</span>
);

/* -------------------------------------------------------------- vistas */

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

const RENDER = { panorama: Panorama, catalogo: Catalogo, calidad: Calidad,
                 linaje: Linaje, glosario: Glosario, politicas: Politicas,
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
