"""
config.py — utilidades compartidas del taller.

Centraliza la creación del modelo de chat (LLM) y de embeddings para que cada
notebook solo tenga que llamar a get_chat_model() / get_embeddings().

Este proyecto usa un recurso de **Azure AI Foundry**:
  - Chat (LLM): endpoint de inferencia compatible con OpenAI  (.../models)
  - Embeddings: endpoint de Azure OpenAI clásico              (.../openai/deployments/...)
Los valores se leen del archivo .env (ver .env.example).
"""
import os
from dotenv import load_dotenv

load_dotenv()  # carga las variables desde el archivo .env


def _require(var: str) -> str:
    val = os.getenv(var)
    if not val or val.startswith("pega-aqui") or "TU-RECURSO" in val:
        raise RuntimeError(
            f"Falta configurar la variable '{var}' en tu archivo .env. "
            f"Copia .env.example a .env y rellena los valores."
        )
    return val


def get_chat_model(temperature: float = 0.0, max_tokens: int = 2048):
    """Modelo de chat (LLM) del endpoint de inferencia de Azure AI Foundry.

    El endpoint (.../models) es compatible con la API de OpenAI, por eso usamos
    ChatOpenAI apuntando a él con la versión de API como query param.
    """
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=_require("AZURE_CHAT_MODEL"),
        api_key=_require("AZURE_API_KEY"),
        base_url=_require("AZURE_CHAT_ENDPOINT"),
        default_query={"api-version": _require("AZURE_CHAT_API_VERSION")},
        temperature=temperature,
        max_tokens=max_tokens,
    )


def get_embeddings():
    """Modelo de embeddings servido por el endpoint de Azure OpenAI clásico."""
    from langchain_openai import AzureOpenAIEmbeddings

    return AzureOpenAIEmbeddings(
        azure_endpoint=_require("AZURE_EMBEDDING_ENDPOINT"),
        api_key=_require("AZURE_API_KEY"),
        api_version=_require("AZURE_EMBEDDING_API_VERSION"),
        azure_deployment=_require("AZURE_EMBEDDING_DEPLOYMENT"),
    )
