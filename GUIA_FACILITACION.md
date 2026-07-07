# 🎬 Guía de facilitación · Taller de Agentes de IA (2 horas)

Guía minuto a minuto para quien dirige el taller. Formato de cada bloque:
**demo corta → implementación guiada → checkpoint rápido**.

> **Siglas:** LLM = *Large Language Model* · MCP = *Model Context Protocol* ·
> RAG = *Retrieval-Augmented Generation* · GraphRAG = RAG sobre un grafo de conocimiento.

---

## 📦 Material del taller

| Tipo | Ubicación | Qué es |
|---|---|---|
| Presentación | `Taller_Agentes_IA_2h.pptx` | 20 slides |
| Notebooks | `notebooks/01…05` | Uno por tema (VS Code) |
| CLIs | `cli/01…05`, `preparar.py`, `visor.py` | Mismos pasos en terminal + visor |
| Servidores MCP | `mcp_server/server.py`, `rag_server.py` | Tools de ejemplo y de RAG |
| Núcleo compartido | `taller_core.py` | Receta FAISS (RAG) + grafo (GraphRAG) |
| Base de conocimiento | `data/historia_zelanor.md` | Historia ficticia de **Miravalle** |
| Ejercicios | `ejercicios/`, `EJERCICIOS.md` | Stubs a completar + soluciones |
| Setup | `setup.ps1`, `setup_check.py`, `requirements.txt` | Instalación y verificación |

---

## ✅ Antes del taller

**Para las participantes (envía 2–3 días antes):**
> 1. Clona el repositorio.
> 2. Corre `.\setup.ps1`.
> 3. Pega tus credenciales de Azure OpenAI en `.env`.
> 4. Verifica con `python setup_check.py` (todo debe salir ✅).
> 5. Corre una vez `python cli\preparar.py` para pre-generar las cachés (RAG + grafo).

