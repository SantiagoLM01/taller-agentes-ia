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
# bucle y colgaría la petición. `taller_core` carga FAISS/faiss al importarse.
import taller_core

mcp = FastMCP("taller-rag")


@mcp.tool()
def buscar_documentos(pregunta: str) -> str:
    """Busca en la base de conocimiento del taller (RAG) y devuelve los
    fragmentos de texto más relevantes para responder la pregunta."""
    docs = taller_core.obtener_retriever().invoke(pregunta)
    if not docs:
        return "No se encontraron fragmentos relevantes."
    return "\n\n---\n\n".join(d.page_content for d in docs)


if __name__ == "__main__":
    mcp.run(transport="stdio")
