"""
Ejercicio 03 — Agrega un nodo/rama nueva en LangGraph.

LangGraph orquesta el flujo como un grafo: nodos = pasos, aristas = transiciones.
El grafo clasifica la pregunta en 'tecnica' o 'general'. Tu misión: agregar una
TERCERA categoría 'matematica' con su propio nodo.

    python ejercicios/03_agrega_nodo.py "¿cuánto es 15*(3+2)?"
"""
import os
import sys
from typing import TypedDict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from langgraph.graph import StateGraph, START, END

from config import get_chat_model

llm = get_chat_model()


class Estado(TypedDict):
    pregunta: str
    categoria: str
    respuesta: str


def clasificar(estado: Estado):
    cat = llm.invoke(
        "Clasifica en UNA palabra ('tecnica', 'general' o 'matematica') esta "
        f"pregunta: {estado['pregunta']}"
    ).content.strip().lower()
    if "mate" in cat:
        categoria = "matematica"
    elif "tecn" in cat:
        categoria = "tecnica"
    else:
        categoria = "general"
    return {"categoria": categoria}


def responder_tecnico(estado: Estado):
    return {"respuesta": llm.invoke(f"Responde de forma técnica y precisa: {estado['pregunta']}").content}


def responder_general(estado: Estado):
    return {"respuesta": llm.invoke(f"Responde de forma simple, para principiantes: {estado['pregunta']}").content}


# ===== EJERCICIO: crea el nodo que responde preguntas matemáticas ===========
def responder_matematica(estado: Estado):
    """Responde preguntas de matemáticas resolviendo paso a paso."""
    # EJERCICIO: pide al LLM resolver paso a paso y dar el resultado final.
    # Debe devolver un diccionario con la clave "respuesta", igual que los otros nodos.
    raise NotImplementedError("Completa el nodo responder_matematica")


def ruta(estado: Estado):
    return estado["categoria"]


def construir_grafo():
    g = StateGraph(Estado)
    g.add_node("clasificar", clasificar)
    g.add_node("responder_tecnico", responder_tecnico)
    g.add_node("responder_general", responder_general)
    # EJERCICIO: registra tu nodo nuevo -> g.add_node("responder_matematica", responder_matematica)

    g.add_edge(START, "clasificar")
    g.add_conditional_edges("clasificar", ruta, {
        "tecnica": "responder_tecnico",
        "general": "responder_general",
        # EJERCICIO: agrega la ruta  "matematica": "responder_matematica"
    })
    g.add_edge("responder_tecnico", END)
    g.add_edge("responder_general", END)
    # EJERCICIO: conecta tu nodo al final -> g.add_edge("responder_matematica", END)
    return g.compile()


def preguntar(app, texto: str):
    salida = app.invoke({"pregunta": texto, "categoria": "", "respuesta": ""})
    return salida["categoria"], salida["respuesta"]


def main():
    app = construir_grafo()
    pregunta = " ".join(sys.argv[1:]) or "¿Cuánto es 15*(3+2)?"
    cat, resp = preguntar(app, pregunta)
    print(f"[categoría: {cat}]\n{resp}")


if __name__ == "__main__":
    main()
