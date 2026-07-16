"""
MV Data Governance · Glosario automático desde el esquema de tu base de datos.

El pedido que origina esto: "el glosario debe venir automático de la base de
datos; si aparece abreviado, se pone la palabra completa — y también se puede
modificar a mano". Eso es exactamente lo que hace este módulo:

1. **Automático**: lee SOLO el esquema (nombres de tablas y columnas, cero
   filas de datos) de una conexión guardada en 🔎 Mis datos, y arma un
   borrador de término de glosario por cada columna.
2. **Abreviaturas → palabra completa**: los nombres de columna reales vienen
   abreviados (``fec_pag``, ``imp_tot``, ``cli_id``). Un diccionario local de
   abreviaturas típicas de bases de datos (ES/EN) expande cada pedazo a la
   palabra completa en el idioma de la interfaz — ``fec_pag`` → "fecha pago".
   Es una heurística local y determinística (sin red, sin API externa): lo
   que no reconoce, lo deja tal cual — nunca inventa una expansión.
3. **Editable a mano**: el borrador se muestra en una tabla editable en la
   pestaña 📖 Glosario (podés corregir nombre y definición celda por celda
   antes de guardar), y una vez guardado entra al mismo circuito de
   🖊️ Curaduría que todo lo demás — un Data Owner/Steward lo valida o lo
   reescribe, con nombre, cargo y fecha.

La persistencia reusa ``mvdg.imported`` (fuente "database"), igual que lo
traído de Purview/Collibra — mismo archivo local, misma entrada a Curaduría.
"""
from __future__ import annotations

import re

# abreviatura -> palabra completa por idioma. Cubre las abreviaturas más
# comunes en esquemas SQL reales en español e inglés. Deliberadamente
# conservador: ante la duda, NO expandir (el usuario corrige a mano en la
# tabla editable — mejor un token sin expandir que una expansión inventada).
ABBREVIATIONS: dict[str, dict[str, str]] = {
    "id":    {"es": "identificador", "en": "identifier", "pt": "identificador"},
    "cod":   {"es": "código", "en": "code", "pt": "código"},
    "cd":    {"es": "código", "en": "code", "pt": "código"},
    "desc":  {"es": "descripción", "en": "description", "pt": "descrição"},
    "descr": {"es": "descripción", "en": "description", "pt": "descrição"},
    "cant":  {"es": "cantidad", "en": "quantity", "pt": "quantidade"},
    "qty":   {"es": "cantidad", "en": "quantity", "pt": "quantidade"},
    "num":   {"es": "número", "en": "number", "pt": "número"},
    "nro":   {"es": "número", "en": "number", "pt": "número"},
    "fec":   {"es": "fecha", "en": "date", "pt": "data"},
    "fch":   {"es": "fecha", "en": "date", "pt": "data"},
    "fecha": {"es": "fecha", "en": "date", "pt": "data"},
    "dt":    {"es": "fecha", "en": "date", "pt": "data"},
    "imp":   {"es": "importe", "en": "amount", "pt": "valor"},
    "amt":   {"es": "importe", "en": "amount", "pt": "valor"},
    "mto":   {"es": "monto", "en": "amount", "pt": "montante"},
    "dir":   {"es": "dirección", "en": "address", "pt": "endereço"},
    "addr":  {"es": "dirección", "en": "address", "pt": "endereço"},
    "tel":   {"es": "teléfono", "en": "phone", "pt": "telefone"},
    "cli":   {"es": "cliente", "en": "customer", "pt": "cliente"},
    "cust":  {"es": "cliente", "en": "customer", "pt": "cliente"},
    "prod":  {"es": "producto", "en": "product", "pt": "produto"},
    "prov":  {"es": "proveedor", "en": "supplier", "pt": "fornecedor"},
    "emp":   {"es": "empleado", "en": "employee", "pt": "funcionário"},
    "fac":   {"es": "factura", "en": "invoice", "pt": "fatura"},
    "fact":  {"es": "factura", "en": "invoice", "pt": "fatura"},
    "inv":   {"es": "factura", "en": "invoice", "pt": "fatura"},
    "ped":   {"es": "pedido", "en": "order", "pt": "pedido"},
    "ord":   {"es": "pedido", "en": "order", "pt": "pedido"},
    "pag":   {"es": "pago", "en": "payment", "pt": "pagamento"},
    "pay":   {"es": "pago", "en": "payment", "pt": "pagamento"},
    "ven":   {"es": "venta", "en": "sale", "pt": "venda"},
    "vta":   {"es": "venta", "en": "sale", "pt": "venda"},
    "usr":   {"es": "usuario", "en": "user", "pt": "usuário"},
    "nom":   {"es": "nombre", "en": "name", "pt": "nome"},
    "apel":  {"es": "apellido", "en": "last name", "pt": "sobrenome"},
    "cat":   {"es": "categoría", "en": "category", "pt": "categoria"},
    "est":   {"es": "estado", "en": "status", "pt": "status"},
    "tot":   {"es": "total", "en": "total", "pt": "total"},
    "prec":  {"es": "precio", "en": "price", "pt": "preço"},
    "pr":    {"es": "precio", "en": "price", "pt": "preço"},
    "seg":   {"es": "segmento", "en": "segment", "pt": "segmento"},
    "suc":   {"es": "sucursal", "en": "branch", "pt": "filial"},
    "dep":   {"es": "departamento", "en": "department", "pt": "departamento"},
    "dept":  {"es": "departamento", "en": "department", "pt": "departamento"},
    "reg":   {"es": "registro", "en": "record", "pt": "registro"},
    "ini":   {"es": "inicio", "en": "start", "pt": "início"},
    "max":   {"es": "máximo", "en": "maximum", "pt": "máximo"},
    "min":   {"es": "mínimo", "en": "minimum", "pt": "mínimo"},
    "prom":  {"es": "promedio", "en": "average", "pt": "média"},
    "avg":   {"es": "promedio", "en": "average", "pt": "média"},
    "obs":   {"es": "observaciones", "en": "notes", "pt": "observações"},
    "doc":   {"es": "documento", "en": "document", "pt": "documento"},
    "cta":   {"es": "cuenta", "en": "account", "pt": "conta"},
    "acct":  {"es": "cuenta", "en": "account", "pt": "conta"},
    "moned": {"es": "moneda", "en": "currency", "pt": "moeda"},
    "mon":   {"es": "moneda", "en": "currency", "pt": "moeda"},
    "pais":  {"es": "país", "en": "country", "pt": "país"},
    "loc":   {"es": "localidad", "en": "location", "pt": "localidade"},
    "tipo":  {"es": "tipo", "en": "type", "pt": "tipo"},
    "tp":    {"es": "tipo", "en": "type", "pt": "tipo"},
}

