"""
MV Data Governance · Chequeo de integridad de la instalación.

Problema real que resuelve: al actualizar el programa copiando archivos sueltos
(p. ej. reemplazar ``app/app.py`` pero no la carpeta ``mvdg/``, o al revés), la
app queda con piezas de versiones distintas y revienta con un traceback críptico
(``KeyError: 'findings'``, una pestaña que muestra ``tab_contracts`` en crudo,
etc.). Para un usuario que actualiza a mano, ese error no dice qué hacer.

Este módulo verifica que las piezas que ``app/app.py`` necesita estén presentes
y sean de la misma versión: unas claves i18n "canario" y unos atributos de los
módulos del motor. Si algo falta, la app muestra un cartel claro ("reemplazá
TODA la carpeta") en vez del traceback. En una copia consistente no salta nunca
—las canario existen— así que no enmascara bugs reales del código correcto.
"""
from __future__ import annotations

import importlib

# Claves i18n que las features recientes de app.py usan. Si el i18n.py instalado
# es más viejo que el app.py, faltan y las pestañas muestran la clave en crudo.
_CANARY_I18N: tuple[str, ...] = (
    "tab_contracts", "con_intro", "con_alerts_title",   # Contratos / Data Products
    "del_findings", "del_kpi_fails", "del_findings_note",  # Entregable con hallazgos
    "cu_bulk_title",                                     # validación masiva de curaduría
    "mcp_title", "mcp_expose_title",                     # MCP (servidor propio)
    "mcp_tab_title", "mcp_tab_verified",                 # MCP de Tableau
)

# (módulo, atributo) que app.py invoca; si el motor está viejo, no existen.
_CANARY_ATTRS: tuple[tuple[str, str], ...] = (
    ("mvdg.deliverable", "findings_df"),
    ("mvdg.deliverable", "build_deliverable"),
    ("mvdg.contracts", "contracts_df"),
    ("mvdg.contracts", "alerts_df"),
    ("mvdg.scope", "combined_results"),
)


def check_install() -> list[str]:
    """Devuelve la lista de piezas faltantes (vacía si la copia es consistente)."""
    missing: list[str] = []

    try:
        from .i18n import _T
    except Exception:  # pragma: no cover - i18n corrupto o ausente
        return ["mvdg/i18n.py (no se pudo cargar)"]

    for key in _CANARY_I18N:
        if key not in _T:
            missing.append(f"i18n: '{key}'")

    for mod_name, attr in _CANARY_ATTRS:
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            missing.append(f"{mod_name} (no se pudo importar)")
            continue
        if not hasattr(mod, attr):
            missing.append(f"{mod_name}.{attr}")

    return missing


# Mensaje del cartel, trilingüe (no depende de i18n: justamente puede estar viejo).
MESSAGE = {
    "es": ("⚠️ **Tu copia del programa está incompleta o desactualizada.**\n\n"
           "Actualizaste algunos archivos pero no todos, así que `app/app.py` "
           "y la carpeta `mvdg/` son de versiones distintas. **Reemplazá TODA "
           "la carpeta del programa con la versión nueva** (no copies archivos "
           "sueltos) y volvé a abrir la app.\n\nPiezas que no coinciden:"),
    "en": ("⚠️ **Your copy of the program is incomplete or out of date.**\n\n"
           "You updated some files but not all, so `app/app.py` and the "
           "`mvdg/` folder are from different versions. **Replace the WHOLE "
           "program folder with the new version** (don't copy individual "
           "files) and reopen the app.\n\nMismatched pieces:"),
    "pt": ("⚠️ **Sua cópia do programa está incompleta ou desatualizada.**\n\n"
           "Você atualizou alguns arquivos, mas não todos, então `app/app.py` "
           "e a pasta `mvdg/` são de versões diferentes. **Substitua a pasta "
           "INTEIRA do programa pela versão nova** (não copie arquivos "
           "avulsos) e reabra o app.\n\nPeças que não coincidem:"),
}
