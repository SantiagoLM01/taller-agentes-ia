"""
preparar.py — Genera por adelantado las dos cachés del taller:

  1. El índice vectorial FAISS (para RAG), el mismo que usa el agente
     (mcp_server/rag_server.py) y el visor (cli/visor.py).
  2. El grafo de conocimiento (para GraphRAG), el mismo que usa el visor.

Así, durante el taller EN VIVO, tanto el agente (`cli/04_rag.py`) como el
visor (`cli/visor.py`) cargan todo al instante desde disco, sin esperar a
construir el índice ni a llamar al modelo.

Uso:
    python cli/preparar.py            # crea lo que falte (no toca lo ya cacheado)
    python cli/preparar.py --force    # borra las cachés y las regenera desde cero

Ambas cachés viven en mcp_server/_faiss_cache/ (ignorada por git).
"""
import json
import os
import shutil
import sys
import warnings
from typing import List

warnings.filterwarnings("ignore", category=DeprecationWarning)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from pydantic import BaseModel, Field

from config import get_chat_model, get_embeddings

# Rutas compartidas con el agente y el visor -------------------------------
_CACHE_DIR = os.path.join(REPO, "mcp_server", "_faiss_cache")
_GRAPH_CACHE = os.path.join(_CACHE_DIR, "grafo.json")
_DATA = os.path.join(REPO, "data", "historia_zelanor.md")


class Relacion(BaseModel):
    origen: str = Field(description="Entidad de origen")
    relacion: str = Field(description="Relación entre las entidades")
    destino: str = Field(description="Entidad de destino")


class Grafo(BaseModel):
    relaciones: List[Relacion]


def _leer_texto() -> str:
    return open(_DATA, encoding="utf-8").read()


def preparar_faiss(force: bool = False) -> None:
    """Construye el índice FAISS (misma receta que rag_server.py)."""
    from langchain_community.vectorstores import FAISS
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    if os.path.isdir(_CACHE_DIR) and os.path.isfile(os.path.join(_CACHE_DIR, "index.faiss")):
        print("[FAISS] ya existe en cache -> nada que hacer.")
        return

    print("[FAISS] construyendo indice vectorial...")
    docs = RecursiveCharacterTextSplitter(
        chunk_size=400, chunk_overlap=50
    ).create_documents([_leer_texto()])
    vs = FAISS.from_documents(docs, get_embeddings())
    vs.save_local(_CACHE_DIR)
    print(f"[FAISS] listo: {len(docs)} fragmentos guardados en {_CACHE_DIR}")


def preparar_grafo(force: bool = False) -> None:
    """Extrae el grafo de conocimiento con el LLM (misma receta que visor.py)."""
    if os.path.isfile(_GRAPH_CACHE):
        print("[Grafo] ya existe en cache (grafo.json) -> nada que hacer.")
        return

    print("[Grafo] extrayendo relaciones con el LLM...")
    llm = get_chat_model(max_tokens=4096)
    res = llm.with_structured_output(Grafo).invoke(
        "Extrae las relaciones clave entre entidades (personajes, lugares, "
        "organizaciones y objetos) de la siguiente historia. Sé conciso, "
        f"máximo 12 relaciones.\n\n{_leer_texto()}"
    )
    rels = [r.model_dump() for r in res.relaciones]
    os.makedirs(_CACHE_DIR, exist_ok=True)
    with open(_GRAPH_CACHE, "w", encoding="utf-8") as fh:
        json.dump(rels, fh, ensure_ascii=False, indent=2)
    print(f"[Grafo] listo: {len(rels)} relaciones guardadas en {_GRAPH_CACHE}")


def main() -> None:
    force = "--force" in sys.argv
    if force and os.path.isdir(_CACHE_DIR):
        print("[--force] borrando cache existente...")
        shutil.rmtree(_CACHE_DIR)

    print("Preparando cachés del taller (vector store + grafo)...\n")
    preparar_faiss(force)
    preparar_grafo(force)
    print("\n¡Todo listo! El agente (cli/04_rag.py) y el visor (cli/visor.py) "
          "cargarán al instante desde disco.")


if __name__ == "__main__":
    main()
