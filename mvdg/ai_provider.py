"""
MV Data Governance · IA externa opcional para las sugerencias de corrección.

Por defecto, las sugerencias de "cómo corregir cada falla" (mvdg.remediation)
son 100% locales y determinísticas — nada sale de la máquina. Este módulo
agrega una capa OPCIONAL: si el usuario configura su propia API key de
Claude, ChatGPT (OpenAI) o Gemini como variable de entorno, cada regla puede
pedir además una sugerencia generada en vivo por ese modelo.

Reglas de diseño (no negociables):
  - Apagado por defecto. Sin ninguna variable de entorno configurada, el
    programa funciona exactamente igual que antes (asistencia local).
  - La API key la pone el usuario en su propio entorno — el programa nunca
    la pide, nunca la guarda, nunca la manda a ningún lado más que al
    proveedor elegido.
  - Solo se manda METADATO de la falla (dataset, columna, dimensión,
    descripción de la regla, cantidad de filas afectadas) — nunca datos
    reales de las filas.
  - Cualquier error (sin conexión, key inválida, timeout, respuesta rara)
    cae en silencio a la sugerencia local; nunca rompe la pantalla.

Nota sobre GitHub Copilot: no se ofrece como proveedor acá porque no expone
una API REST simple de "pedime un texto" con solo una API key, como sí
tienen Claude/OpenAI/Gemini — Copilot se integra vía OAuth de GitHub dentro
de un IDE, no como llamada directa de servidor a servidor. Si en el futuro
GitHub publica una API de ese tipo, se puede agregar con el mismo patrón.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

_TIMEOUT = 20  # segundos

# provider_key -> (env var de la API key, nombre para mostrar, modelo default,
# variable de entorno opcional para overridear el modelo)
_PROVIDERS = {
    "claude": ("ANTHROPIC_API_KEY", "Claude (Anthropic)", "claude-sonnet-5", "MVDG_AI_MODEL_CLAUDE"),
    "openai": ("OPENAI_API_KEY", "ChatGPT (OpenAI)", "gpt-4o-mini", "MVDG_AI_MODEL_OPENAI"),
    "gemini": ("GEMINI_API_KEY", "Gemini (Google)", "gemini-1.5-flash", "MVDG_AI_MODEL_GEMINI"),
}
# orden de preferencia si hay más de una key cargada; MVDG_AI_PROVIDER fuerza una
_PRIORITY = ["claude", "openai", "gemini"]


def configured_provider() -> str | None:
    """¿Qué proveedor de IA externa está configurado (si hay alguno)?

    MVDG_AI_PROVIDER fuerza uno en particular (si tiene su key cargada);
    si no, se usa el primero disponible en orden de prioridad. None si no
    hay ninguna key configurada — modo local (el de siempre)."""
    forced = os.environ.get("MVDG_AI_PROVIDER", "").strip().lower()
    if forced in _PROVIDERS and os.environ.get(_PROVIDERS[forced][0]):
        return forced
    for key in _PRIORITY:
        env_var, _, _, _ = _PROVIDERS[key]
        if os.environ.get(env_var):
            return key
    return None


def provider_label(provider: str) -> str:
    return _PROVIDERS.get(provider, (None, provider, None, None))[1]


def _model_for(provider: str) -> str:
    env_var, _, default, model_env = _PROVIDERS[provider]
    return os.environ.get(model_env, default)


_PROMPT_TMPL = {
    "es": (
        "Sos un consultor experto en gobierno de datos (DAMA-DMBOK). Una regla de "
        "calidad de datos no pasó. Dataset: {dataset}. Columna: {column}. Dimensión "
        "DAMA: {dimension}. Regla: {description}. Filas afectadas: {affected} de un "
        "total mayor. Respondé SOLO con un objeto JSON (sin texto extra, sin markdown) "
        "con estas 4 claves, en español, cada una 1-2 oraciones concretas y accionables: "
        '{{"root_cause": "causa probable del problema", "short_term": "qué hacer con las '
        'filas ya cargadas, corto plazo", "long_term": "cómo prevenirlo en el origen, '
        'largo plazo", "owner": "a qué rol/equipo asignárselo"}}'
    ),
    "en": (
        "You are an expert data governance consultant (DAMA-DMBOK). A data quality rule "
        "failed. Dataset: {dataset}. Column: {column}. DAMA dimension: {dimension}. Rule: "
        "{description}. Affected rows: {affected} out of a larger total. Reply ONLY with a "
        "JSON object (no extra text, no markdown) with these 4 keys, in English, each 1-2 "
        'concrete actionable sentences: {{"root_cause": "likely cause of the problem", '
        '"short_term": "what to do with the rows already loaded, short term", "long_term": '
        '"how to prevent it at the source, long term", "owner": "which role/team should own '
        'this"}}'
    ),
    "pt": (
        "Você é um consultor especialista em governança de dados (DAMA-DMBOK). Uma regra de "
        "qualidade de dados falhou. Dataset: {dataset}. Coluna: {column}. Dimensão DAMA: "
        "{dimension}. Regra: {description}. Linhas afetadas: {affected} de um total maior. "
        "Responda APENAS com um objeto JSON (sem texto extra, sem markdown) com estas 4 "
        "chaves, em português, cada uma com 1-2 frases concretas e acionáveis: "
        '{{"root_cause": "causa provável do problema", "short_term": "o que fazer com as '
        'linhas já carregadas, curto prazo", "long_term": "como prevenir na origem, longo '
        'prazo", "owner": "para qual papel/equipe atribuir isto"}}'
    ),
}


def _build_prompt(dataset: str, column: str, dimension: str, description: str,
                  affected_rows: int, lang: str) -> str:
    tmpl = _PROMPT_TMPL.get(lang, _PROMPT_TMPL["es"])
    return tmpl.format(dataset=dataset, column=column, dimension=dimension,
                       description=description, affected=affected_rows)


def _post_json(url: str, headers: dict, body: dict) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _extract_json_object(text: str) -> dict | None:
    """El modelo a veces envuelve el JSON en texto o markdown; nos quedamos
    con el primer objeto {...} que aparezca."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except (json.JSONDecodeError, ValueError):
        return None


