"""
rag_server.py — Servidor MCP (Model Context Protocol) con una herramienta de RAG.

Expone una sola herramienta:
  - buscar_documentos(pregunta): hace RAG (Retrieval-Augmented Generation /
    Generación Aumentada por Recuperación) sobre `data/historia_zelanor.md`.
    Trocea el documento, calcula embeddings, construye un índice FAISS y
    devuelve los fragmentos de texto más relevantes para la pregunta.

Está separado de `server.py` porque carga librerías más pesadas (FAISS,
langchain-community). El notebook 04 lo lanza como subproceso por "stdio".

Para probarlo a mano:
    python mcp_server/rag_server.py
"""
import os
import sys
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from mcp.server.fastmcp import FastMCP

# --- Rutas del proyecto (para importar config y leer data/) ---
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# Cargamos las credenciales desde la raíz del repo: el subproceso puede
# arrancar con otro directorio de trabajo (p. ej. notebooks/).
from dotenv import load_dotenv
load_dotenv(os.path.join(_REPO, ".env"))

# Importamos las librerías de RAG a nivel de módulo (al arrancar el servidor,
# ANTES de que empiece el bucle de eventos). Si se importaran por primera vez
# dentro del handler asíncrono de una herramienta, la carga bloquearía el
# bucle y colgaría la petición.
from config import get_embeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Forzamos aquí la carga de la librería nativa de FAISS por el mismo motivo.
# Redirigimos sus mensajes a stderr para no corromper el canal stdio (que
# transporta el protocolo MCP por stdout).
import contextlib
with contextlib.redirect_stdout(sys.stderr):
    import faiss  # noqa: F401

mcp = FastMCP("taller-rag")

_retriever = None


def _get_retriever():
    """Construye (o carga de caché) el índice vectorial una sola vez."""
    global _retriever
    if _retriever is None:
        emb = get_embeddings()
        cache_dir = os.path.join(_HERE, "_faiss_cache")
        if os.path.isdir(cache_dir):
            print("[rag_server] cargando indice desde cache...", file=sys.stderr, flush=True)
            vs = FAISS.load_local(cache_dir, emb, allow_dangerous_deserialization=True)
        else:
            print("[rag_server] construyendo indice RAG (primera vez)...", file=sys.stderr, flush=True)
            ruta = os.path.join(_REPO, "data", "historia_zelanor.md")
            texto = open(ruta, encoding="utf-8").read()
            chunks = RecursiveCharacterTextSplitter(
                chunk_size=400, chunk_overlap=50
            ).create_documents([texto])
            vs = FAISS.from_documents(chunks, emb)
            vs.save_local(cache_dir)
            print(f"[rag_server] indice listo ({len(chunks)} chunks) y guardado en cache",
                  file=sys.stderr, flush=True)
        _retriever = vs.as_retriever(search_kwargs={"k": 3})
    return _retriever


@mcp.tool()
def buscar_documentos(pregunta: str) -> str:
    """Busca en la base de conocimiento del taller (RAG) y devuelve los
    fragmentos de texto más relevantes para responder la pregunta."""
    docs = _get_retriever().invoke(pregunta)
    if not docs:
        return "No se encontraron fragmentos relevantes."
    return "\n\n---\n\n".join(d.page_content for d in docs)


if __name__ == "__main__":
    mcp.run(transport="stdio")
