import React, { useEffect, useState } from "react";

// Textos del launcher en los 3 idiomas del producto; el idioma sale del
// sistema (navigator.language) — dentro del programa ya está el selector.
const T = {
  es: {
    tagline: "Gobierno de datos claro y listo para BI",
    searching_python: "Buscando Python con Streamlit…",
    starting: "Levantando el servidor local…",
    waiting: "Esperando que el programa responda…",
    ready: "Listo — abriendo el programa…",
    no_python: "No se encontró Python con Streamlit. Instalá Python 3.10+ y corré: pip install -r requirements.txt",
    server_died: "El servidor local se cerró inesperadamente.",
    timeout: "El servidor no respondió a tiempo.",
    retry: "Reintentar",
    local: "Todo corre en esta máquina — nada viaja a internet.",
  },
  en: {
    tagline: "Clear, BI-ready data governance",
    searching_python: "Looking for Python with Streamlit…",
    starting: "Starting the local server…",
    waiting: "Waiting for the app to respond…",
    ready: "Ready — opening the app…",
    no_python: "No Python with Streamlit found. Install Python 3.10+ and run: pip install -r requirements.txt",
    server_died: "The local server exited unexpectedly.",
    timeout: "The server didn't respond in time.",
    retry: "Retry",
    local: "Everything runs on this machine — nothing goes to the internet.",
  },
  pt: {
    tagline: "Governança de dados clara e pronta para BI",
    searching_python: "Procurando Python com Streamlit…",
    starting: "Iniciando o servidor local…",
    waiting: "Aguardando o programa responder…",
    ready: "Pronto — abrindo o programa…",
    no_python: "Não foi encontrado Python com Streamlit. Instale Python 3.10+ e rode: pip install -r requirements.txt",
    server_died: "O servidor local fechou inesperadamente.",
    timeout: "O servidor não respondeu a tempo.",
    retry: "Tentar novamente",
    local: "Tudo roda nesta máquina — nada vai para a internet.",
  },
};

function lang() {
  const l = (navigator.language || "es").slice(0, 2);
  return T[l] ? l : "es";
}

const ERROR_KEYS = new Set(["no_python", "server_died", "timeout"]);

export default function App() {
  const t = T[lang()];
  const [status, setStatus] = useState({ key: "starting", detail: "" });
  const [log, setLog] = useState("");

  useEffect(() => {
    if (window.mvdg) {
      window.mvdg.onStatus((s) => {
        if (s.key === "log") setLog(s.detail);
        else setStatus(s);
      });
    }
  }, []);

  const isError = ERROR_KEYS.has(status.key);
  return (
    <div className="wrap">
      <div className="card">
        <div className="brand">
          <span className="shield">🛡️</span>
          <h1>MV <b>Data Governance</b></h1>
        </div>
        <p className="tagline">{t.tagline}</p>
        {!isError && <div className="spinner" aria-label="cargando" />}
        <p className={isError ? "status error" : "status"}>
          {t[status.key] || t.starting}
        </p>
        {status.detail && !isError && <p className="detail">{status.detail}</p>}
        {isError && (
          <button className="retry" onClick={() => window.mvdg && window.mvdg.retry()}>
            {t.retry}
          </button>
        )}
        {log && !isError && <p className="log">{log}</p>}
        <p className="local">{t.local}</p>
      </div>
    </div>
  );
}