def _call_claude(prompt: str, api_key: str, model: str) -> str:
    body = {"model": model, "max_tokens": 400,
            "messages": [{"role": "user", "content": prompt}]}
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01",
              "content-type": "application/json"}
    data = _post_json("https://api.anthropic.com/v1/messages", headers, body)
    return data["content"][0]["text"]


def _call_openai(prompt: str, api_key: str, model: str) -> str:
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400}
    headers = {"Authorization": f"Bearer {api_key}", "content-type": "application/json"}
    data = _post_json("https://api.openai.com/v1/chat/completions", headers, body)
    return data["choices"][0]["message"]["content"]


def _call_gemini(prompt: str, api_key: str, model: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"content-type": "application/json"}
    data = _post_json(url, headers, body)
    return data["candidates"][0]["content"]["parts"][0]["text"]


_CALLERS = {"claude": _call_claude, "openai": _call_openai, "gemini": _call_gemini}


def ai_suggest_fix(dataset: str, column: str, dimension: str, description: str,
                   affected_rows: int, lang: str = "es",
                   provider: str | None = None) -> dict | None:
    """Pide una sugerencia en vivo al proveedor de IA configurado. Devuelve
    None (nunca levanta excepción) si no hay proveedor configurado o si la
    llamada falla por cualquier motivo — el llamador cae a la sugerencia
    local sin que se note como un error."""
    provider = provider or configured_provider()
    if not provider or provider not in _CALLERS:
        return None
    env_var, _, _, _ = _PROVIDERS[provider]
    api_key = os.environ.get(env_var)
    if not api_key:
        return None
    prompt = _build_prompt(dataset, column, dimension, description, affected_rows, lang)
    model = _model_for(provider)
    try:
        text = _CALLERS[provider](prompt, api_key, model)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
            KeyError, IndexError, ValueError, OSError):
        return None
    parsed = _extract_json_object(text)
    if not parsed:
        return None
    if not all(k in parsed and parsed[k] for k in ("root_cause", "short_term", "long_term", "owner")):
        return None
    return {k: str(parsed[k]) for k in ("root_cause", "short_term", "long_term", "owner")}


