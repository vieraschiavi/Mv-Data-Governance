# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Servidores MCP de BI listos para conectar.

Para qué
--------
Power BI, Fabric y Tableau publicaron servidores MCP oficiales. Conectarlos no
es difícil, pero sí es fácil equivocarse: cada uno tiene su transporte, su
versión mínima de Node, su forma de autenticar y su propio nombre de paquete.
Este módulo tiene esos datos en un solo lugar y genera el ``mcp.json`` exacto,
para que nadie tenga que tipear un paquete de memoria.

Por qué NO se conectan solos desde el programa
----------------------------------------------
Los dos servidores REMOTOS (Power BI/Fabric y Tableau Cloud) autentican con
OAuth interactivo — Entra ID y OAuth 2.1 respectivamente. Implementar ese
flujo significaría que el programa maneje credenciales de tu tenant, que es
justo lo que este producto evita por diseño (ver mvdg/connectors.py). El
camino oficial de los dos proveedores es configurarlos en el cliente MCP
(VS Code, Claude Desktop), y eso es lo que se genera acá.

Los LOCALES sí se pueden lanzar desde el programa por stdio con
``mvdg.mcp_client``, que ya existe.

Honestidad sobre lo verificado
------------------------------
Los datos de abajo salen de la documentación oficial de cada proveedor
(agosto 2026), no de memoria. Lo que NO está probado en vivo es la conexión
real contra un tenant de Power BI/Fabric o un sitio de Tableau: hace falta una
suscripción, credenciales y, en el caso de Power BI, que el administrador
habilite la opción a nivel tenant. Es la misma declaración explícita que ya
hacen los conectores de Purview y Collibra.
"""
from __future__ import annotations

import json

# Transportes posibles. "stdio" = el programa puede lanzarlo; "http" =
# Streamable HTTP con OAuth, se configura en el cliente MCP.
STDIO = "stdio"
HTTP = "http"

SERVIDORES: dict[str, dict] = {
    "powerbi_local": {
        "etiqueta": "Power BI · modelado (local)",
        "plataforma": "Power BI",
        "transporte": STDIO,
        "comando": "npx",
        "args": ["-y", "@microsoft/powerbi-modeling-mcp@latest", "--start"],
        "requisitos": "Node.js 20+ y un modelo semántico abierto en Power BI "
                      "Desktop, un workspace de Fabric o archivos PBIP.",
        "auth": "Microsoft Entra ID o service principal.",
        "para_que": "Crear y modificar tablas, columnas, medidas y relaciones; "
                    "validar DAX. Escribe sobre el modelo.",
        "docs": "https://github.com/microsoft/powerbi-modeling-mcp",
    },
    "powerbi_remoto": {
        "etiqueta": "Power BI / Fabric · consultas (remoto)",
        "plataforma": "Power BI",
        "transporte": HTTP,
        "url": "https://api.fabric.microsoft.com/v1/mcp/powerbi",
        "requisitos": "El administrador del tenant tiene que habilitar «Users "
                      "can use the Power BI Model Context Protocol server "
                      "endpoint (preview)», y hace falta permiso Build sobre "
                      "el modelo semántico.",
        "auth": "OAuth de Microsoft Entra ID, interactivo.",
        "para_que": "Consultar modelos semánticos: ejecutar DAX, leer el "
                    "esquema y la metadata de reportes. Solo lectura.",
        "docs": "https://learn.microsoft.com/power-bi/developer/mcp/"
                "remote-mcp-server-get-started",
    },
    "tableau_local": {
        "etiqueta": "Tableau · servidor local",
        "plataforma": "Tableau",
        "transporte": STDIO,
        "comando": "npx",
        "args": ["-y", "@tableau/mcp-server"],
        "requisitos": "Node.js 22.7.5 o superior, y credenciales de tu sitio "
                      "de Tableau en el entorno del servidor.",
        "auth": "Token de acceso personal (PAT) de Tableau.",
        "para_que": "Explorar orígenes publicados, consultar datos y leer "
                    "metadata del sitio.",
        "docs": "https://tableau.github.io/tableau-mcp/docs/getting-started",
    },
    "tableau_cloud": {
        "etiqueta": "Tableau Cloud · servicio administrado",
        "plataforma": "Tableau",
        "transporte": HTTP,
        "url": "https://mcp.tableau.com",
        "requisitos": "Una cuenta de Tableau Cloud. Cada usuario entra con su "
                      "propia identidad y se respetan sus permisos.",
        "auth": "OAuth 2.1, interactivo.",
        "para_que": "Lo mismo que el local, sin instalar ni mantener nada.",
        "docs": "https://tableau.github.io/tableau-mcp/",
    },
}


def por_plataforma(plataforma: str) -> dict[str, dict]:
    """Los servidores de una plataforma ("Power BI" / "Tableau")."""
    return {k: v for k, v in SERVIDORES.items()
            if v["plataforma"].lower() == plataforma.lower()}


def config_json(preset: str, nombre: str | None = None) -> str:
    """El bloque de ``mcp.json`` para pegar en VS Code o Claude Desktop.

    Se genera y no se escribe a mano en la interfaz para que no pueda quedar
    desincronizado del registro: si mañana cambia un nombre de paquete, cambia
    en un solo lugar y la interfaz muestra lo nuevo.
    """
    cfg = SERVIDORES.get(preset)
    if cfg is None:
        raise KeyError(f"servidor MCP desconocido: {preset}")
    nombre = nombre or preset.replace("_", "-")
    if cfg["transporte"] == HTTP:
        entrada = {"type": "http", "url": cfg["url"]}
    else:
        entrada = {"command": cfg["comando"], "args": list(cfg["args"])}
    return json.dumps({"servers": {nombre: entrada}}, indent=2,
                      ensure_ascii=False)


def lanzable_localmente(preset: str) -> bool:
    """¿El programa puede lanzarlo por su cuenta?

    Solo los de stdio. Los remotos necesitan un OAuth interactivo que este
    programa no hace a propósito — decirlo acá evita que la interfaz ofrezca
    un botón que siempre iba a fallar.
    """
    return SERVIDORES.get(preset, {}).get("transporte") == STDIO


def herramientas(preset: str, timeout: float = 60.0) -> list[dict]:
    """Lista las herramientas de un servidor local, lanzándolo por stdio.

    Levanta ValueError para los remotos en vez de intentar y fallar con un
    error de red incomprensible.
    """
    cfg = SERVIDORES.get(preset)
    if cfg is None:
        raise KeyError(f"servidor MCP desconocido: {preset}")
    if not lanzable_localmente(preset):
        raise ValueError(
            f"{cfg['etiqueta']} usa {cfg['auth']} y se configura en el cliente "
            f"MCP, no se lanza desde acá. Usá config_json('{preset}').")
    from .mcp_client import list_tools
    return list_tools(cfg["comando"], cfg["args"], timeout=timeout)
