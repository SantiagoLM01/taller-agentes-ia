"""
taller_core.py — Núcleo compartido del taller (una sola fuente de verdad).

Centraliza las dos "recetas" que antes se repetían por varios archivos:

  1. RAG / vector store: trocear la historia, calcular embeddings y construir
     (o cargar) el índice FAISS.  -> obtener_vectorstore(), obtener_retriever()
  2. GraphRAG / grafo: extraer con el LLM las relaciones (tripletas) y armar
     el grafo de conocimiento.     -> obtener_relaciones(), construir_grafo()

Lo usan: mcp_server/rag_server.py, cli/preparar.py, cli/visor.py,
cli/05_graphrag.py y el notebook 05.

Ambas cachés viven en mcp_server/_faiss_cache/ (ignorada por git):
  - index.faiss / index.pkl  (índice vectorial FAISS)
  - grafo.json               (relaciones del grafo)

NOTA técnica (importante): las librerías pesadas (FAISS y la librería nativa
`faiss`) se importan AQUÍ, a nivel de módulo. Así, cuando rag_server.py importa
este módulo al arrancar (antes del bucle de eventos), la carga ocurre fuera del
handler asíncrono y NO bloquea el event loop. Los mensajes del cargador de
faiss se redirigen a stderr para no corromper el canal stdio de MCP (stdout).
"""
import contextlib
import json
import os
import sys
from typing import List

import networkx as nx
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field

# Forzamos la carga de la librería nativa de faiss al importar este módulo
# (no dentro de un handler async), redirigiendo su salida a stderr.
with contextlib.redirect_stdout(sys.stderr):
    import faiss  # noqa: F401

from config import get_chat_model, get_embeddings

# --- Rutas y parámetros compartidos ----------------------------------------
_REPO = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_REPO, "data", "historia_zelanor.md")
CACHE_DIR = os.path.join(_REPO, "mcp_server", "_faiss_cache")
GRAPH_CACHE = os.path.join(CACHE_DIR, "grafo.json")

CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
DEFAULT_K = 3

PROMPT_GRAFO = (
    "Extrae las relaciones clave entre entidades (personajes, lugares, "
    "organizaciones y objetos) de la siguiente historia. Sé conciso, "
    "máximo 12 relaciones.\n\n"
)


# ============================================================================
# RAG · vector store (FAISS)
# ============================================================================
def cargar_texto() -> str:
    """Lee la historia ficticia que sirve de base de conocimiento."""
    return open(DATA_PATH, encoding="utf-8").read()


def trocear(texto: str):
    """Divide el texto en fragmentos (chunks) para el RAG."""
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    ).create_documents([texto])


_VS = None  # memoización del vector store en el proceso


def obtener_vectorstore(force: bool = False):
    """Construye o carga el índice FAISS (una sola vez por proceso).

    Si ya existe en disco (CACHE_DIR) se carga; si no, se construye a partir
    de la historia y se guarda. Con force=True se reconstruye desde cero.
    """
    global _VS
    if _VS is not None and not force:
        return _VS

    emb = get_embeddings()
    existe = os.path.isfile(os.path.join(CACHE_DIR, "index.faiss"))
    if existe and not force:
        _VS = FAISS.load_local(CACHE_DIR, emb, allow_dangerous_deserialization=True)
    else:
        docs = trocear(cargar_texto())
        _VS = FAISS.from_documents(docs, emb)
        _VS.save_local(CACHE_DIR)
    return _VS


def obtener_retriever(k: int = DEFAULT_K):
    """Devuelve un retriever del índice FAISS (los k fragmentos más cercanos)."""
    return obtener_vectorstore().as_retriever(search_kwargs={"k": k})


# ============================================================================
# GraphRAG · grafo de conocimiento
# ============================================================================
class Relacion(BaseModel):
    origen: str = Field(description="Entidad de origen")
    relacion: str = Field(description="Relación entre las entidades")
    destino: str = Field(description="Entidad de destino")


class Grafo(BaseModel):
    relaciones: List[Relacion]


def obtener_relaciones(force: bool = False) -> List[dict]:
    """Extrae (con el LLM) o carga de caché las relaciones del grafo.

    Devuelve una lista de dicts {origen, relacion, destino}. La extracción se
    hace una sola vez y se cachea en grafo.json para que sea reproducible.
    """
    if os.path.isfile(GRAPH_CACHE) and not force:
        with open(GRAPH_CACHE, encoding="utf-8") as fh:
            return json.load(fh)

    llm = get_chat_model(max_tokens=4096)
    res = llm.with_structured_output(Grafo).invoke(PROMPT_GRAFO + cargar_texto())
    rels = [r.model_dump() for r in res.relaciones]
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(GRAPH_CACHE, "w", encoding="utf-8") as fh:
        json.dump(rels, fh, ensure_ascii=False, indent=2)
    return rels


def construir_grafo(relaciones: List[dict] = None) -> "nx.DiGraph":
    """Arma un grafo dirigido de NetworkX a partir de las relaciones."""
    if relaciones is None:
        relaciones = obtener_relaciones()
    G = nx.DiGraph()
    for r in relaciones:
        G.add_edge(r["origen"], r["destino"], rel=r["relacion"])
    return G
