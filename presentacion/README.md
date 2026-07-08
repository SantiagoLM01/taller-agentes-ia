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
5. LLM · 6. Agent · 7. System prompt · 8. Práctica 1 (LangChain)
9. MCP · 10. Arquitectura MCP · 11. Flujo Cliente⇄Servidor MCP · 12. Práctica 2 (Tools con MCP)
13. ¿Por qué LangGraph? · 14. ¿Qué es LangGraph? · 15. El grafo de nuestro código (imagen) · 16. Práctica 3
17. RAG · 18. Componentes de RAG · 19. Similitud densa (coseno, producto punto, distancia euclidiana)
20. Búsqueda léxica (TF-IDF y BM25) · 21. Práctica 4 (RAG)
22. GraphRAG · 23. Práctica 5 · 24. Visor RAG vs GraphRAG · 25. Cierre
