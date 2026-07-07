# Presentación del taller

- **`Taller_Agentes_IA_2h.pptx`** — presentación lista para usar (22 diapositivas, 2 horas).
- **`build_deck.py`** — genera el `.pptx` desde código (python-pptx). Editá este archivo y regenerá; no edites el `.pptx` a mano.

## Regenerar la presentación

```powershell
pip install python-pptx
python build_deck.py
```

El archivo se guarda junto al script como `Taller_Agentes_IA_2h.pptx`.
Para guardarlo en otra ruta, definí la variable de entorno `DECK_OUT`:

```powershell
$env:DECK_OUT = "C:\ruta\salida.pptx"; python build_deck.py
```

## Contenido (orden de las diapositivas)

1. Título · 2. Agenda · 3. Reglas · 4. Setup
5. LLM · 6. Agent · 7. Práctica 1 (LangChain)
8. MCP · 9. Arquitectura MCP · 10. Práctica 2 (Tools con MCP)
11. ¿Por qué LangGraph? · 12. ¿Qué es LangGraph? · 13. Práctica 3
14. RAG · 15. Comparación con/sin RAG · 16. Similitud densa (coseno, producto punto, distancia euclidiana)
17. Búsqueda léxica (TF-IDF y BM25) · 18. Práctica 4 (RAG)
19. GraphRAG · 20. Práctica 5 · 21. Visor RAG vs GraphRAG · 22. Cierre
