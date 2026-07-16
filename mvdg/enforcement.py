"""
MV Data Governance · Enforcement de acceso — generador de DDL, no un proxy.

Honestidad de arquitectura (no negociable): **bloquear una consulta en vivo
requiere estar parado en el camino del dato** — un proxy o gateway entre el
usuario y la base, o una plataforma cloud-native como Purview dentro de
Azure. Un programa de escritorio local que se conecta de a ratos a tus
bases NO puede, ni debe, hacerse pasar por eso: montar un interceptor de
consultas desde acá sería frágil, peligroso en producción, y — sobre
todo — vendería humo sobre lo que este programa realmente es.

Lo que SÍ es honesto y genuinamente útil: este módulo toma lo que el
catálogo ya sabe (qué datasets están clasificados como Confidencial/PII,
qué columnas tienen datos personales) y genera el **DDL real** — GRANT/
REVOKE, Row-Level Security, enmascaramiento de columnas — para que un DBA
(o el propio Purview, si lo tenés) lo revise y lo aplique en la base. El
programa arma la receta; quien tiene las llaves de la base la ejecuta.
Nunca se conecta a ejecutar nada de esto — ``dry_run`` no es un parámetro
acá porque **no hay otro modo**: este módulo solo genera texto SQL.

Motores cubiertos: PostgreSQL (Row-Level Security nativo desde 9.5) y SQL
Server (Dynamic Data Masking + Row-Level Security con predicados de
seguridad, desde 2016). Son los dos motores con soporte nativo de
enforcement declarativo bien establecido; para el resto (MySQL, Oracle,
Snowflake...) el patrón de GRANT/REVOKE por columna aplica igual, pero el
enmascaramiento/RLS tiene sintaxis propia no cubierta todavía acá.
"""
from __future__ import annotations

import pandas as pd

SUPPORTED_MASKING_ENGINES = ("postgresql", "sqlserver")


def _quote_ident(name: str, engine: str) -> str:
    return f"[{name}]" if engine == "sqlserver" else f'"{name}"'


def build_grant_revoke_ddl(catalog: pd.DataFrame, roles_by_classification: dict[str, list[str]],
                           engine: str = "postgresql") -> list[str]:
    """GRANT SELECT sobre cada dataset solo a los roles autorizados para su
    clasificación (``roles_by_classification``, ej. {"PII": ["rol_rrhh"],
    "Confidencial": ["rol_finanzas"], "Pública": ["rol_analista"]}), y
    REVOKE explícito de PUBLIC para no dejar nada abierto por default."""
    ddl = []
    for _, row in catalog.iterrows():
        table = _quote_ident(row["dataset"], engine)
        classification = row.get("classification", "")
        roles = roles_by_classification.get(classification, [])
        ddl.append(f"REVOKE ALL ON {table} FROM PUBLIC;")
        for role in roles:
            ddl.append(f"GRANT SELECT ON {table} TO {_quote_ident(role, engine)};")
    return ddl


