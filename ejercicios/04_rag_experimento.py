"""
Ejercicio 04 — Experimenta con la recuperación de RAG.

RAG = Retrieval-Augmented Generation (Generación Aumentada por Recuperación).
Este script reutiliza el MISMO vector store FAISS del taller (taller_core) y te
muestra qué fragmentos recupera para tu pregunta.

    python ejercicios/04_rag_experimento.py "¿quién fundó Miravalle?"

EJERCICIOS:
  1) Cambia K (abajo) a 1, 3 y 5 y compara qué fragmentos aparecen.
  2) (Reto) Cambia CHUNK_SIZE / CHUNK_OVERLAP en taller_core.py y regenera el
     índice con:   python cli/preparar.py --force
     Luego vuelve a correr este script y observa la diferencia.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import taller_core

# ===== EJERCICIO 1: prueba distintos valores de K =====
K = 3  # EJERCICIO: cambia este número (1, 3, 5) y compara los resultados


def main():
    pregunta = " ".join(sys.argv[1:]) or "¿Quién fundó Miravalle?"
    retriever = taller_core.obtener_retriever(k=K)
    docs = retriever.invoke(pregunta)

    print(f"\nPregunta: {pregunta!r}")
    print(f"K = {K}  ->  {len(docs)} fragmentos recuperados\n")
    for i, d in enumerate(docs, 1):
        print(f"--- Fragmento {i} ---")
        print(d.page_content[:300].strip(), "\n")


if __name__ == "__main__":
    main()
