"""
Ejercicio 05 — Experimenta con el grafo (GraphRAG).

GraphRAG = RAG potenciado con un grafo de conocimiento (entidades + relaciones).
Este script reutiliza el MISMO grafo del taller (taller_core) y lo imprime.

    python ejercicios/05_graphrag_experimento.py

EJERCICIOS:
  1) Completa la parte marcada para listar los vecinos de una entidad.
  2) (Reto) Cambia PROMPT_GRAFO en taller_core.py (p. ej. "máximo 20 relaciones")
     y regenera con:   python cli/preparar.py --force
     Vuelve a correr este script y observa cómo cambia el grafo.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import taller_core

ENTIDAD = "Miravalle"  # EJERCICIO: prueba con otras entidades del grafo


def main():
    G = taller_core.construir_grafo()
    print(f"\nGrafo: {G.number_of_nodes()} entidades · {G.number_of_edges()} relaciones\n")
    for o, d, data in G.edges(data=True):
        print(f"{o} --{data['rel']}--> {d}")

    # ===== EJERCICIO: lista los vecinos de ENTIDAD =====
    # Pista: busca el nodo cuyo nombre contenga ENTIDAD (en minúsculas) y usa
    #   G.successors(nombre)  (a dónde apunta)  y  G.predecessors(nombre)  (quién lo apunta).
    print(f"\n--- Vecinos de «{ENTIDAD}» ---")
    # EJERCICIO: reemplaza esta línea por tu código que imprima los vecinos.
    raise NotImplementedError("Completa la búsqueda de vecinos de la entidad")


if __name__ == "__main__":
    main()
