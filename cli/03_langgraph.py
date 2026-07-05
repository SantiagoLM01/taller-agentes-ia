"""
03_langgraph.py — CLI del Paso 03: flujo con LangGraph.

LangGraph orquesta al agente como un grafo: nodos = pasos, aristas = transiciones.
Este grafo clasifica la pregunta (técnica o general) y la enruta al nodo adecuado.

Uso:
    python cli/03_langgraph.py                 # modo interactivo
    python cli/03_langgraph.py "tu pregunta"   # una sola pregunta y termina
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
        f"Clasifica en una sola palabra ('tecnica' o 'general') esta pregunta: {estado['pregunta']}"
    ).content.strip().lower()
    return {"categoria": "tecnica" if "tecn" in cat else "general"}


def responder_tecnico(estado: Estado):
    return {"respuesta": llm.invoke(f"Responde de forma técnica y precisa: {estado['pregunta']}").content}


def responder_general(estado: Estado):
    return {"respuesta": llm.invoke(f"Responde de forma simple, para principiantes: {estado['pregunta']}").content}


def ruta(estado: Estado):
    return estado["categoria"]


def construir_grafo():
    g = StateGraph(Estado)
    g.add_node("clasificar", clasificar)
    g.add_node("responder_tecnico", responder_tecnico)
    g.add_node("responder_general", responder_general)
    g.add_edge(START, "clasificar")
    g.add_conditional_edges("clasificar", ruta, {
        "tecnica": "responder_tecnico",
        "general": "responder_general",
    })
    g.add_edge("responder_tecnico", END)
    g.add_edge("responder_general", END)
    return g.compile()


def preguntar(app, texto: str):
    salida = app.invoke({"pregunta": texto, "categoria": "", "respuesta": ""})
    return salida["categoria"], salida["respuesta"]


def main():
    app = construir_grafo()

    if len(sys.argv) > 1:
        cat, resp = preguntar(app, " ".join(sys.argv[1:]))
        print(f"[categoría: {cat}]\n{resp}")
        return

    print("Grafo listo. Escribe tu pregunta ('salir' para terminar).\n")
    while True:
        try:
            pregunta = input("Tú> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n¡Hasta luego!")
            break
        if pregunta.lower() in {"salir", "exit", "quit", ""}:
            print("¡Hasta luego!")
            break
        cat, resp = preguntar(app, pregunta)
        print(f"[categoría: {cat}]\nAgente> {resp}\n")


if __name__ == "__main__":
    main()
