"""
preparar.py — Genera por adelantado las dos cachés del taller:

  1. El índice vectorial FAISS (para RAG).
  2. El grafo de conocimiento (para GraphRAG).

Ambas usan las mismas recetas que el resto del proyecto, definidas en el módulo
compartido `taller_core.py`. Así, durante el taller EN VIVO, tanto el agente
(`cli/04_rag.py`) como el visor (`cli/visor.py`) cargan todo al instante desde
disco, sin esperar a construir el índice ni a llamar al modelo.

Uso:
    python cli/preparar.py            # crea lo que falte (no toca lo ya cacheado)
    python cli/preparar.py --force    # borra las cachés y las regenera desde cero

Ambas cachés viven en mcp_server/_faiss_cache/ (ignorada por git).
"""
import os
import shutil
import sys
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import taller_core


def main() -> None:
    force = "--force" in sys.argv
    if force and os.path.isdir(taller_core.CACHE_DIR):
        print("[--force] borrando cache existente...")
        shutil.rmtree(taller_core.CACHE_DIR)

    print("Preparando cachés del taller (vector store + grafo)...\n")

    print("[FAISS] preparando índice vectorial...")
    vs = taller_core.obtener_vectorstore(force=force)
    print(f"[FAISS] listo: {vs.index.ntotal} fragmentos en {taller_core.CACHE_DIR}")

    print("[Grafo] preparando grafo de conocimiento...")
    rels = taller_core.obtener_relaciones(force=force)
    print(f"[Grafo] listo: {len(rels)} relaciones en {taller_core.GRAPH_CACHE}")

    print("\n¡Todo listo! El agente (cli/04_rag.py) y el visor (cli/visor.py) "
          "cargarán al instante desde disco.")


if __name__ == "__main__":
    main()
