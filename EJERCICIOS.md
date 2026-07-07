# 🏋️ Ejercicios del taller

Ejercicios prácticos para reforzar cada tema. Los archivos con **stubs** (código
a completar) están en la carpeta [`ejercicios/`](ejercicios/) y usan la marca
`# EJERCICIO` donde debes escribir. El código de referencia en `cli/` y
`mcp_server/` queda **completo e intacto** — úsalo si te atoras.

> **Siglas:** LLM = *Large Language Model* · MCP = *Model Context Protocol* ·
> RAG = *Retrieval-Augmented Generation* · GraphRAG = RAG sobre un grafo de conocimiento.

Cada ejercicio sigue el ciclo del taller: **implementas → ejecutas → checkpoint**.

---

## Ejercicio 1 · Agrega un tool al agente (LangChain)

**Archivo:** `ejercicios/01_agrega_tool.py`

1. Completa la herramienta `contar_palabras`.
2. (Reto) Crea una herramienta **nueva** desde cero (p. ej. `invertir_texto`) y
   agrégala a la lista `TOOLS`.

```powershell
python ejercicios/01_agrega_tool.py "¿cuántas palabras tiene 'hola que tal amigas'?"
```

**Otras tools que puedes agregar** (todas sin APIs externas):
`contar_vocales(texto)`, `hora_actual()` (con `datetime`), `es_primo(n)`,
`dias_hasta(fecha)`, `mayusculas(texto)`.

**✅ Checkpoint:** el agente responde usando tu herramienta nueva.

<details><summary>💡 Solución</summary>

```python
@tool
def contar_palabras(texto: str) -> int:
    """Devuelve cuántas PALABRAS tiene un texto."""
    return len(texto.split())


@tool
def invertir_texto(texto: str) -> str:
    """Devuelve el texto escrito al revés."""
    return texto[::-1]


TOOLS = [longitud_texto, contar_palabras, invertir_texto]
```
</details>

---

## Ejercicio 2 · Agrega un tool a un servidor MCP

**Archivos:** `ejercicios/02_servidor.py` (a completar) + `ejercicios/02_cliente.py` (listo).

1. Completa la herramienta `convertir_moneda` en el **servidor**.
2. Ejecuta el **cliente** (lanza el servidor solo):

```powershell
python ejercicios/02_cliente.py "convierte 100 USD a EUR"
```

**Otras tools MCP que puedes agregar:** ampliar `clima` con más ciudades,
ampliar `calcular` con `raíz cuadrada`/`factorial`, o crear un segundo servidor.

**✅ Checkpoint:** el cliente lista tu tool y el agente la usa para responder.

<details><summary>💡 Solución</summary>

```python
@mcp.tool()
def convertir_moneda(monto: float, de: str, a: str) -> str:
    """Convierte un monto entre monedas usando tasas fijas (USD, EUR, MXN, COP)."""
    tasas = {"USD": 1.0, "EUR": 1.08, "MXN": 0.058, "COP": 0.00025}
    de, a = de.upper(), a.upper()
    if de not in tasas or a not in tasas:
        return f"No conozco la moneda {de} o {a}. Usa USD, EUR, MXN o COP."
    en_usd = monto * tasas[de]
    resultado = en_usd / tasas[a]
    return f"{monto} {de} = {resultado:.2f} {a}"
```
</details>

---

## Ejercicio 3 · Agrega un nodo/rama en LangGraph

**Archivo:** `ejercicios/03_agrega_nodo.py`

Agrega una tercera categoría **`matematica`** con su propio nodo:
1. Completa el nodo `responder_matematica`.
2. Regístralo con `add_node`, agrégalo a la ruta y conéctalo al `END`.

```powershell
python ejercicios/03_agrega_nodo.py "¿cuánto es 15*(3+2)?"
```

**✅ Checkpoint:** una pregunta matemática se clasifica como `matematica` y la
responde tu nodo nuevo.

<details><summary>💡 Solución</summary>

```python
def responder_matematica(estado: Estado):
    return {"respuesta": llm.invoke(
        f"Resuelve paso a paso y da el resultado final: {estado['pregunta']}"
    ).content}

# dentro de construir_grafo():
g.add_node("responder_matematica", responder_matematica)
g.add_conditional_edges("clasificar", ruta, {
    "tecnica": "responder_tecnico",
    "general": "responder_general",
    "matematica": "responder_matematica",
})
g.add_edge("responder_matematica", END)
```
</details>

---

## Ejercicio 4 · Experimenta con RAG

**Archivo:** `ejercicios/04_rag_experimento.py`

1. Cambia `K` (1, 3, 5) y observa cuántos/qué fragmentos recupera FAISS.
2. (Reto) Cambia `CHUNK_SIZE` / `CHUNK_OVERLAP` en `taller_core.py`, regenera con
   `python cli/preparar.py --force` y compara.

```powershell
python ejercicios/04_rag_experimento.py "¿quién fundó Miravalle?"
```

**✅ Checkpoint:** puedes explicar cómo cambia la recuperación al variar `K`.

<details><summary>💡 Pistas</summary>

- Con `K=1` el agente tiene menos contexto (puede quedarse corto); con `K=5`,
  más contexto pero también más ruido.
- Chunks más pequeños = búsqueda más precisa pero más fragmentada; más grandes =
  más contexto por fragmento pero menos preciso.
- Después de cambiar el tamaño de chunk **hay que** regenerar el índice (`--force`).
</details>

---

## Ejercicio 5 · Experimenta con GraphRAG

**Archivo:** `ejercicios/05_graphrag_experimento.py`

1. Completa el código que lista los **vecinos** de una entidad.
2. (Reto) Cambia `PROMPT_GRAFO` en `taller_core.py`, regenera con
   `python cli/preparar.py --force` y observa cómo cambia el grafo.

```powershell
python ejercicios/05_graphrag_experimento.py
```

**✅ Checkpoint:** imprimes las relaciones de una entidad y entiendes la
diferencia con RAG (relaciones vs fragmentos de texto).

<details><summary>💡 Solución</summary>

```python
objetivo = ENTIDAD.lower()
for n in G.nodes():
    if objetivo in n.lower():
        for s in G.successors(n):
            print(f"{n} --{G[n][s]['rel']}--> {s}")
        for p in G.predecessors(n):
            print(f"{p} --{G[p][n]['rel']}--> {n}")
```
</details>

---

## Cierre · Compara RAG vs GraphRAG en el visor

Abre el visor y usa el **toggle RAG / GraphRAG** con la misma pregunta:

```powershell
python cli/visor.py
```

Observa que **RAG** recupera *fragmentos de texto* (resaltados en los embeddings)
y **GraphRAG** recupera *relaciones* (resaltadas en el grafo).