_DEFINITION_TEMPLATE = {
    "es": "Columna «{original}» de la tabla «{table}» de tu base de datos. "
          "Borrador generado automáticamente desde el esquema — corregilo acá "
          "o validalo/reescribilo en 🖊️ Curaduría.",
    "en": "Column “{original}” of table “{table}” in your database. Draft "
          "generated automatically from the schema — fix it here or "
          "validate/rewrite it in 🖊️ Curation.",
    "pt": "Coluna «{original}» da tabela «{table}» do seu banco de dados. "
          "Rascunho gerado automaticamente do esquema — corrija aqui ou "
          "valide/reescreva em 🖊️ Curadoria.",
}


def split_identifier(name: str) -> list[str]:
    """Parte un identificador SQL en tokens: snake_case, kebab-case,
    camelCase/PascalCase y dígitos pegados."""
    # camelCase/PascalCase -> espacios, después separadores clásicos
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", str(name))
    tokens = re.split(r"[\s_\-\.]+", spaced)
    return [t for t in (tok.strip() for tok in tokens) if t]


def expand_identifier(name: str, lang: str = "es") -> tuple[str, bool]:
    """Expande cada token abreviado a su palabra completa en ``lang``.
    Devuelve (frase_expandida, hubo_expansión). Lo que no está en el
    diccionario queda tal cual (en minúsculas) — nunca se inventa."""
    tokens = split_identifier(name)
    out, expanded = [], False
    for tok in tokens:
        low = tok.lower()
        hit = ABBREVIATIONS.get(low)
        if hit:
            out.append(hit.get(lang, hit["es"]))
            if hit.get(lang, hit["es"]) != low:
                expanded = True
        else:
            out.append(low)
    return " ".join(out), expanded


def build_terms_from_schema(schema: dict[str, list[str]], lang: str = "es",
                            conn_id: str = "") -> list[dict]:
    """Un borrador de término por columna, con el nombre expandido y la
    definición plantilla. ``schema`` = {tabla: [columnas]}. El ``database_id``
    es estable (conexión:tabla.columna) para que re-generar haga upsert en
    vez de duplicar."""
    template = _DEFINITION_TEMPLATE.get(lang, _DEFINITION_TEMPLATE["es"])
    terms = []
    for table, columns in schema.items():
        for col in columns:
            name, was_expanded = expand_identifier(col, lang)
            terms.append({
                "database_id": f"{conn_id}:{table}.{col}" if conn_id else f"{table}.{col}",
                "name": name,
                "definition": template.format(original=col, table=table),
                "table": table,
                "column": col,
                "expanded": was_expanded,
            })
    return terms


def build_from_connection(profile: dict, lang: str = "es",
                          password: str | None = None,
                          max_tables: int = 50) -> list[dict]:
    """Pipeline completo contra una conexión guardada: lista las tablas
    (hasta ``max_tables``, tope de cortesía para no colgar la interfaz con
    un esquema gigante), lee SOLO los nombres de columnas de cada una, y
    arma los borradores. Una tabla que falle no frena el resto."""
    from . import connectors

    tables = connectors.list_tables(profile, password=password)[:max_tables]
    schema: dict[str, list[str]] = {}
    for tbl in tables:
        try:
            schema[tbl] = connectors.list_columns(profile, tbl, password=password)
        except Exception:  # noqa: BLE001 - una tabla rota no frena el resto
            continue
    return build_terms_from_schema(schema, lang, conn_id=profile.get("conn_id", ""))
