"""
visor.py — Visor interactivo EN VIVO del vector store (RAG) y del grafo (GraphRAG).

Lanza una app local en el navegador con dos pestañas:
  1. Vector Store (RAG): escribe una consulta y ve, en tiempo real, los embeddings
     del MISMO índice FAISS que usa el agente (rag_server.py), proyectados en 3D;
     la búsqueda la hace el propio FAISS (index.search) y se resaltan tu consulta
     y los k fragmentos recuperados, con sus distancias L2 reales.
  2. Grafo (GraphRAG): el grafo de conocimiento de la historia; escribe una
     entidad y se resaltan sus relaciones, con una explicación del LLM.

Uso:
    python cli/visor.py
    # abre http://127.0.0.1:7860 en el navegador

Requiere: gradio, plotly, scikit-learn (ya en requirements.txt).
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)


import gradio as gr
import networkx as nx
import numpy as np
import plotly.graph_objects as go
from langchain.agents import create_agent
from langchain_core.tools import tool
from sklearn.decomposition import PCA

import taller_core
from config import get_chat_model, get_embeddings

# ----------------------------------------------------------------------------
# Carga de datos y modelos (una sola vez, al arrancar)
# ----------------------------------------------------------------------------
print("Cargando documento y modelos...", flush=True)
_TEXTO = taller_core.cargar_texto()
_emb = get_embeddings()

# Usamos EXACTAMENTE el mismo índice FAISS que el agente (rag_server.py): la
# receta y la caché viven en taller_core, así el visor y el agente comparten
# el mismo store.
print("Cargando indice FAISS (compartido con el agente)...", flush=True)
_VS = taller_core.obtener_vectorstore()

# Recuperamos los vectores YA GUARDADOS en el índice FAISS (no los recalculamos)
# y los textos en el mismo orden que el índice, para poder graficarlos.
_N = _VS.index.ntotal
_CHUNK_VECS = _VS.index.reconstruct_n(0, _N)  # (n_chunks, dim), tal cual en FAISS
_CHUNKS = [_VS.docstore.search(_VS.index_to_docstore_id[i]).page_content for i in range(_N)]
print(f"Indice FAISS listo: {_N} fragmentos.", flush=True)


def _preview(texto: str, n: int = 70) -> str:
    return " ".join(texto.split())[:n]


# ----------------------------------------------------------------------------
# Pestaña 1 · Vector Store (RAG) — búsqueda REAL sobre el índice FAISS
# ----------------------------------------------------------------------------
def ver_vector_store(consulta: str, k: int = 3):
    tiene_consulta = bool(consulta and consulta.strip())
    if tiene_consulta:
        # Embedding de la consulta y BÚSQUEDA REAL en FAISS (index.search):
        # devuelve las distancias L2 y los índices de los k más cercanos,
        # exactamente como cuando el agente llama a la herramienta de RAG.
        qvec = np.array(_emb.embed_query(consulta), dtype="float32").reshape(1, -1)
        dist_top, idx_top = _VS.index.search(qvec, k)
        top = idx_top[0]
        dist_top = dist_top[0]
        puntos = np.vstack([_CHUNK_VECS, qvec])
    else:
        top = np.array([], dtype=int)
        puntos = _CHUNK_VECS

    # Proyección a 3D con PCA (Análisis de Componentes Principales)
    coords = PCA(n_components=3).fit_transform(puntos)
    chunk_xyz = coords[:len(_CHUNKS)]

    colores = []
    for i in range(len(_CHUNKS)):
        colores.append("#EF4444" if i in top else "#64748B")  # rojo = recuperado

    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=chunk_xyz[:, 0], y=chunk_xyz[:, 1], z=chunk_xyz[:, 2],
        mode="markers+text",
        marker=dict(size=7, color=colores),
        text=[f"#{i}" for i in range(len(_CHUNKS))],
        textposition="top center",
        hovertext=[_preview(c, 120) for c in _CHUNKS],
        hoverinfo="text",
        name="fragmentos",
    ))
    if tiene_consulta:
        q_xyz = coords[-1]
        fig.add_trace(go.Scatter3d(
            x=[q_xyz[0]], y=[q_xyz[1]], z=[q_xyz[2]],
            mode="markers+text",
            marker=dict(size=11, color="#22C55E", symbol="diamond"),
            text=["CONSULTA"], textposition="bottom center",
            hovertext=[consulta], hoverinfo="text",
            name="consulta",
        ))
    fig.update_layout(
        title="Embeddings del índice FAISS (proyección 3D) · rojo = recuperados",
        margin=dict(l=0, r=0, t=40, b=0), height=560, showlegend=True,
    )

    if tiene_consulta:
        md = "### Fragmentos recuperados por FAISS (top-%d)\n" % k
        md += "\n_Distancia L2 (euclidiana): **menor = más cercano**, la métrica que usa FAISS._\n"
        for rank, (i, dist) in enumerate(zip(top, dist_top), 1):
            md += f"\n**{rank}. #{i}** · distancia L2 `{dist:.3f}`\n\n> {_preview(_CHUNKS[i], 200)}…\n"
    else:
        md = "Escribe una consulta arriba para buscar en el índice FAISS y resaltar los fragmentos recuperados."
    return fig, md


# ----------------------------------------------------------------------------
# Pestaña 2 · Grafo de conocimiento (GraphRAG)
# ----------------------------------------------------------------------------
# El grafo (extracción con el LLM + caché en grafo.json) vive en taller_core,
# compartido con cli/05_graphrag.py y preparar.py. Aquí solo lo cargamos.
print("Cargando el grafo de conocimiento...", flush=True)
_llm = get_chat_model(max_tokens=4096)
_G = taller_core.construir_grafo()
_POS = nx.spring_layout(_G, seed=42, k=0.9)  # layout fijo para estabilidad visual


def _construir_figura_grafo(resaltados: set):
    edge_x, edge_y, edge_hi_x, edge_hi_y = [], [], [], []
    etiquetas_x, etiquetas_y, etiquetas = [], [], []
    for o, d, data in _G.edges(data=True):
        x0, y0 = _POS[o]; x1, y1 = _POS[d]
        destino = (edge_hi_x, edge_hi_y) if (o in resaltados and d in resaltados) else (edge_x, edge_y)
        destino[0].extend([x0, x1, None]); destino[1].extend([y0, y1, None])
        etiquetas_x.append((x0 + x1) / 2); etiquetas_y.append((y0 + y1) / 2)
        etiquetas.append(data["rel"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines",
                             line=dict(width=1, color="#CBD5E1"), hoverinfo="none", name="relaciones"))
    if edge_hi_x:
        fig.add_trace(go.Scatter(x=edge_hi_x, y=edge_hi_y, mode="lines",
                                 line=dict(width=3, color="#EF4444"), hoverinfo="none", name="resaltado"))
    fig.add_trace(go.Scatter(x=etiquetas_x, y=etiquetas_y, mode="text",
                             text=etiquetas, textfont=dict(size=9, color="#64748B"), hoverinfo="none",
                             showlegend=False))

    nodos = list(_G.nodes())
    fig.add_trace(go.Scatter(
        x=[_POS[n][0] for n in nodos], y=[_POS[n][1] for n in nodos],
        mode="markers+text", text=nodos, textposition="top center",
        marker=dict(size=[22 if n in resaltados else 14 for n in nodos],
                    color=["#EF4444" if n in resaltados else "#8B5CF6" for n in nodos]),
        hovertext=nodos, hoverinfo="text", name="entidades",
    ))
    fig.update_layout(title="Grafo de conocimiento (arrastra, haz zoom) · rojo = entidad y sus relaciones",
                      margin=dict(l=0, r=0, t=40, b=0), height=560,
                      xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
    return fig


def _entidades_que_coinciden(texto: str) -> set:
    """Nodos del grafo cuyo nombre aparece mencionado en el texto (y su vecindario)."""
    activa = texto.strip().lower() if texto else ""
    resaltados = set()
    if activa:
        for n in _G.nodes():
            if n.lower() in activa or activa in n.lower():
                resaltados.add(n)
                resaltados.update(_G.successors(n))
                resaltados.update(_G.predecessors(n))
    return resaltados


def ver_grafo(entidad: str):
    resaltados = _entidades_que_coinciden(entidad)
    fig = _construir_figura_grafo(resaltados)

    if entidad and entidad.strip() and resaltados:
        contexto = "\n".join(f"{o} --{data['rel']}--> {d}" for o, d, data in _G.edges(data=True)
                             if o in resaltados and d in resaltados)
        explicacion = _llm.invoke(
            f"Usando SOLO estas relaciones, explica brevemente con qué se relaciona "
            f"'{entidad}' y cómo.\n\n{contexto}"
        ).content
        md = f"### Relaciones de «{entidad}»\n```\n{contexto}\n```\n{explicacion}"
    else:
        md = "Escribe una entidad (p. ej. *Miravalle*, *lumincita*, *Sombra-corsarios*) para resaltar sus relaciones."
    return fig, md


# ----------------------------------------------------------------------------
# Pestaña 3 · Agente RAG en vivo (pregunta → recuperación → respuesta)
# ----------------------------------------------------------------------------
# Un agente real (LLM + tool) que, para responder, llama a `buscar_documentos`.
# La tool usa el MISMO retriever FAISS de taller_core (el mismo que expone el
# servidor MCP) y, de paso, guarda qué se recuperó para poder resaltarlo.
_ULTIMA_RECUPERACION = {"pregunta": "", "docs": []}


@tool
def buscar_documentos(pregunta: str) -> str:
    """Busca en la base de conocimiento del taller (RAG) y devuelve los
    fragmentos de texto más relevantes para responder la pregunta."""
    docs = taller_core.obtener_retriever().invoke(pregunta)
    _ULTIMA_RECUPERACION["pregunta"] = pregunta
    _ULTIMA_RECUPERACION["docs"] = docs
    if not docs:
        return "No se encontraron fragmentos relevantes."
    return "\n\n---\n\n".join(d.page_content for d in docs)


_AGENTE = create_agent(
    get_chat_model(),
    tools=[buscar_documentos],
    system_prompt=(
        "Eres una asistente experta. Antes de responder SIEMPRE usa la herramienta "
        "'buscar_documentos' para recuperar contexto. Responde usando SOLO esa "
        "información; si no está en el contexto, di que no lo sabes."
    ),
)


# --- Modo GraphRAG: agente independiente con SU PROPIA tool (grafo) -----------
# No mezclamos tools en un mismo agente: este agente recupera RELACIONES del
# grafo de conocimiento (GraphRAG), no fragmentos de texto (RAG).
_ULTIMA_GRAFO = {"pregunta": "", "entidades": set(), "relaciones": ""}


@tool
def buscar_en_grafo(pregunta: str) -> str:
    """Busca en el GRAFO DE CONOCIMIENTO (GraphRAG) las entidades mencionadas
    en la pregunta y devuelve sus relaciones estructuradas (entidad --relación--> entidad)."""
    resaltados = _entidades_que_coinciden(pregunta)
    relaciones = "\n".join(
        f"{o} --{data['rel']}--> {d}"
        for o, d, data in _G.edges(data=True)
        if o in resaltados and d in resaltados
    )
    _ULTIMA_GRAFO["pregunta"] = pregunta
    _ULTIMA_GRAFO["entidades"] = resaltados
    _ULTIMA_GRAFO["relaciones"] = relaciones
    if not relaciones:
        return "No se encontraron entidades ni relaciones relevantes en el grafo."
    return relaciones


_AGENTE_GRAFO = create_agent(
    get_chat_model(),
    tools=[buscar_en_grafo],
    system_prompt=(
        "Eres una asistente experta. Antes de responder SIEMPRE usa la herramienta "
        "'buscar_en_grafo' para recuperar las relaciones del grafo de conocimiento. "
        "Responde usando SOLO esas relaciones; si no están en el contexto, di que no lo sabes."
    ),
)


async def preguntar_al_agente(pregunta: str, modo: str = "RAG"):
    if not pregunta or not pregunta.strip():
        vacio = ver_vector_store("")[0] if modo == "RAG" else _construir_figura_grafo(set())
        return vacio, "Escribe una pregunta para el agente."

    if modo == "GraphRAG":
        _ULTIMA_GRAFO["entidades"] = set(); _ULTIMA_GRAFO["relaciones"] = ""
        resultado = await _AGENTE_GRAFO.ainvoke({"messages": [{"role": "user", "content": pregunta}]})
        respuesta = resultado["messages"][-1].content
        uso_tool = any(getattr(m, "tool_calls", None) for m in resultado["messages"])

        fig = _construir_figura_grafo(_ULTIMA_GRAFO["entidades"])
        rels = _ULTIMA_GRAFO["relaciones"]
        md = f"### 🧠 Respuesta del agente (GraphRAG)\n\n{respuesta}\n\n---\n"
        md += ("✅ El agente **llamó a `buscar_en_grafo`** (GraphRAG) antes de responder.\n"
               if uso_tool else
               "⚠️ El agente respondió **sin** usar la herramienta de grafo.\n")
        if rels:
            n_ent = len(_ULTIMA_GRAFO["entidades"])
            md += f"\n### 🕸️ Relaciones recuperadas del grafo ({n_ent} entidades)\n```\n{rels}\n```\n"
        return fig, md

    # Modo RAG (por defecto)
    _ULTIMA_RECUPERACION["docs"] = []
    resultado = await _AGENTE.ainvoke({"messages": [{"role": "user", "content": pregunta}]})
    respuesta = resultado["messages"][-1].content

    # ¿El agente llamó a la tool de recuperación?
    uso_tool = any(
        getattr(m, "tool_calls", None) for m in resultado["messages"]
    )

    # Reconstruimos el gráfico resaltando lo que FAISS recuperó para la pregunta.
    fig, _ = ver_vector_store(pregunta)

    docs = _ULTIMA_RECUPERACION["docs"]
    md = f"### 🧠 Respuesta del agente (RAG)\n\n{respuesta}\n\n---\n"
    md += ("✅ El agente **llamó a `buscar_documentos`** (RAG) antes de responder.\n"
           if uso_tool else
           "⚠️ El agente respondió **sin** usar la herramienta de recuperación.\n")
    if docs:
        md += f"\n### 📚 Fragmentos recuperados por FAISS ({len(docs)})\n"
        for rank, d in enumerate(docs, 1):
            md += f"\n**{rank}.** > {_preview(d.page_content, 200)}…\n"
    return fig, md


# ----------------------------------------------------------------------------
# Interfaz Gradio
# ----------------------------------------------------------------------------
def construir_app():
    with gr.Blocks(title="Visor RAG / GraphRAG") as app:
        gr.Markdown("# 🔎 Visor en vivo · Agente RAG, Vector Store y Grafo (GraphRAG)\n"
                    "Base de conocimiento: la historia ficticia de **Miravalle**.")
        with gr.Tab("Agente RAG en vivo"):
            gr.Markdown("Pregúntale al **agente** y elige el enfoque de recuperación:\n"
                        "- **RAG:** recupera *fragmentos de texto* con FAISS (se resaltan en el espacio de embeddings).\n"
                        "- **GraphRAG:** recupera *relaciones* del grafo de conocimiento (se resaltan en el grafo).\n\n"
                        "_Cada modo es un agente independiente con una sola herramienta; no se mezclan._")
            modo = gr.Radio(["RAG", "GraphRAG"], value="RAG", label="Enfoque de recuperación")
            qa = gr.Textbox(label="Pregunta al agente",
                            placeholder="p. ej. ¿Quién fundó Miravalle y en qué año?")
            with gr.Row():
                plot_a = gr.Plot(label="Recuperación")
                info_a = gr.Markdown()
            qa.submit(preguntar_al_agente, inputs=[qa, modo], outputs=[plot_a, info_a])
            gr.Button("Preguntar").click(preguntar_al_agente, inputs=[qa, modo], outputs=[plot_a, info_a])
        with gr.Tab("Vector Store (RAG)"):
            q = gr.Textbox(label="Consulta", placeholder="p. ej. ¿Quién fundó Miravalle?")
            with gr.Row():
                plot_v = gr.Plot(label="Espacio de embeddings")
                info_v = gr.Markdown()
            q.submit(ver_vector_store, inputs=q, outputs=[plot_v, info_v])
            gr.Button("Ver").click(ver_vector_store, inputs=q, outputs=[plot_v, info_v])
            app.load(ver_vector_store, inputs=q, outputs=[plot_v, info_v])
        with gr.Tab("Grafo (GraphRAG)"):
            e = gr.Textbox(label="Entidad", placeholder="p. ej. Miravalle")
            with gr.Row():
                plot_g = gr.Plot(label="Grafo de conocimiento")
                info_g = gr.Markdown()
            e.submit(ver_grafo, inputs=e, outputs=[plot_g, info_g])
            gr.Button("Ver").click(ver_grafo, inputs=e, outputs=[plot_g, info_g])
            app.load(ver_grafo, inputs=e, outputs=[plot_g, info_g])
    return app


if __name__ == "__main__":
    construir_app().launch(server_name="127.0.0.1", server_port=7860, inbrowser=True)
