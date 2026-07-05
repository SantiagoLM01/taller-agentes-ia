"""
01_agente.py — CLI del Paso 01: LLM + Agente con LangChain.

LLM = Large Language Model (Modelo de Lenguaje Grande).
Un agente = LLM + instrucciones + herramientas (tools).

Uso:
    python cli/01_agente.py                 # modo chat interactivo
    python cli/01_agente.py "tu pregunta"   # una sola pregunta y termina
"""
import os
import sys

# Permite importar config.py desde la raíz del repo.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from langchain.agents import create_agent
from langchain_core.tools import tool

from config import get_chat_model


@tool
def longitud_texto(texto: str) -> int:
    """Devuelve cuántos caracteres tiene un texto."""
    return len(texto)


def crear_agente():
    return create_agent(
        get_chat_model(),
        tools=[longitud_texto],
        system_prompt="Eres un asistente útil. Usa herramientas cuando ayuden.",
    )


def preguntar(agente, texto: str) -> str:
    resultado = agente.invoke({"messages": [{"role": "user", "content": texto}]})
    return resultado["messages"][-1].content


def main():
    agente = crear_agente()

    # Si pasan una pregunta como argumento: respuesta única.
    if len(sys.argv) > 1:
        pregunta = " ".join(sys.argv[1:])
        print(preguntar(agente, pregunta))
        return

    # Si no: modo chat interactivo.
    print("Agente listo. Escribe tu mensaje ('salir' para terminar).\n")
    while True:
        try:
            pregunta = input("Tú> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n¡Hasta luego!")
            break
        if pregunta.lower() in {"salir", "exit", "quit", ""}:
            print("¡Hasta luego!")
            break
        print("Agente>", preguntar(agente, pregunta), "\n")


if __name__ == "__main__":
    main()
