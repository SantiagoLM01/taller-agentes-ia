"""
04_rag.py — CLI del Paso 04: RAG agéntico (Agente + LLM + MCP + tool).

RAG = Retrieval-Augmented Generation (Generación Aumentada por Recuperación):
recupera contexto relevante antes de responder. Aquí el agente usa la tool MCP
`buscar_documentos` (servidor `mcp_server/rag_server.py`) para buscar en la
historia ficticia `data/historia_zelanor.md` y responde solo con ese contexto.

Prueba preguntas de la historia, p. ej.:
    "¿Quién fundó Miravalle y en qué año?"
    "¿Quién lidera los Sombra-corsarios?"
    "¿Qué es la lumincita y de dónde se extrae?"

Uso:
    python cli/04_rag.py                 # modo chat interactivo
    python cli/04_rag.py "tu pregunta"   # una sola pregunta y termina
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

SYSTEM = (
    "Eres una asistente experta. Antes de responder SIEMPRE usa la herramienta "
    "'buscar_documentos' para recuperar contexto. Responde usando SOLO esa "
    "información; si no está en el contexto, di que no lo sabes."
)


async def preguntar(agente, texto: str) -> str:
    resultado = await agente.ainvoke({"messages": [{"role": "user", "content": texto}]})
    return resultado["messages"][-1].content


async def main():
    client = MultiServerMCPClient({
        "rag": {
            "command": sys.executable,
            "args": [os.path.join(REPO, "mcp_server", "rag_server.py")],
            "transport": "stdio",
        }
    })

    async with client.session("rag") as sesion:
        tools = await load_mcp_tools(sesion)
        agente = create_agent(get_chat_model(), tools=tools, system_prompt=SYSTEM)

        if len(sys.argv) > 1:
            print(await preguntar(agente, " ".join(sys.argv[1:])))
            return

        print("Agente RAG listo (base de conocimiento: historia de Miravalle).")
        print("Escribe tu pregunta ('salir' para terminar).\n")
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
