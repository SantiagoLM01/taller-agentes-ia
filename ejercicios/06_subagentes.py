"""
Ejercicio 06 — Subagentes con LangChain (un agente coordinador que delega).

En vez de un solo agente que lo hace todo, un agente COORDINADOR delega en
subagentes especialistas. Cada subagente se expone al coordinador como si fuera
una herramienta (tool):

    coordinador
      ├── historiador  (busca en la historia de Miravalle · RAG)
      └── traductor    (traduce la respuesta al inglés)

Esto es un patrón muy usado: dividir un problema grande en especialistas
pequeños y enfocados. LLM = Large Language Model · RAG = Retrieval-Augmented
Generation (Generación Aumentada por Recuperación).

Completa lo marcado con  # EJERCICIO  y ejecuta:
    python ejercicios/06_subagentes.py "¿quién gobierna Miravalle? responde en inglés"
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from langchain.agents import create_agent
from langchain_core.tools import tool

from config import get_chat_model
from taller_core import obtener_retriever

modelo = get_chat_model()

# Cargamos el retriever de forma perezosa (solo cuando se use por primera vez).
_retriever = None


def _get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = obtener_retriever()
    return _retriever


# ----- Subagente 1: HISTORIADOR (YA resuelto, para que veas el patrón) ------
@tool
def historiador(pregunta: str) -> str:
    """Especialista en la historia de Miravalle. Responde SOLO con datos de la historia."""
    docs = _get_retriever().invoke(pregunta)
    contexto = "\n\n".join(d.page_content for d in docs)
    sub = create_agent(
        modelo,
        tools=[],
        system_prompt="Eres un historiador de Miravalle. Responde solo con el contexto dado.",
    )
    r = sub.invoke({"messages": [{"role": "user",
        "content": f"Contexto:\n{contexto}\n\nPregunta: {pregunta}"}]})
    return r["messages"][-1].content


# ===== EJERCICIO 1: crea el subagente TRADUCTOR ============================
@tool
def traductor(texto: str) -> str:
    """Traduce un texto al inglés. Recibe el texto y devuelve su traducción."""
    # EJERCICIO: crea un subagente con create_agent (sin tools) cuyo system_prompt
    # sea "Eres un traductor. Traduce al inglés el texto del usuario, sin explicar."
    # Luego invócalo con `texto` y devuelve  r["messages"][-1].content
    # Pista: mira cómo lo hace 'historiador' arriba.
    raise NotImplementedError("Completa el subagente traductor")


# ----- Agente COORDINADOR: delega en los subagentes (como si fueran tools) --
SUBAGENTES = [historiador]  # EJERCICIO 2: agrega aquí el subagente 'traductor'


def main():
    coordinador = create_agent(
        modelo,
        tools=SUBAGENTES,
        system_prompt=(
            "Eres un coordinador. Para preguntas sobre Miravalle usa 'historiador'. "
            "Si piden la respuesta en inglés, pásala por 'traductor'. "
            "Delega siempre en los subagentes; no respondas de memoria."
        ),
    )
    pregunta = " ".join(sys.argv[1:]) or "¿Quién gobierna Miravalle? Responde en inglés."
    r = coordinador.invoke({"messages": [{"role": "user", "content": pregunta}]})
    print(r["messages"][-1].content)


if __name__ == "__main__":
    main()
