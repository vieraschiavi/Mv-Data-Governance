// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
/*
 * MV Data Governance · las dos vistas de lo que pasa ANTES de tocar un dato:
 * Relevamiento (qué preguntarle al cliente) y Reuniones (qué se dijo).
 *
 * Por qué están acá y no en App.jsx
 * ---------------------------------
 * App.jsx ya pasa las mil líneas. Estas dos vistas suman trescientas más y
 * no comparten estado con las otras: van en su propio archivo, que es la
 * regla del repo y encima hace que se puedan leer solas.
 *
 * Qué NO hay acá
 * --------------
 * Ninguna lógica de negocio. El banco de preguntas, el detector de
 * respuestas a medias y el parser de transcripciones viven en Python
 * (mvdg/interview.py, mvdg/meetings.py) y esta vista los consulta por la
 * API. Reimplementarlos en JavaScript daría dos motores que se separan en el
 * primer cambio, y el que se probaría menos es justo el del .exe — que es el
 * que corre en la máquina del cliente.
 */
import { useCallback, useEffect, useRef, useState } from "react";

import {
  descargarMinuta, empresas, relevamientoEstado, relevamientoGuardar,
  relevamientoPreguntas, relevamientoRepreguntas, reunionMinuta,
  transcribirAudio, transcripcionEstado, urlRelevamientoDoc,
} from "./api";
import { t } from "./i18n";
import { Tabla } from "./tabla";

const FORMATOS = [["html", "tz_dl_html"], ["docx", "tz_dl_docx"],
                  ["pdf", "tz_dl_pdf"], ["xlsx", "srv_dl_xlsx"]];

/* ------------------------------------------------------------ relevamiento */

/**
 * Una pregunta del banco: el porqué, a quién preguntarle, los campos para
 * anotar la respuesta, y el casillero de repreguntas.
 *
 * Las repreguntas locales se piden apenas cambia la respuesta guardada: son
 * un cálculo del servidor sin red hacia afuera, así que no hay motivo para
 * escondérselas al consultor detrás de un botón.
 */