**Para ti (facilitadora):**
- Deja el visor abierto: `python cli\visor.py` (http://127.0.0.1:7860).
- Ten esta guía y el cheat-sheet a mano.

---

## Cronograma

| Tiempo | Bloque | Slides |
|---|---|---|
| 0:00–0:05 | Apertura | 1–4 |
| 0:05–0:20 | LLM + Agents (LangChain) | 5–7 |
| 0:20–0:45 | Tools con MCP | 8–10 |
| 0:45–1:10 | Migración a LangGraph | 11–13 |
| 1:10–1:35 | RAG | 14–16 |
| 1:35–1:55 | GraphRAG | 17–19 |
| 1:55–2:00 | Cierre | 20 |

---

## 🟣 Bloque 0 · Apertura — 0:00–0:05 *(slides 1–4)*
- Bienvenida, agenda y reglas (demo → implementas → checkpoint; pide ayuda rápido).
- **Checkpoint de setup:** "¿A todas les dio ✅ en `setup_check.py`?" Resuelve rezagadas ahora.

## 🟣 Bloque 1 · LLM + Agents — 0:05–0:20 *(slides 5–7)*
- **Teoría (3 min):** LLM = genera texto; Agent = LLM + instrucciones + tools.
- **Demo (4 min):**
  ```powershell
  python cli\01_agente.py "¿Cuántos caracteres tiene 'LangChain'?"
  ```
- **Práctica 1 (7 min):** `ejercicios\01_agrega_tool.py` → completar `contar_palabras`; reto `invertir_texto`.
  ```powershell
  python ejercicios\01_agrega_tool.py "¿cuántas palabras tiene 'hola que tal amigas'?"
  ```
- **✅ Checkpoint:** el agente responde usando su tool nueva.

## 🟣 Bloque 2 · Tools con MCP — 0:20–0:45 *(slides 8–10)*
- **Teoría (5 min):** MCP conecta el modelo con herramientas externas (cliente ↔ servidor ↔ tools).
- **Demo (5 min):**
  ```powershell
  python cli\02_mcp.py "¿Cuánto es 15*(3+2)? ¿Qué clima hace en Madrid?"
  ```
- **Práctica 2 (12 min):** `ejercicios\02_servidor.py` → completar `convertir_moneda`; correr cliente:
  ```powershell
  python ejercicios\02_cliente.py "convierte 100 USD a EUR"
  ```
- **✅ Checkpoint:** el cliente lista `convertir_moneda` y el agente la usa.

## 🟣 Bloque 3 · Migración a LangGraph — 0:45–1:10 *(slides 11–13)*
- **Teoría (6 min):** por qué migrar (control de flujo, estado, ramas); nodos y transiciones.
- **Demo (5 min):**
  ```powershell
  python cli\03_langgraph.py "¿Qué es un embedding?"
  ```
- **Práctica 3 (12 min):** `ejercicios\03_agrega_nodo.py` → añadir categoría `matematica` (nodo + ruta + edge).
  ```powershell
  python ejercicios\03_agrega_nodo.py "¿cuánto es 15*(3+2)?"
  ```
- **✅ Checkpoint:** una pregunta matemática cae en el nodo nuevo.

## 🟣 Bloque 4 · RAG — 1:10–1:35 *(slides 14–16)*
- **Teoría (5 min):** RAG recupera contexto antes de responder; pipeline documentos → chunks → embeddings → vector store → LLM.
- **Demo (6 min):** en el **visor** (pestaña *Agente RAG en vivo*, modo RAG) pregunta *"¿Quién fundó Miravalle?"* → respuesta + fragmentos FAISS resaltados en 3D.
- **Práctica 4 (12 min):** `ejercicios\04_rag_experimento.py` → variar `K` (1/3/5).
  ```powershell
  python ejercicios\04_rag_experimento.py "¿quién fundó Miravalle?"
  ```
- **✅ Checkpoint:** explican cómo cambia la recuperación al variar `K`.

## 🟣 Bloque 5 · GraphRAG — 1:35–1:55 *(slides 17–19)*
- **Teoría (4 min):** GraphRAG = RAG sobre un grafo (entidades + relaciones); útil para multi-salto.
- **Demo (5 min):** en el visor, **toggle a GraphRAG**, misma pregunta → recupera *relaciones* resaltadas en el grafo. Compara con RAG (slide 19).
- **Práctica 5 (8 min):** `ejercicios\05_graphrag_experimento.py` → listar vecinos de una entidad.
  ```powershell
  python ejercicios\05_graphrag_experimento.py
  ```
- **✅ Checkpoint:** imprimen las relaciones de Miravalle y explican texto (RAG) vs relaciones (GraphRAG).

## 🟣 Bloque 6 · Cierre — 1:55–2:00 *(slide 20)*
- Tabla "cuándo usar cada enfoque": LLM solo · Agent+MCP · LangGraph · RAG · GraphRAG.
- Comparte el repo para seguir experimentando.

---

## 🛠️ Cheat-sheet de comandos

```powershell
# Setup (antes del taller)
.\setup.ps1
python setup_check.py
python cli\preparar.py             # pre-genera cachés RAG + grafo

# Demos por bloque
python cli\01_agente.py "..."      # LLM + Agent
python cli\02_mcp.py "..."         # MCP
python cli\03_langgraph.py "..."   # LangGraph
python cli\visor.py                # RAG / GraphRAG en vivo (deja abierto)

# Ejercicios
python ejercicios\01_agrega_tool.py "..."
python ejercicios\02_cliente.py "..."
python ejercicios\03_agrega_nodo.py "..."
python ejercicios\04_rag_experimento.py "..."
python ejercicios\05_graphrag_experimento.py
```

---

## ⚠️ Riesgos y mitigaciones

- **Setup en vivo** es el mayor riesgo → exige `setup_check.py` ✅ **antes** del taller.
- **Cachés** → que corran `preparar.py` antes, para que RAG/GraphRAG no indexen en vivo.
- **Tiempo justo** → si un bloque se atrasa, salta la parte de escribir código del ejercicio
  y quédate solo con la demo en el visor.
- **Preguntas fuera de contexto** → en RAG/GraphRAG, si algo no está en la historia de
  Miravalle, el agente debe decir que no lo sabe (así se ve el valor de la recuperación).