# --------------------------------------------------------------- refactor DAX
# Misma regla que arriba: solo se manda METADATO del modelo (nombre de la
# medida, tabla y su expresión DAX) — nunca datos reales de las filas.
_DAX_KEYS = ("assessment", "issues", "refactored_dax", "explanation")

_DAX_PROMPT_TMPL = {
    "es": (
        "Sos un experto en modelado tabular y DAX de Power BI. Te paso una medida "
        "de un modelo semántico (solo metadato, sin datos). Tabla: {table}. Medida: "
        "{measure}. DAX actual:\n{dax}\n\nEvaluá anti-patrones (iteradores innecesarios, "
        "FILTER sobre tablas enteras, contexto mal manejado, columnas calculadas que "
        "deberían ser medidas, falta de variables). Respondé SOLO con un objeto JSON "
        "(sin texto extra, sin markdown) con estas 4 claves, en español: "
        '{{"assessment": "veredicto general en 1-2 oraciones", "issues": "anti-patrones '
        'o problemas concretos detectados", "refactored_dax": "el DAX mejorado (solo la '
        'expresión, sin explicación)", "explanation": "por qué la versión nueva es mejor, '
        '1-2 oraciones"}}'
    ),
    "en": (
        "You are an expert in Power BI tabular modeling and DAX. Here is a measure from "
        "a semantic model (metadata only, no data). Table: {table}. Measure: {measure}. "
        "Current DAX:\n{dax}\n\nAssess anti-patterns (unnecessary iterators, FILTER over "
        "whole tables, mishandled context, calculated columns that should be measures, "
        "missing variables). Reply ONLY with a JSON object (no extra text, no markdown) "
        'with these 4 keys, in English: {{"assessment": "overall verdict in 1-2 sentences", '
        '"issues": "concrete anti-patterns or problems found", "refactored_dax": "the '
        'improved DAX (expression only, no explanation)", "explanation": "why the new '
        'version is better, 1-2 sentences"}}'
    ),
    "pt": (
        "Você é um especialista em modelagem tabular e DAX do Power BI. Aqui está uma "
        "medida de um modelo semântico (apenas metadados, sem dados). Tabela: {table}. "
        "Medida: {measure}. DAX atual:\n{dax}\n\nAvalie anti-padrões (iteradores "
        "desnecessários, FILTER sobre tabelas inteiras, contexto mal tratado, colunas "
        "calculadas que deveriam ser medidas, falta de variáveis). Responda APENAS com um "
        "objeto JSON (sem texto extra, sem markdown) com estas 4 chaves, em português: "
        '{{"assessment": "veredicto geral em 1-2 frases", "issues": "anti-padrões ou '
        'problemas concretos encontrados", "refactored_dax": "o DAX melhorado (apenas a '
        'expressão, sem explicação)", "explanation": "por que a nova versão é melhor, '
        '1-2 frases"}}'
    ),
}


def _build_dax_prompt(measure: str, dax: str, table: str, lang: str) -> str:
    tmpl = _DAX_PROMPT_TMPL.get(lang, _DAX_PROMPT_TMPL["es"])
    return tmpl.format(measure=measure, dax=dax, table=table or "—")


def ai_refactor_dax(measure: str, dax: str, table: str = "",
                    lang: str = "es", provider: str | None = None) -> dict | None:
    """Pide al proveedor de IA configurado una evaluación + refactor del DAX de
    una medida. Devuelve un dict con las claves de ``_DAX_KEYS`` o None (sin
    proveedor configurado, DAX vacío o fallo de la llamada) — nunca levanta."""
    if not dax or not dax.strip():
        return None
    provider = provider or configured_provider()
    if not provider or provider not in _CALLERS:
        return None
    env_var, _, _, _ = _PROVIDERS[provider]
    api_key = os.environ.get(env_var)
    if not api_key:
        return None
    prompt = _build_dax_prompt(measure, dax, table, lang)
    model = _model_for(provider)
    try:
        text = _CALLERS[provider](prompt, api_key, model)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
            KeyError, IndexError, ValueError, OSError):
        return None
    parsed = _extract_json_object(text)
    if not parsed:
        return None
    if not all(k in parsed and parsed[k] for k in _DAX_KEYS):
        return None
    return {k: str(parsed[k]) for k in _DAX_KEYS}


