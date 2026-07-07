"""
Ejercicio 02 (cliente) — Conecta el agente al servidor MCP del ejercicio.

Este archivo YA está completo: lanza ejercicios/02_servidor.py como subproceso,
carga sus herramientas y deja que el agente las use.

    python ejercicios/02_cliente.py "convierte 100 USD a EUR"
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


async def main():
    servidor = os.path.join(os.path.dirname(os.path.abspath(__file__)), "02_servidor.py")
    client = MultiServerMCPClient({
        "ejercicio": {
            "command": sys.executable,
            "args": [servidor],
            "transport": "stdio",
        }
    })
    async with client.session("ejercicio") as sesion:
        tools = await load_mcp_tools(sesion)
        print("Herramientas MCP disponibles:", [t.name for t in tools])
        agente = create_agent(
            get_chat_model(),
            tools=tools,
            system_prompt="Usa las herramientas disponibles para responder.",
        )
        pregunta = " ".join(sys.argv[1:]) or "convierte 100 USD a EUR"
        resultado = await agente.ainvoke({"messages": [{"role": "user", "content": pregunta}]})
        print(resultado["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
