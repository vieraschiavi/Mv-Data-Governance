"""
MV Data Governance · Cliente MCP genérico (stdio).

Permite conectar el programa a cualquier servidor MCP local por stdio para
listar sus herramientas y llamarlas — por ejemplo, el **Power BI Modeling MCP
Server** oficial de Microsoft (Public Preview), que se lanza con:

    npx -y @microsoft/powerbi-modeling-mcp@latest --start

Honestidad sobre lo verificado (2026-07-19):
  - Este cliente está probado end-to-end, con transporte stdio REAL, contra el
    servidor MCP propio del programa (``mvdg.mcp_server``) en los tests y el
    selfcheck.
  - NO fue probado contra los servidores oficiales de Microsoft en vivo (igual
    que los conectores Purview/Collibra: implementado contra la documentación
    oficial, disclosure explícito). El servidor local de Microsoft es
    tooling orientado a Windows y requiere Power BI Desktop / Node 20+.
  - El servidor REMOTO de Power BI (https://api.fabric.microsoft.com/v1/mcp/powerbi,
    Streamable HTTP + OAuth de Entra ID) NO se implementa acá a propósito:
    requiere registrar una app en Entra y un flujo OAuth interactivo del
    usuario; el programa no maneja credenciales por diseño. La UI documenta
    cómo conectarlo desde VS Code / Claude, que es el camino oficial.

Todo es opt-in: nada se conecta salvo que el usuario ejecute la acción.
"""
from __future__ import annotations

import asyncio
from typing import Sequence

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin el SDK
    MCP_AVAILABLE = False


def _require_sdk() -> None:
    if not MCP_AVAILABLE:
        raise ImportError(
            "El cliente MCP necesita el SDK oficial: pip install mcp "
            "(incluido en requirements.txt)")


async def _with_session(command: str, args: Sequence[str],
                        env: dict | None, fn):
    params = StdioServerParameters(command=command, args=list(args),
                                   env=env)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await fn(session)


def list_tools(command: str, args: Sequence[str] = (),
               env: dict | None = None, timeout: float = 60.0) -> list[dict]:
    """Lanza un servidor MCP por stdio y devuelve sus herramientas.

    Devuelve [{"name", "description"}] — suficiente para explorar qué ofrece
    un servidor (p. ej. las operaciones de modelado del Power BI Modeling MCP).
    """
    _require_sdk()

    async def _run():
        async def _fn(session):
            result = await session.list_tools()
            return [{"name": t.name, "description": (t.description or "")}
                    for t in result.tools]
        return await asyncio.wait_for(
            _with_session(command, args, env, _fn), timeout)

    return asyncio.run(_run())


def call_tool(command: str, args: Sequence[str], tool: str,
              arguments: dict | None = None, env: dict | None = None,
              timeout: float = 120.0) -> str:
    """Llama una herramienta de un servidor MCP por stdio y devuelve el texto.

    Concatena el contenido de texto de la respuesta (formato estándar MCP).
    """
    _require_sdk()

    async def _run():
        async def _fn(session):
            result = await session.call_tool(tool, arguments or {})
            parts = []
            for item in result.content:
                text = getattr(item, "text", None)
                if text:
                    parts.append(text)
            return "\n".join(parts)
        return await asyncio.wait_for(
            _with_session(command, args, env, _fn), timeout)

    return asyncio.run(_run())