function Pregunta({ q, guardada, lang, onGuardar, ia }) {
  const [resp, setResp] = useState(guardada.respuesta || "");
  const [quien, setQuien] = useState(guardada.responsable || "");
  const [area, setArea] = useState(guardada.area_responsable || "");
  const [estado, setEstado] = useState(guardada.estado || "pendiente");
  /* Abierto/cerrado lo maneja el USUARIO. Estuvo atado a `estado` y el
     resultado era absurdo: escribías la respuesta, el estado pasaba a
     "respondida" y React cerraba la pregunta que estabas contestando, con el
     botón de guardar adentro. Se inicializa con lo que había GUARDADO —lo ya
     respondido arranca plegado— y a partir de ahí manda el clic. */
  const [abierto, setAbierto] = useState(guardada.estado !== "respondida");
  const [repre, setRepre] = useState([]);
  const [repreIa, setRepreIa] = useState(null);
  const [msg, setMsg] = useState(null);
  const [ocupado, setOcupado] = useState(false);

  useEffect(() => {
    let vivo = true;
    relevamientoRepreguntas(q.id, guardada.respuesta || "", lang)
      .then((r) => { if (vivo) setRepre(r.repreguntas || []); })
      .catch(() => {});
    return () => { vivo = false; };
  }, [q.id, guardada.respuesta, lang]);

  /* El selector de estado tiene que decir lo que se va a guardar.
     Antes no lo hacía: se escribía la respuesta, se apretaba Guardar y
     quedaba "pendiente", porque el selector seguía en el valor con el que se
     abrió. La cobertura no subía nunca y no había forma de darse cuenta sin
     mirar el JSON. Lo encontró la prueba en Chromium contra la API real.
     "No aplica" es una decisión explícita y no se pisa. */
  useEffect(() => {
    setEstado((actual) => {
      if (actual === "no_aplica") return actual;
      return resp.trim() ? "respondida" : "pendiente";
    });
  }, [resp]);

  const guardar = async () => {
    setOcupado(true);
    setMsg(null);
    try {
      await onGuardar({ id: q.id, respuesta: resp, responsable: quien,
                        area_responsable: area, estado });
      setMsg({ mal: false, txt: t("srv_saved", lang) });
    } catch (e) {
      setMsg({ mal: true, txt: e.detalle || e.message });
    } finally {
      setOcupado(false);
    }
  };

  const pedirIa = async () => {
    setOcupado(true);
    setRepreIa(null);
    try {
      const r = await relevamientoRepreguntas(q.id, resp, lang, true);
      setRepreIa(r.repreguntas_ia && r.repreguntas_ia.length
        ? r.repreguntas_ia : []);
    } catch {
      setRepreIa([]);
    } finally {
      setOcupado(false);
    }
  };

  return (
    <details className="panel" open={abierto}
             onToggle={(e) => setAbierto(e.currentTarget.open)}>
      <summary><b>{q.id}</b> · {q.pregunta}</summary>
      <p className="sub"><b>{t("srv_why", lang)}:</b> {q.porque}</p>
      <p className="sub"><b>{t("srv_ask_whom", lang)}:</b> {q.a_quien}</p>

      <div className="fila">
        <div>
          <label htmlFor={`q-${q.id}`}>{t("srv_who", lang)}</label>
          <input id={`q-${q.id}`} value={quien} onChange={(e) => setQuien(e.target.value)} />
        </div>
        <div>
          <label htmlFor={`a-${q.id}`}>{t("srv_who_area", lang)}</label>
          <input id={`a-${q.id}`} value={area} onChange={(e) => setArea(e.target.value)} />
        </div>
        <div>
          <label htmlFor={`e-${q.id}`}>{t("srv_state", lang)}</label>
          <select id={`e-${q.id}`} value={estado} onChange={(e) => setEstado(e.target.value)}>
            <option value="pendiente">{t("srv_st_pending", lang)}</option>
            <option value="respondida">{t("srv_st_answered", lang)}</option>
            <option value="no_aplica">{t("srv_st_na", lang)}</option>
          </select>
        </div>
      </div>
      <div className="fila">
        <div className="ancho">
          <label htmlFor={`r-${q.id}`}>{t("srv_answer", lang)}</label>
          <textarea id={`r-${q.id}`} rows="3" value={resp}
                    onChange={(e) => setResp(e.target.value)} />
        </div>
      </div>

      <div className="fila">
        <button className="btn" onClick={guardar} disabled={ocupado}>
          {t("srv_save", lang)}
        </button>
        {ia.disponible ? (
          <button className="btn btn-sec" onClick={pedirIa} disabled={ocupado}
                  title={t("srv_ai_warning", lang)}>
            {t("srv_ask_ai", lang)}
          </button>
        ) : null}
      </div>
      {msg ? <p className={msg.mal ? "malo" : "bueno"} role="status">{msg.txt}</p> : null}

      <h3>{t("srv_followups", lang)}</h3>
      <ul>{repre.map((r, i) => <li key={i}>{r}</li>)}</ul>
      {ia.disponible ? null : <p className="sub">{t("srv_no_ai", lang)}</p>}
      {repreIa === null ? null : repreIa.length ? (
        <>
          <h3>{t("srv_followups_ai", lang)}</h3>
          <ul>{repreIa.map((r, i) => <li key={i}>{r}</li>)}</ul>
        </>
      ) : <p className="sub">{t("srv_ai_failed", lang)}</p>}
    </details>
  );
}

