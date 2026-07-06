"""
05_graphrag.py — CLI del Paso 05: Mini GraphRAG.

GraphRAG = RAG + grafo de conocimiento. En vez de buscar solo por similitud,
extrae entidades y las relaciones entre ellas (tripletas origen-relación-destino).
Trabaja sobre la historia ficticia `data/historia_zelanor.md` (la ciudad de Miravalle).

Al arrancar construye el grafo una vez; luego consultas por una entidad y el LLM
explica sus relaciones usando SOLO el grafo.

Prueba entidades como: Miravalle, lumincita, Sombra-corsarios, Sorenia Valdés.

Uso:
    python cli/05_graphrag.py                # modo interactivo
    python cli/05_graphrag.py "Miravalle"    # una sola consulta y termina
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import taller_core
from config import get_chat_model

llm = get_chat_model(max_tokens=4096)


def contexto_grafo(G, entidad: str) -> str:
    lineas = []
    for o, d, data in G.edges(data=True):
        if entidad.lower() in o.lower() or entidad.lower() in d.lower():
            lineas.append(f"{o} --{data['rel']}--> {d}")
    return "\n".join(lineas) or "(sin relaciones para esa entidad)"


def consultar(G, entidad: str) -> str:
    ctx = contexto_grafo(G, entidad)
    if ctx.startswith("(sin"):
        return ctx
    resp = llm.invoke(
        f"Usando SOLO estas relaciones, explica con qué se relaciona '{entidad}' y cómo.\n\n{ctx}"
    ).content
    return f"Relaciones encontradas:\n{ctx}\n\n{resp}"


def main():
    print("Cargando el grafo de conocimiento... (unos segundos la primera vez)")
    G = taller_core.construir_grafo()
    print(f"Grafo listo: {G.number_of_nodes()} entidades, {G.number_of_edges()} relaciones.\n")

    if len(sys.argv) > 1:
        print(consultar(G, " ".join(sys.argv[1:])))
        return

    print("Escribe una entidad para consultar sus relaciones ('salir' para terminar).\n")
    while True:
        try:
            entidad = input("Entidad> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n¡Hasta luego!")
            break
        if entidad.lower() in {"salir", "exit", "quit", ""}:
            print("¡Hasta luego!")
            break
        print(consultar(G, entidad), "\n")


if __name__ == "__main__":
    main()
