# Guía rápida: Agentes de Inteligencia Artificial

## LLM (Large Language Model)
Un LLM, o Modelo de Lenguaje Grande, es un modelo entrenado con enormes cantidades
de texto para comprender y generar lenguaje natural. GPT-4o es un ejemplo de LLM
desarrollado por OpenAI. Los LLM funcionan mejor cuando reciben contexto claro y
prompts específicos. Son la base sobre la que se construyen los agentes modernos.

## Agentes
Un agente es un LLM combinado con instrucciones y herramientas (tools). A diferencia
de un chatbot tradicional, un agente sigue un ciclo: observar, decidir, actuar y
responder. El agente puede decidir por sí mismo qué herramienta usar para resolver
una tarea. LangChain es un framework muy usado para construir agentes.

## MCP (Model Context Protocol)
El Model Context Protocol, o Protocolo de Contexto de Modelo, es un estándar creado
por Anthropic para conectar modelos de lenguaje con herramientas externas. MCP define
un cliente (tu aplicación o agente) y un servidor (que expone las herramientas). Gracias
a MCP, las herramientas se pueden reutilizar entre distintos agentes y aplicaciones,
mejorando la interoperabilidad y la escalabilidad.

## LangGraph
LangGraph es un framework construido sobre LangChain para orquestar agentes como grafos.
En LangGraph, los nodos representan pasos y las aristas (edges) representan transiciones
entre pasos. LangGraph permite manejar estado compartido, ramas condicionales y reintentos.
Es ideal cuando el flujo del agente es complejo o de larga duración.

## RAG (Retrieval-Augmented Generation)
RAG, o Generación Aumentada por Recuperación, es una técnica que recupera contexto
relevante antes de que el LLM genere una respuesta. El proceso típico convierte los
documentos en fragmentos (chunks), calcula embeddings, los guarda en un vector store
y usa un retriever para buscar por similitud. RAG reduce las alucinaciones y mejora la
precisión de las respuestas. RAG se puede implementar con LangChain.

## GraphRAG
GraphRAG combina RAG con un grafo de conocimiento. En lugar de solo buscar fragmentos
por similitud, GraphRAG extrae entidades y las relaciones explícitas entre ellas.
Esto lo hace especialmente útil para consultas multi-salto (multi-hop), donde la
respuesta depende de conectar varios hechos relacionados. Microsoft publicó una
implementación conocida de GraphRAG.
