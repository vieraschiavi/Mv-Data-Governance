"""
MV Data Governance · Etiquetas de sensibilidad (MIP) — acelerador sobre la
API real de Microsoft, no una reimplementación local.

Honestidad de arquitectura (no negociable): Microsoft Information
Protection NO es solo una etiqueta de texto — es cifrado y Rights
Management embebidos en el propio archivo de Office/PDF, atado a la
infraestructura de Azure Information Protection / Rights Management
Services de Microsoft. **No hay forma de replicar eso localmente**: ni
este programa ni ningún otro fuera del ecosistema Microsoft puede "aplicar
una etiqueta MIP" sin llamar a la infraestructura real de Microsoft. Por
eso este módulo NO reimplementa nada — llama a la Microsoft Graph API real
(``assignSensitivityLabel``) para aplicar una etiqueta de verdad a un
archivo que ya vive en OneDrive/SharePoint, usando la clasificación que
este programa ya calculó (PII detectada, clasificación del catálogo).

Límite honesto de alcance: esto SOLO aplica a datasets cuyo archivo fuente
ya está en OneDrive/SharePoint (Word, Excel, PDF...) — una tabla de
PostgreSQL o un CSV que nunca pasó por Microsoft 365 no tiene "etiqueta
MIP" posible, porque la etiqueta vive en el formato del archivo, no en el
dato en abstracto. Para catálogos gobernados desde archivos que sí viven
ahí (muy común: Excel compartidos por el equipo), este conector cierra la
brecha real.

Apagado por defecto. Service principal propio del usuario (Azure AD, mismo
patrón que Power BI/Purview): ``MIP_TENANT_ID``, ``MIP_CLIENT_ID``,
``MIP_CLIENT_SECRET``. Permiso de aplicación necesario: ``Files.ReadWrite.All``
sobre Microsoft Graph, más habilitar las metered APIs de M365 (ver
docs/PURVIEW_COLLIBRA.md).

Implementado contra Microsoft Graph v1.0/beta (Microsoft Learn, verificado
2026-07-16): ``POST /drives/{id}/items/{id}/assignSensitivityLabel``,
``GET /security/informationProtection/sensitivityLabels`` (beta) y la
codificación de sharing URL -> shareId documentada para
``GET /shares/{id}/driveItem``. NO se probó contra un tenant M365 real (no
disponible en este entorno de desarrollo).
"""
from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request

import pandas as pd

_TIMEOUT = 30
_ENV = ("MIP_TENANT_ID", "MIP_CLIENT_ID", "MIP_CLIENT_SECRET")
_GRAPH_V1 = "https://graph.microsoft.com/v1.0"
_GRAPH_BETA = "https://graph.microsoft.com/beta"

# heurística: qué palabra en el nombre de la etiqueta corresponde a cada
# clasificación del catálogo — se resuelve contra las etiquetas REALES del
# tenant (list_labels), nunca se inventa un id.
_LABEL_NAME_HINTS = {
    "PII": ("confidencial", "confidential", "personal", "restricted", "restringido"),
    "Confidencial": ("confidencial", "confidential", "restricted", "restringido"),
    "Interna": ("interno", "internal"),
    "Pública": ("publico", "público", "public", "general"),
}


def configured() -> bool:
    return all(os.environ.get(v) for v in _ENV)


