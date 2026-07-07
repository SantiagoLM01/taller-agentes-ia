"""
Ejercicio 01 — Agrega tu propia herramienta (tool) al agente.

LLM = Large Language Model (Modelo de Lenguaje Grande).
Una tool = una función de Python que el agente puede decidir usar.

Completa lo marcado con  # EJERCICIO  y ejecuta:
    python ejercicios/01_agrega_tool.py "¿cuántas palabras tiene 'hola que tal amigas'?"
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from langchain.agents import create_agent
from langchain_core.tools import tool

from config import get_chat_model


# ----- Herramienta de ejemplo (YA resuelta, para que veas el patrón) --------
@tool
def longitud_texto(texto: str) -> int:
    """Devuelve cuántos caracteres tiene un texto."""
    return len(texto)


# ===== EJERCICIO 1: completa esta herramienta ===============================
@tool
def contar_palabras(texto: str) -> int:
    """Devuelve cuántas PALABRAS tiene un texto."""
    # EJERCICIO: reemplaza la siguiente línea para contar palabras.
    # Pista: en Python, "hola que tal".split() -> ['hola', 'que', 'tal']
    raise NotImplementedError("Completa la herramienta contar_palabras")


# ===== EJERCICIO 2 (reto): crea una herramienta NUEVA desde cero ============
# EJERCICIO: define abajo una herramienta con @tool. Por ejemplo:
#   invertir_texto(texto) -> str   que devuelva el texto al revés.
# Recuerda: buen docstring (el agente lo lee para decidir) + type hints.
# Luego agrégala a la lista TOOLS de abajo.


TOOLS = [longitud_texto, contar_palabras]  # EJERCICIO: agrega aquí tu tool nueva


def main():
    agente = create_agent(
        get_chat_model(),
        tools=TOOLS,
        system_prompt="Eres un asistente útil. Usa herramientas cuando ayuden.",
    )
    pregunta = " ".join(sys.argv[1:]) or "¿Cuántas palabras tiene 'hola que tal amigas'?"
    resultado = agente.invoke({"messages": [{"role": "user", "content": pregunta}]})
    print(resultado["messages"][-1].content)


if __name__ == "__main__":
    main()
