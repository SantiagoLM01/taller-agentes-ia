"""
config.py — utilidades compartidas del taller.

Centraliza la creación del modelo de chat (LLM) y de embeddings de Azure OpenAI
para que cada notebook solo tenga que llamar a get_chat_model() / get_embeddings().
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


def get_chat_model(temperature: float = 0.0):
    """Devuelve un modelo de chat (LLM) de Azure OpenAI listo para usar."""
    from langchain_openai import AzureChatOpenAI

    return AzureChatOpenAI(
        azure_endpoint=_require("AZURE_OPENAI_ENDPOINT"),
        api_key=_require("AZURE_OPENAI_API_KEY"),
        api_version=_require("AZURE_OPENAI_API_VERSION"),
        azure_deployment=_require("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        temperature=temperature,
    )


def get_embeddings():
    """Devuelve el modelo de embeddings de Azure OpenAI."""
    from langchain_openai import AzureOpenAIEmbeddings

    return AzureOpenAIEmbeddings(
        azure_endpoint=_require("AZURE_OPENAI_ENDPOINT"),
        api_key=_require("AZURE_OPENAI_API_KEY"),
        api_version=_require("AZURE_OPENAI_API_VERSION"),
        azure_deployment=_require("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    )
