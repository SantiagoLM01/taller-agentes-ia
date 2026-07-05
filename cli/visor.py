"""
visor.py — Visor interactivo EN VIVO del vector store (RAG) y del grafo (GraphRAG).

Lanza una app local en el navegador con dos pestañas:
  1. Vector Store (RAG): escribe una consulta y ve, en tiempo real, los embeddings
     de los fragmentos proyectados en 3D; se resaltan tu consulta y los k más
     cercanos (los que el RAG recuperaría).
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

from typing import List

import gradio as gr
import networkx as nx
import numpy as np
import plotly.graph_objects as go
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from sklearn.decomposition import PCA

from config import get_chat_model, get_embeddings

# ----------------------------------------------------------------------------
# Carga de datos y modelos (una sola vez, al arrancar)
# ----------------------------------------------------------------------------
print("Cargando documento y modelos...", flush=True)
_TEXTO = open(os.path.join(REPO, "data", "historia_zelanor.md"), encoding="utf-8").read()
_CHUNKS = [d.page_content for d in
           RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50).create_documents([_TEXTO])]

_emb = get_embeddings()
print(f"Calculando embeddings de {len(_CHUNKS)} fragmentos...", flush=True)
_CHUNK_VECS = np.array(_emb.embed_documents(_CHUNKS))  # (n_chunks, dim)


def _preview(texto: str, n: int = 70) -> str:
    return " ".join(texto.split())[:n]


# ----------------------------------------------------------------------------
# Pestaña 1 · Vector Store (RAG)
# ----------------------------------------------------------------------------
def _cosine(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = a / (np.linalg.norm(a) + 1e-9)
    b = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-9)
    return b @ a


def ver_vector_store(consulta: str, k: int = 3):
    tiene_consulta = bool(consulta and consulta.strip())
    if tiene_consulta:
        qvec = np.array(_emb.embed_query(consulta))
        sims = _cosine(qvec, _CHUNK_VECS)
        top = np.argsort(-sims)[:k]
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
        title="Embeddings de los fragmentos (proyección 3D) · rojo = recuperados",
        margin=dict(l=0, r=0, t=40, b=0), height=560, showlegend=True,
    )

    if tiene_consulta:
        md = "### Fragmentos recuperados (top-%d)\n" % k
        for rank, i in enumerate(top, 1):
            md += f"\n**{rank}. #{i}** · similitud `{sims[i]:.3f}`\n\n> {_preview(_CHUNKS[i], 200)}…\n"
    else:
        md = "Escribe una consulta arriba para resaltar los fragmentos más cercanos."
    return fig, md


# ----------------------------------------------------------------------------
# Pestaña 2 · Grafo de conocimiento (GraphRAG)
# ----------------------------------------------------------------------------
class Relacion(BaseModel):
    origen: str = Field(description="Entidad de origen")
    relacion: str = Field(description="Relación entre las entidades")
    destino: str = Field(description="Entidad de destino")


class Grafo(BaseModel):
    relaciones: List[Relacion]


print("Extrayendo el grafo de conocimiento (LLM)...", flush=True)
_llm = get_chat_model(max_tokens=4096)
_res = _llm.with_structured_output(Grafo).invoke(
    "Extrae las relaciones clave entre entidades (personajes, lugares, "
    "organizaciones y objetos) de la siguiente historia. Sé conciso, "
    f"máximo 12 relaciones.\n\n{_TEXTO}"
)
_G = nx.DiGraph()
for r in _res.relaciones:
    _G.add_edge(r.origen, r.destino, rel=r.relacion)
_POS = nx.spring_layout(_G, seed=42, k=0.9)  # layout fijo para estabilidad visual


def ver_grafo(entidad: str):
    activa = entidad.strip().lower() if entidad else ""
    resaltados = set()
    if activa:
        for n in _G.nodes():
            if activa in n.lower():
                resaltados.add(n)
                resaltados.update(_G.successors(n))
                resaltados.update(_G.predecessors(n))

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

    if activa and resaltados:
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
# Interfaz Gradio
# ----------------------------------------------------------------------------
def construir_app():
    with gr.Blocks(title="Visor RAG / GraphRAG") as app:
        gr.Markdown("# 🔎 Visor en vivo · Vector Store (RAG) y Grafo (GraphRAG)\n"
                    "Base de conocimiento: la historia ficticia de **Miravalle**.")
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
