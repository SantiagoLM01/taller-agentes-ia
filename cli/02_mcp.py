"""
02_mcp.py — CLI del Paso 02: Agente que usa herramientas vía MCP.

MCP = Model Context Protocol (Protocolo de Contexto de Modelo): estándar para
conectar el LLM con herramientas externas. Aquí el agente usa las tools
`calcular` y `clima` que expone `mcp_server/server.py`.

Abrimos UNA sesión MCP persistente: el servidor se lanza una sola vez y queda
vivo durante todo el chat (rápido en cada mensaje).

Uso:
    python cli/02_mcp.py                 # modo chat interactivo
    python cli/02_mcp.py "tu pregunta"   # una sola pregunta y termina
"""
import asyncio
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from config import get_chat_model

SYSTEM = "Eres un asistente que usa herramientas para calcular y consultar el clima."


async def preguntar(agente, texto: str) -> str:
    resultado = await agente.ainvoke({"messages": [{"role": "user", "content": texto}]})
    return resultado["messages"][-1].content


async def main():
    client = MultiServerMCPClient({
        "taller": {
            "command": sys.executable,
            "args": [os.path.join(REPO, "mcp_server", "server.py")],
            "transport": "stdio",
        }
    })

    # La sesión se mantiene abierta mientras dure el bloque `async with`.
    async with client.session("taller") as sesion:
        tools = await load_mcp_tools(sesion)
        print("Herramientas MCP disponibles:", [t.name for t in tools])
        agente = create_agent(get_chat_model(), tools=tools, system_prompt=SYSTEM)

        if len(sys.argv) > 1:
            print(await preguntar(agente, " ".join(sys.argv[1:])))
            return

        print("Agente MCP listo. Escribe tu mensaje ('salir' para terminar).\n")
        while True:
            try:
                pregunta = input("Tú> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n¡Hasta luego!")
                break
            if pregunta.lower() in {"salir", "exit", "quit", ""}:
                print("¡Hasta luego!")
                break
            print("Agente>", await preguntar(agente, pregunta), "\n")


if __name__ == "__main__":
    asyncio.run(main())
