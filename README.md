# Taller de Agentes de Inteligencia Artificial 🤖

Taller práctico de 2 horas para construir agentes de IA paso a paso, cubriendo:

**LLM → Agentes (LangChain) → Tools (MCP) → LangGraph → RAG → GraphRAG**

Todo el código está en **notebooks** para VS Code. Cada notebook tiene huecos `# TODO`
que completas en vivo, y en `soluciones/` está la versión completa por si te atoras.

> **Siglas:** LLM = *Large Language Model* (Modelo de Lenguaje Grande) · MCP = *Model Context Protocol* ·
> RAG = *Retrieval-Augmented Generation* (Generación Aumentada por Recuperación).

---

## 📋 Requisitos previos (haz esto ANTES del taller)

1. **Python 3.10 o superior** — comprueba con `python --version`.
2. **VS Code** con las extensiones *Python* y *Jupyter* (se recomiendan solas al abrir el proyecto).
3. Credenciales de **Azure OpenAI** (te las darán los organizadores).

## ⚙️ Instalación

```powershell
# 1. Crear y activar un entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate         # macOS / Linux

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar las credenciales
copy .env.example .env              # en macOS/Linux: cp .env.example .env
# ...edita .env y pega tu endpoint, API key y nombres de deployment

# 4. Verificar que todo está listo
python setup_check.py
```

Si `setup_check.py` muestra ✅ en todo, ¡estás lista para el taller!

---

## 🗂️ Estructura del proyecto

```
taller-agentes-ia/
├── notebooks/            # Notebooks del taller (con # TODO para completar)
│   ├── 01_llm_y_agente.ipynb
│   ├── 02_tools_mcp.ipynb
│   ├── 03_langgraph.ipynb
│   ├── 04_rag.ipynb
│   └── 05_graphrag.ipynb
├── soluciones/           # Versiones completas de cada notebook
├── mcp_server/
│   └── server.py         # Servidor MCP de ejemplo (tools: calcular, clima)
├── data/
│   └── agentes_ia.md     # Documento usado por RAG y GraphRAG
├── config.py             # Crea el LLM y los embeddings de Azure OpenAI
├── setup_check.py        # Verificador del entorno
├── requirements.txt
└── .env.example
```

---

## ⏱️ Agenda (2 horas)

| Tiempo | Tema | Notebook |
|---|---|---|
| 0:00–0:20 | LLM + Agentes con LangChain | `01_llm_y_agente.ipynb` |
| 0:20–0:45 | Tools con MCP | `02_tools_mcp.ipynb` |
| 0:45–1:10 | Migración a LangGraph | `03_langgraph.ipynb` |
| 1:10–1:35 | RAG | `04_rag.ipynb` |
| 1:35–1:55 | GraphRAG | `05_graphrag.ipynb` |
| 1:55–2:00 | Cierre | — |

**Ciclo de cada bloque:** demo corta → completas los `# TODO` → checkpoint rápido.

---

## ▶️ Cómo trabajar en los notebooks

1. Abre la carpeta en VS Code.
2. Abre el notebook del bloque actual.
3. Selecciona el kernel de Python del entorno virtual (`.venv`).
4. Ejecuta las celdas de arriba hacia abajo, completando los `# TODO`.
5. Llega al **✅ Checkpoint** de cada notebook antes de pasar al siguiente.

---

## 🧰 Tecnologías

LangChain · LangGraph · Model Context Protocol (MCP) · Azure OpenAI · FAISS · NetworkX
