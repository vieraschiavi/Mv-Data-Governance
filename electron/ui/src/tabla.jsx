// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
/*
 * MV Data Governance · la tabla con buscador, y los dos helpers que la rodean.
 *
 * Vivían dentro de App.jsx. Se sacaron acá cuando aparecieron las vistas de
 * Relevamiento y Reuniones, que las necesitan: importarlas desde App.jsx
 * habría hecho que App importe las vistas y las vistas importen App — una
 * dependencia circular que esbuild resuelve a veces y en el orden equivocado
 * deja un componente en `undefined` sin ningún error de compilación.
 */
import { useMemo, useState } from "react";

import { t } from "./i18n";

/** Un número formateado para mostrar, o "—" si no hay nada que mostrar. */
export const num = (v, dec = 0) =>
  v === null || v === undefined || v === "" || Number.isNaN(Number(v))
    ? "—"
    : Number(v).toLocaleString(undefined, {
        minimumFractionDigits: dec, maximumFractionDigits: dec });

/** Texto plano de una fila, para el buscador. */
const textoDe = (fila) => Object.values(fila).map((v) => String(v ?? "")).join(" ").toLowerCase();

export function useBusqueda(filas) {
  const [q, setQ] = useState("");
  const filtradas = useMemo(() => {
    const texto = q.trim().toLowerCase();
    if (!texto) return filas;
    return filas.filter((f) => textoDe(f).includes(texto));
  }, [filas, q]);
  return { q, setQ, filtradas };
}

/**
 * Tabla con buscador. `columnas` = [{clave, etiqueta, tipo?, render?}].
 * El buscador filtra sobre la fila COMPLETA y no solo sobre las columnas
 * visibles: buscar "PII" o el nombre de un steward tiene que encontrar algo
 * aunque esa columna no se esté mostrando.
 */
export function Tabla({ filas, columnas, lang }) {
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