def _http_json(url: str, headers: dict, method: str = "GET", body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        raw = resp.read()
        return json.loads(raw.decode("utf-8")) if raw else {}


def _http_form(url: str, form: dict) -> dict:
    data = urllib.parse.urlencode(form).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_token() -> str:
    tenant = os.environ["MIP_TENANT_ID"]
    url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    form = {"grant_type": "client_credentials", "client_id": os.environ["MIP_CLIENT_ID"],
            "client_secret": os.environ["MIP_CLIENT_SECRET"],
            "scope": "https://graph.microsoft.com/.default"}
    return _http_form(url, form)["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def encode_share_url(url: str) -> str:
    """Codifica una sharing URL de OneDrive/SharePoint al shareId que pide
    la Graph API (base64url sin padding, prefijo 'u!'), documentado por
    Microsoft Learn ("Access shared items")."""
    b64 = base64.b64encode(url.encode("utf-8")).decode("ascii")
    b64url = b64.rstrip("=").replace("/", "_").replace("+", "-")
    return f"u!{b64url}"


def resolve_share_url(url: str, token: str | None = None) -> dict:
    """Sharing URL -> {driveId, itemId} vía /shares/{shareId}/driveItem."""
    token = token or _get_token()
    share_id = encode_share_url(url)
    item = _http_json(f"{_GRAPH_V1}/shares/{share_id}/driveItem", _headers(token))
    return {"driveId": item.get("parentReference", {}).get("driveId"), "itemId": item.get("id"),
            "name": item.get("name")}


def list_labels(token: str | None = None) -> list[dict]:
    """Etiquetas de sensibilidad REALES configuradas en el tenant (nunca
    inventamos un id: siempre se resuelve contra esta lista)."""
    if token is None:
        if not configured():
            return []
        token = _get_token()
    data = _http_json(f"{_GRAPH_BETA}/security/informationProtection/sensitivityLabels",
                      _headers(token))
    return data.get("value", [])


def suggest_label(classification: str, labels: list[dict]) -> dict | None:
    """De las etiquetas reales del tenant, sugiere la que mejor matchea la
    clasificación del catálogo (por nombre) — nunca un id inventado."""
    hints = _LABEL_NAME_HINTS.get(classification, ())
    for label in labels:
        name = label.get("name", "").lower()
        if any(h in name for h in hints):
            return label
    return None


def build_assignment_plan(catalog: pd.DataFrame, file_map: dict[str, dict],
                          labels: list[dict]) -> list[dict]:
    """Arma qué etiqueta se aplicaría a cada dataset que SÍ tiene un
    archivo mapeado en OneDrive/SharePoint (``file_map``: {dataset:
    {"driveId":.., "itemId":..}}). Los datasets sin archivo mapeado no
    tienen etiqueta posible (no reimplementamos MIP local) y se listan
    aparte, explícitamente, para que quede claro por qué se saltean."""
    plan, skipped = [], []
    for _, row in catalog.iterrows():
        ds = row["dataset"]
        if ds not in file_map:
            skipped.append(ds)
            continue
        label = suggest_label(row.get("classification", ""), labels)
        plan.append({"dataset": ds, "driveId": file_map[ds]["driveId"],
                     "itemId": file_map[ds]["itemId"],
                     "classification": row.get("classification", ""),
                     "suggested_label": label["name"] if label else None,
                     "label_id": label["id"] if label else None})
    return {"plan": plan, "skipped_no_file": skipped}


def assign_label(drive_id: str, item_id: str, label_id: str, justification: str = "",
                 dry_run: bool = True, token: str | None = None) -> dict:
    body = {"sensitivityLabelId": label_id, "assignmentMethod": "standard",
           "justificationText": justification or "Asignado por MV Data Governance"}
    if dry_run:
        return {"dry_run": True, "url": f"{_GRAPH_V1}/drives/{drive_id}/items/{item_id}/assignSensitivityLabel",
               "body": body}
    if not configured():
        raise RuntimeError("MIP no configurado — faltan variables de entorno.")
    token = token or _get_token()
    url = f"{_GRAPH_V1}/drives/{drive_id}/items/{item_id}/assignSensitivityLabel"
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers=_headers(token))
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return {"dry_run": False, "status": resp.status, "location": resp.headers.get("Location")}


def push_labels(catalog: pd.DataFrame, file_map: dict[str, dict], dry_run: bool = True) -> dict:
    """Orquesta el plan completo: resuelve etiquetas reales del tenant,
    arma qué le tocaría a cada dataset con archivo mapeado, y (si
    dry_run=False) las aplica una por una vía la Graph API real."""
    token = _get_token() if (not dry_run and configured()) else None
    labels = list_labels(token) if (not dry_run) else []
    result = build_assignment_plan(catalog, file_map, labels)
    if dry_run:
        return {"dry_run": True, **result, "assigned": []}
    if not configured():
        raise RuntimeError("MIP no configurado — faltan variables de entorno.")
    assigned = []
    for item in result["plan"]:
        if not item["label_id"]:
            continue
        r = assign_label(item["driveId"], item["itemId"], item["label_id"],
                         dry_run=False, token=token)
        assigned.append({**item, "result": r})
    return {"dry_run": False, **result, "assigned": assigned}