export function Relevamiento({ lang }) {
  const [lista, setLista] = useState(null);
  const [cid, setCid] = useState("");
  const [banco, setBanco] = useState(null);
  const [estado, setEstado] = useState(null);
  const [area, setArea] = useState("");
  const [ia, setIa] = useState({ disponible: false });
  const [error, setError] = useState(null);

  useEffect(() => {
    let vivo = true;
    Promise.all([empresas(), transcripcionEstado(lang)])
      .then(([e, i]) => {
        if (!vivo) return;
        setLista(e);
        setIa(i);
        if (e.length && !cid) setCid(e[0].client_id);
      })
      .catch((err) => { if (vivo) setError(err); });
    return () => { vivo = false; };
    // `cid` a propósito fuera: solo se usa para elegir el primero al abrir.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang]);

  useEffect(() => {
    let vivo = true;
    relevamientoPreguntas(lang)
      .then((b) => { if (vivo) { setBanco(b); if (!area) setArea(b.areas[0].key); } })
      .catch((err) => { if (vivo) setError(err); });
    return () => { vivo = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang]);

  const refrescar = useCallback(() => {
    if (!cid) return;
    relevamientoEstado(cid, lang).then(setEstado).catch(setError);
  }, [cid, lang]);

  useEffect(() => { refrescar(); }, [refrescar]);

  const guardar = async (cuerpo) => {
    await relevamientoGuardar(cid, cuerpo);
    refrescar();
  };

  if (error) {
    return <section><h2>{t("relevamiento", lang)}</h2>
      <p className="malo">{error.detalle || error.message}</p></section>;
  }
  if (!lista || !banco) return <div className="centro"><div className="spinner" /></div>;
  if (!lista.length) {
    return (
      <section>
        <h2>{t("relevamiento", lang)}</h2>
        <p className="sub">{t("srv_intro", lang)}</p>
        <p className="malo">{t("srv_no_client_exe", lang)}</p>
      </section>
    );
  }

  const empresa = lista.find((e) => e.client_id === cid) || lista[0];
  const guardadas = {};
  ((estado && estado.respuestas) || []).forEach((r) => { guardadas[r.id] = r; });

  return (
    <section>
      <h2>{t("relevamiento", lang)}</h2>
      <p className="sub">{t("srv_intro", lang)}</p>

      <div className="fila">
        <div>
          <label htmlFor="srv-empresa">{t("srv_client", lang)}</label>
          <select id="srv-empresa" value={cid} onChange={(e) => setCid(e.target.value)}>
            {lista.map((e) => (
              <option key={e.client_id} value={e.client_id}>{e.company}</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="srv-area">{t("srv_area", lang)}</label>
          <select id="srv-area" value={area} onChange={(e) => setArea(e.target.value)}>
            {banco.areas.map((a) => (
              <option key={a.key} value={a.key}>
                {a.n}. {a.titulo} ({a.preguntas})
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="kpis">
        <div className="kpi">
          <div className="et">{t("srv_coverage", lang)}</div>
          <div className="val">{estado ? `${estado.cobertura}%` : "—"}</div>
        </div>
        <div className="kpi">
          <div className="et">{t("srv_kpi_questions", lang)}</div>
          <div className="val">{banco.preguntas.length}</div>
        </div>
        <div className="kpi">
          <div className="et">{t("srv_kpi_areas", lang)}</div>
          <div className="val">{banco.areas.length}</div>
        </div>
      </div>

      <div className="panel">
        <h2>{t("srv_progress", lang)}</h2>
        <Tabla lang={lang} filas={(estado && estado.por_area) || []} columnas={[
          { clave: "area", etiqueta: t("srv_area", lang) },
          { clave: "preguntas", etiqueta: t("srv_kpi_questions", lang), tipo: "num" },
          { clave: "respondidas", etiqueta: t("srv_st_answered", lang), tipo: "num" },
          { clave: "cobertura_%", etiqueta: t("srv_coverage", lang), tipo: "num" },
        ]} />
      </div>

      {banco.preguntas.filter((q) => q.area === area).map((q) => (
        <Pregunta key={q.id} q={q} lang={lang} ia={ia}
                  guardada={guardadas[q.id] || {}} onGuardar={guardar} />
      ))}

      <h3>{t("srv_export", lang)}</h3>
      <div className="fila">
        {FORMATOS.map(([f, clave]) => (
          <a key={f} className="btn btn-sec" download
             href={urlRelevamientoDoc(cid, f, lang, empresa.company)}>
            {t(clave, lang)}
          </a>
        ))}
      </div>
    </section>
  );
}

/* --------------------------------------------------------------- reuniones */

/**
 * Grabador de la reunión presencial.
 *
 * Un micrófono da UN canal, así que la transcripción que salga de acá no va
 * a saber quién habló. Está dicho en pantalla: la vía buena es la
 * transcripción que ya generó Zoom/Teams/Meet/WebEx, donde el orador viene
 * identificado por el sistema que sabía quién tenía el micrófono abierto.
 *
 * Si el navegador (o la política de la VM del cliente) no da acceso al
 * micrófono, se devuelve el motivo en vez de dejar un botón que no hace
 * nada: en un equipo corporativo ese permiso denegado es lo normal, no la
 * excepción.
 */
function useGrabador(lang) {
  const [grabando, setGrabando] = useState(false);
  const [audio, setAudio] = useState(null);
  const [fallo, setFallo] = useState(null);
  const ref = useRef(null);

  const arrancar = async () => {
    setFallo(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream);
      const trozos = [];
      rec.ondataavailable = (e) => { if (e.data.size) trozos.push(e.data); };
      rec.onstop = () => {
        stream.getTracks().forEach((p) => p.stop());
        const blob = new Blob(trozos, { type: rec.mimeType || "audio/webm" });
        blob.name = "reunion.webm";
        setAudio(blob);
      };
      ref.current = rec;
      rec.start();
      setGrabando(true);
    } catch (e) {
      setFallo(`${t("mtg_no_mic", lang)} (${e.name || e.message})`);
    }
  };

  const parar = () => {
    if (ref.current && ref.current.state !== "inactive") ref.current.stop();
    setGrabando(false);
  };

  return { grabando, audio, fallo, arrancar, parar, limpiar: () => setAudio(null) };
}

const FUENTES = ["transcripcion", "grabar", "audio", "pegar"];

export function Reuniones({ lang }) {
  const [fuente, setFuente] = useState("transcripcion");
  const [texto, setTexto] = useState("");
  const [minuta, setMinuta] = useState(null);
  const [meta, setMeta] = useState({ titulo: "", fecha: "", participantes: "" });
  const [ia, setIa] = useState({ disponible: false });
  const [confirmo, setConfirmo] = useState(false);
  const [ocupado, setOcupado] = useState(false);
  const [msg, setMsg] = useState(null);
  const [tipos, setTipos] = useState([]);
  const grab = useGrabador(lang);

  useEffect(() => {
    let vivo = true;
    transcripcionEstado(lang).then((i) => { if (vivo) setIa(i); }).catch(() => {});
    return () => { vivo = false; };
  }, [lang]);

  useEffect(() => {
    let vivo = true;
    if (!texto.trim()) { setMinuta(null); return undefined; }
    reunionMinuta({ texto, lang, ...meta })
      .then((m) => { if (vivo) { setMinuta(m); setTipos([]); } })
      .catch((e) => { if (vivo) setMsg({ mal: true, txt: e.detalle || e.message }); });
    return () => { vivo = false; };
  }, [texto, lang, meta]);

  const leerTranscripcion = async (ev) => {
    const archivo = ev.target.files && ev.target.files[0];
    ev.target.value = "";
    if (!archivo) return;
    setTexto(await archivo.text());
  };

  const transcribir = async (archivo) => {
    setOcupado(true);
    setMsg(null);
    try {
      const r = await transcribirAudio(archivo, lang);
      setTexto(r.texto);
      setMsg({ mal: false, txt: t("mtg_transcribed", lang) });
    } catch (e) {
      setMsg({ mal: true, txt: e.detalle || e.message });
    } finally {
      setOcupado(false);
    }
  };

  /* Subir un audio ya grabado. Las dos condiciones se chequean ACÁ y no en
     el servidor solo: sin clave el botón no puede hacer nada, y sin la
     confirmación explícita no se manda el audio de una reunión de un cliente
     a ningún lado. */
  const audioElegido = (ev) => {
    const archivo = ev.target.files && ev.target.files[0];
    ev.target.value = "";
    if (!archivo) return;
    if (!ia.disponible) { setMsg({ mal: true, txt: ia.motivo }); return; }
    if (!confirmo) { setMsg({ mal: true, txt: t("mtg_need_confirm", lang) }); return; }
    transcribir(archivo);
  };

  const bajar = async (formato) => {
    setMsg(null);
    try {
      await descargarMinuta({ texto, lang, ...meta }, formato);
    } catch (e) {
      setMsg({ mal: true, txt: e.detalle || e.message });
    }
  };

  const hallazgos = (minuta && minuta.hallazgos) || [];
  const tiposHay = [...new Set(hallazgos.map((h) => h.tipo))];
  const visibles = tipos.length
    ? hallazgos.filter((h) => tipos.includes(h.tipo)) : hallazgos;

  return (
    <section>
      <h2>{t("reuniones", lang)}</h2>
      <p className="sub">{t("mtg_intro", lang)}</p>

      <div className="fila">
        {FUENTES.map((f) => (
          <button key={f} className={`btn ${fuente === f ? "" : "btn-sec"}`}
                  aria-pressed={fuente === f} onClick={() => setFuente(f)}>
            {t(`mtg_src_${f}`, lang)}
          </button>
        ))}
      </div>

      {fuente === "transcripcion" ? (
        <>
          <p className="sub">{t("mtg_transcript_help", lang)}</p>
          <label className="btn md-elegir">
            {t("mtg_upload_tr", lang)}
            <input type="file" accept=".vtt,.srt,.txt,.json,.csv" hidden
                   onChange={leerTranscripcion} />
          </label>
        </>
      ) : null}

      {fuente === "grabar" ? (
        <>
          <p className="sub">{t("mtg_record_help", lang)}</p>
          <div className="fila">
            {grab.grabando ? (
              <button className="btn" onClick={grab.parar}>{t("mtg_stop", lang)}</button>
            ) : (
              <button className="btn" onClick={grab.arrancar}>{t("mtg_record", lang)}</button>
            )}
          </div>
          {grab.fallo ? <p className="malo" role="status">{grab.fallo}</p> : null}
        </>
      ) : null}

      {fuente === "audio" ? (
        <label className="btn md-elegir">
          {t("mtg_upload_audio", lang)}
          <input type="file" accept="audio/*,video/mp4" hidden onChange={audioElegido} />
        </label>
      ) : null}

      {fuente === "pegar" ? (
        <div className="fila">
          <div className="ancho">
            <label htmlFor="mtg-pegar">{t("mtg_paste", lang)}</label>
            <textarea id="mtg-pegar" rows="8" value={texto}
                      onChange={(e) => setTexto(e.target.value)} />
          </div>
        </div>
      ) : null}

      {/* Transcribir manda el audio a un tercero: se pide permiso acá, cada
          vez, con el nombre del proveedor delante. */}
      {(fuente === "grabar" || fuente === "audio") ? (
        ia.disponible ? (
          <>
            <p className="malo">{t("mtg_ai_warning", lang).replace("{proveedor}", ia.etiqueta)}</p>
            <label className="fila">
              <input type="checkbox" checked={confirmo}
                     onChange={(e) => setConfirmo(e.target.checked)} />
              <span>{t("mtg_ai_confirm", lang)}</span>
            </label>
            {grab.audio ? (
              <button className="btn" disabled={!confirmo || ocupado}
                      onClick={() => transcribir(grab.audio)}>
                {ocupado ? t("mtg_transcribing", lang) : t("mtg_transcribe", lang)}
              </button>
            ) : null}
          </>
        ) : <p className="sub">{ia.motivo}</p>
      ) : null}

      {msg ? <p className={msg.mal ? "malo" : "bueno"} role="status">{msg.txt}</p> : null}

      {!minuta ? <p className="sub">{t("mtg_empty", lang)}</p> : (
        <>
          <div className="fila">
            <div>
              <label htmlFor="mtg-tit">{t("mtg_title", lang)}</label>
              <input id="mtg-tit" value={meta.titulo}
                     onChange={(e) => setMeta({ ...meta, titulo: e.target.value })} />
            </div>
            <div>
              <label htmlFor="mtg-fec">{t("mtg_date", lang)}</label>
              <input id="mtg-fec" value={meta.fecha}
                     onChange={(e) => setMeta({ ...meta, fecha: e.target.value })} />
            </div>
            <div>
              <label htmlFor="mtg-par">{t("mtg_people", lang)}</label>
              <input id="mtg-par" value={meta.participantes}
                     onChange={(e) => setMeta({ ...meta, participantes: e.target.value })} />
            </div>
          </div>

          <div className="kpis">
            <div className="kpi">
              <div className="et">{t("mtg_kpi_turns", lang)}</div>
              <div className="val">{minuta.intervenciones}</div>
            </div>
            <div className="kpi">
              <div className="et">{t("mtg_kpi_min", lang)}</div>
              <div className="val">{minuta.duracion_min}</div>
            </div>
            <div className="kpi">
              <div className="et">{t("mtg_kpi_findings", lang)}</div>
              <div className="val">{hallazgos.length}</div>
            </div>
          </div>

          <div className="panel">
            <h2>{t("mtg_speakers", lang)}</h2>
            <p className="sub">{t("mtg_speakers_note", lang)}</p>
            <Tabla lang={lang} filas={minuta.oradores} columnas={[
              { clave: "orador", etiqueta: t("mtg_speakers", lang) },
              { clave: "intervenciones", etiqueta: t("mtg_kpi_turns", lang), tipo: "num" },
              { clave: "palabras", etiqueta: t("mtg_words", lang), tipo: "num" },
              { clave: "peso_%", etiqueta: t("mtg_share", lang), tipo: "num" },
            ]} />
          </div>

          <div className="panel">
            <h2>{t("mtg_findings", lang)}</h2>
            {hallazgos.length ? (
              <>
                <div className="fila">
                  {tiposHay.map((tp) => (
                    <button key={tp} className={`btn ${tipos.includes(tp) || !tipos.length ? "" : "btn-sec"}`}
                            onClick={() => setTipos(tipos.includes(tp)
                              ? tipos.filter((x) => x !== tp) : [...tipos, tp])}>
                      {tp}
                    </button>
                  ))}
                </div>
                <Tabla lang={lang} filas={visibles} columnas={[
                  { clave: "tipo", etiqueta: t("mtg_filter_type", lang) },
                  { clave: "minuto", etiqueta: t("mtg_minute", lang) },
                  { clave: "orador", etiqueta: t("mtg_speakers", lang) },
                  { clave: "cita", etiqueta: t("mtg_quote", lang) },
                ]} />
              </>
            ) : <p className="sub">{t("mtg_no_findings", lang)}</p>}
          </div>

          <div className="panel">
            <h2>{t("mtg_pipeline", lang)}</h2>
            <p className="sub">{t("mtg_pipeline_note", lang)}</p>
            {minuta.pipeline.length ? (
              <Tabla lang={lang} filas={minuta.pipeline} columnas={[
                { clave: "n", etiqueta: "#", tipo: "num" },
                { clave: "etapa", etiqueta: t("mtg_stage", lang) },
                { clave: "minuto", etiqueta: t("mtg_minute", lang) },
                { clave: "orador", etiqueta: t("mtg_speakers", lang) },
                { clave: "cita", etiqueta: t("mtg_quote", lang) },
              ]} />
            ) : <p className="sub">{t("mtg_no_pipeline", lang)}</p>}
          </div>

          <div className="panel">
            <h2>{t("mtg_transcript", lang)}</h2>
            <p className="sub">{t("mtg_assign_note", lang)}</p>
            <Tabla lang={lang} filas={minuta.transcripcion} columnas={[
              { clave: "minuto", etiqueta: t("mtg_minute", lang) },
              { clave: "orador", etiqueta: t("mtg_speakers", lang) },
              { clave: "texto", etiqueta: t("mtg_quote", lang) },
            ]} />
          </div>

          <h3>{t("mtg_export", lang)}</h3>
          <div className="fila">
            {FORMATOS.map(([f, clave]) => (
              <button key={f} className="btn btn-sec" onClick={() => bajar(f)}>
                {t(clave === "srv_dl_xlsx" ? "mtg_dl_xlsx" : clave, lang)}
              </button>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