def build_column_masking_ddl(dictionary: pd.DataFrame, engine: str = "postgresql",
                             mask_role: str = "rol_sin_pii") -> list[str]:
    """Enmascara las columnas marcadas pii=True del diccionario, para el
    rol que no debe ver el dato real. En PostgreSQL, vía una vista
    enmascarada (no hay masking nativo de columna, a diferencia de SQL
    Server); en SQL Server, vía ADD MASKED WITH (nativo desde 2016)."""
    if engine not in SUPPORTED_MASKING_ENGINES:
        raise ValueError(f"Enmascaramiento no soportado todavía para '{engine}' — "
                         f"motores cubiertos: {', '.join(SUPPORTED_MASKING_ENGINES)}.")
    ddl = []
    pii_cols = dictionary[dictionary["pii"] == True]  # noqa: E712
    if engine == "sqlserver":
        for _, row in pii_cols.iterrows():
            table = _quote_ident(row["dataset"], engine)
            col = _quote_ident(row["column"], engine)
            func = "email()" if "email" in row["column"].lower() or "correo" in row["column"].lower() \
                else "default()"
            ddl.append(f"ALTER TABLE {table} ALTER COLUMN {col} ADD MASKED WITH (FUNCTION = '{func}');")
        if ddl:
            ddl.append(f"-- para que {mask_role} vea el dato real (no enmascarado), sumalo a")
            ddl.append(f"-- db_datareader y ademas: GRANT UNMASK TO {_quote_ident(mask_role, engine)};")
    else:  # postgresql: no hay masking nativo de columna -> vista con columnas ofuscadas
        by_dataset = pii_cols.groupby("dataset")["column"].apply(list).to_dict()
        for dataset, cols in by_dataset.items():
            all_cols = dictionary[dictionary["dataset"] == dataset]["column"].tolist()
            select_list = ", ".join(
                f"'***' AS {_quote_ident(c, engine)}" if c in cols else _quote_ident(c, engine)
                for c in all_cols)
            view = _quote_ident(f"{dataset}_masked", engine)
            table = _quote_ident(dataset, engine)
            ddl.append(f"CREATE OR REPLACE VIEW {view} AS SELECT {select_list} FROM {table};")
        if ddl:
            ddl.append(f"-- dale acceso a {mask_role} sobre las vistas *_masked, "
                       "no sobre las tablas originales (ver build_grant_revoke_ddl).")
    return ddl


def build_row_level_security_ddl(dataset: str, policy_column: str, policy_role: str,
                                 engine: str = "postgresql") -> list[str]:
    """RLS: cada fila solo la ve quien coincide con ``policy_column`` (ej.
    steward_id = current_user, o region = current_setting('app.region')).
    Genera la política declarativa; el valor de comparación en runtime lo
    define quien administra la base (session variable, current_user, etc.)."""
    table = _quote_ident(dataset, engine)
    col = _quote_ident(policy_column, engine)
    if engine == "postgresql":
        return [
            f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;",
            f"CREATE POLICY {dataset}_rls ON {table} FOR SELECT "
            f"TO {_quote_ident(policy_role, engine)} "
            f"USING ({col} = current_setting('app.current_value', true));",
        ]
    if engine == "sqlserver":
        fn = f"dbo.fn_{dataset}_predicate"
        return [
            f"CREATE FUNCTION {fn}(@value AS sysname) RETURNS TABLE "
            f"WITH SCHEMABINDING AS RETURN SELECT 1 AS fn_result "
            f"WHERE @value = SESSION_CONTEXT(N'app_current_value');",
            f"CREATE SECURITY POLICY {dataset}_rls "
            f"ADD FILTER PREDICATE {fn}({col}) ON {table};",
        ]
    raise ValueError(f"RLS no soportado todavía para '{engine}' — "
                     f"motores cubiertos: {', '.join(SUPPORTED_MASKING_ENGINES)}.")


def enforcement_plan(catalog: pd.DataFrame, dictionary: pd.DataFrame,
                     roles_by_classification: dict[str, list[str]] | None = None,
                     engine: str = "postgresql") -> dict:
    """Arma el paquete completo de DDL a partir del catálogo/diccionario ya
    gobernados: GRANT/REVOKE por clasificación + enmascaramiento de
    columnas PII. Devuelve el DDL como texto, listo para copiar — nunca se
    ejecuta desde acá."""
    roles_by_classification = roles_by_classification or {}
    grants = build_grant_revoke_ddl(catalog, roles_by_classification, engine)
    masking = build_column_masking_ddl(dictionary, engine) if engine in SUPPORTED_MASKING_ENGINES else []
    script = "\n".join(
        ["-- MV Data Governance · DDL de enforcement generado, NO ejecutado.",
         "-- Revisalo y correlo vos (o tu DBA / Purview) contra la base real.",
         "", "-- 1) Acceso por clasificación", *grants,
         "", "-- 2) Enmascaramiento de columnas PII", *masking])
    return {"engine": engine, "grant_statements": len(grants), "masking_statements": len(masking),
            "script": script}