# ------------------------------------------------- refactor cálculo de Tableau
# Mismo patrón que el refactor de DAX: solo se manda METADATO del campo
# (nombre, datasource y su fórmula) — nunca datos reales de las filas.
_CALC_KEYS = ("assessment", "issues", "refactored_formula", "explanation")

_CALC_PROMPT_TMPL = {
    "es": (
        "Sos un experto en Tableau y su lenguaje de cálculo. Te paso un campo "
        "calculado de un datasource publicado (solo metadato, sin datos). "
        "Datasource: {datasource}. Campo: {field}. Fórmula actual:\n{formula}\n\n"
        "Evaluá anti-patrones (LOD innecesario, cálculos anidados que podrían "
        "simplificarse, funciones de tabla costosas, casteos redundantes). "
        "Respondé SOLO con un objeto JSON (sin texto extra, sin markdown) con "
        "estas 4 claves, en español: "
        '{{"assessment": "veredicto general en 1-2 oraciones", "issues": "anti-patrones '
        'o problemas concretos detectados", "refactored_formula": "la fórmula mejorada '
        '(solo la expresión, sin explicación)", "explanation": "por qué la versión nueva '
        'es mejor, 1-2 oraciones"}}'
    ),
    "en": (
        "You are an expert in Tableau and its calculation language. Here is a "
        "calculated field from a published datasource (metadata only, no data). "
        "Datasource: {datasource}. Field: {field}. Current formula:\n{formula}\n\n"
        "Assess anti-patterns (unnecessary LOD, nested calculations that could be "
        "simplified, costly table functions, redundant casts). Reply ONLY with a "
        "JSON object (no extra text, no markdown) with these 4 keys, in English: "
        '{{"assessment": "overall verdict in 1-2 sentences", "issues": "concrete '
        'anti-patterns or problems found", "refactored_formula": "the improved formula '
        '(expression only, no explanation)", "explanation": "why the new version is '
        'better, 1-2 sentences"}}'
    ),
    "pt": (
        "Você é um especialista em Tableau e sua linguagem de cálculo. Aqui está um "
        "campo calculado de um datasource publicado (apenas metadados, sem dados). "
        "Datasource: {datasource}. Campo: {field}. Fórmula atual:\n{formula}\n\n"
        "Avalie anti-padrões (LOD desnecessário, cálculos aninhados que poderiam ser "
        "simplificados, funções de tabela custosas, conversões redundantes). Responda "
        "APENAS com um objeto JSON (sem texto extra, sem markdown) com estas 4 chaves, "
        'em português: {{"assessment": "veredicto geral em 1-2 frases", "issues": '
        '"anti-padrões ou problemas concretos encontrados", "refactored_formula": "a '
        'fórmula melhorada (apenas a expressão, sem explicação)", "explanation": "por '
        'que a nova versão é melhor, 1-2 frases"}}'
    ),
}


def _build_calc_prompt(field: str, formula: str, datasource: str, lang: str) -> str:
    tmpl = _CALC_PROMPT_TMPL.get(lang, _CALC_PROMPT_TMPL["es"])
    return tmpl.format(field=field, formula=formula, datasource=datasource or "—")


def ai_refactor_calc(field: str, formula: str, datasource: str = "",
                     lang: str = "es", provider: str | None = None) -> dict | None:
    """Pide al proveedor de IA configurado una evaluación + refactor de un
    campo calculado de Tableau. Devuelve un dict con las claves de
    ``_CALC_KEYS`` o None (sin proveedor configurado, fórmula vacía o fallo
    de la llamada) — nunca levanta."""
    if not formula or not formula.strip():
        return None
    provider = provider or configured_provider()
    if not provider or provider not in _CALLERS:
        return None
    env_var, _, _, _ = _PROVIDERS[provider]
    api_key = os.environ.get(env_var)
    if not api_key:
        return None
    prompt = _build_calc_prompt(field, formula, datasource, lang)
    model = _model_for(provider)
    try:
        text = _CALLERS[provider](prompt, api_key, model)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
            KeyError, IndexError, ValueError, OSError):
        return None
    parsed = _extract_json_object(text)
    if not parsed:
        return None
    if not all(k in parsed and parsed[k] for k in _CALC_KEYS):
        return None
    return {k: str(parsed[k]) for k in _CALC_KEYS}
