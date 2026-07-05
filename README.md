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
├── cli/                  # Mismos pasos, pero para la terminal (interactivos)
│   ├── 01_agente.py
│   ├── 02_mcp.py
│   ├── 03_langgraph.py
│   ├── 04_rag.py
│   ├── 05_graphrag.py
│   ├── preparar.py       # Genera por adelantado las cachés (FAISS + grafo)
│   └── visor.py          # Visor interactivo (vector store + grafo en tiempo real)
├── mcp_server/
│   ├── server.py         # Servidor MCP de ejemplo (tools: calcular, clima)
│   └── rag_server.py     # Servidor MCP con la tool de RAG (buscar_documentos)
├── data/
│   └── historia_zelanor.md   # Historia ficticia usada por RAG y GraphRAG
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

## 💻 Correr cada paso desde la terminal (CLI)

Además de los notebooks, en `cli/` tienes un script por cada tema. Cada uno funciona
de dos formas:

```powershell
# Modo chat interactivo: escribes mensajes y el agente responde ('salir' para terminar)
python cli/01_agente.py

# Modo pregunta única: pasas la pregunta como argumento y obtienes la respuesta
python cli/01_agente.py "¿Cuántos caracteres tiene 'inteligencia'? Usa la herramienta."
```

| Script | Qué hace | Ejemplo de pregunta |
|---|---|---|
| `cli/01_agente.py` | Agente (LLM + tool) | *"¿Cuántos caracteres tiene 'LangChain'?"* |
| `cli/02_mcp.py` | Agente con tools vía MCP | *"¿Cuánto es 15*(3+2)? ¿Qué clima hace en Madrid?"* |
| `cli/03_langgraph.py` | Flujo con LangGraph (clasifica y enruta) | *"¿Qué es un embedding?"* |
| `cli/04_rag.py` | RAG agéntico (agente + MCP + tool) | *"¿Quién fundó Miravalle y en qué año?"* |
| `cli/05_graphrag.py` | GraphRAG (grafo de conocimiento) | *"Miravalle"* (una entidad) |

> Los scripts `02` y `04` abren **una sola sesión MCP** que se mantiene viva durante
> todo el chat, así cada mensaje responde rápido.

---

## 🔎 Visor interactivo (vector store + grafo en tiempo real)

Para *ver* qué pasa por dentro de RAG y GraphRAG hay una pequeña app web:

```powershell
python cli/visor.py
```

Abre **http://127.0.0.1:7860** en el navegador. Tiene dos pestañas:

- **Vector Store (RAG):** proyecta en 3D los *embeddings* (vectores numéricos) de los
  fragmentos de la historia. Escribes una consulta y ves qué fragmentos quedan más
  cerca (los que RAG recuperaría) resaltados junto al punto de tu consulta.
- **Grafo (GraphRAG):** muestra el grafo de conocimiento (entidades y relaciones)
  extraído de la historia. Eliges una entidad y resalta su vecindario, con una
  explicación generada por el modelo.

> Requiere las dependencias de visualización (`gradio`, `plotly`, `scikit-learn`),
> ya incluidas en `requirements.txt`.

### Preparar las cachés antes del taller (opcional pero recomendado)

El índice **FAISS** (vector store de RAG) y el **grafo** (GraphRAG) se generan la
primera vez que se usan y quedan cacheados en `mcp_server/_faiss_cache/`. Para que
en vivo todo cargue al instante, puedes generarlos por adelantado:

```powershell
python cli/preparar.py           # crea lo que falte
python cli/preparar.py --force   # borra las cachés y las regenera desde cero
```

Después, tanto `cli/04_rag.py` (el agente) como `cli/visor.py` cargan directamente
desde disco, sin esperar a construir el índice ni a llamar al modelo.

---

## 🧰 Tecnologías

LangChain · LangGraph · Model Context Protocol (MCP) · Azure OpenAI · FAISS · NetworkX
