"""
setup_check.py — Ejecuta ESTO antes del taller para verificar que todo está listo.

    python setup_check.py

Comprueba:
  1. Versión de Python
  2. Que las librerías necesarias están instaladas
  3. Que el archivo .env existe y tiene las variables
  4. (Opcional) Que Azure OpenAI responde de verdad
"""
import sys
import importlib

OK = "✅"
FAIL = "❌"
WARN = "⚠️ "

PAQUETES = [
    "langchain", "langchain_openai", "langgraph",
    "langchain_mcp_adapters", "mcp", "faiss", "networkx", "dotenv",
]


def check_python():
    v = sys.version_info
    if v >= (3, 10):
        print(f"{OK} Python {v.major}.{v.minor}.{v.micro}")
        return True
    print(f"{FAIL} Python {v.major}.{v.minor}: se requiere 3.10 o superior")
    return False


def check_paquetes():
    todo_ok = True
    for p in PAQUETES:
        try:
            importlib.import_module(p)
            print(f"{OK} {p}")
        except ImportError:
            print(f"{FAIL} {p} no está instalado  ->  pip install -r requirements.txt")
            todo_ok = False
    return todo_ok


def check_env():
    import os
    from dotenv import load_dotenv
    load_dotenv()
    faltan = []
    for var in [
        "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_API_VERSION", "AZURE_OPENAI_CHAT_DEPLOYMENT",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT",
    ]:
        val = os.getenv(var)
        if not val or val.startswith("pega-aqui") or "TU-RECURSO" in (val or ""):
            faltan.append(var)
    if faltan:
        print(f"{WARN}Faltan variables en .env: {', '.join(faltan)}")
        return False
    print(f"{OK} Archivo .env configurado")
    return True


def check_azure():
    try:
        from config import get_chat_model
        llm = get_chat_model()
        r = llm.invoke("Responde solo con la palabra: listo")
        print(f"{OK} Azure OpenAI responde: {r.content.strip()!r}")
        return True
    except Exception as e:
        print(f"{WARN}No se pudo contactar a Azure OpenAI: {e}")
        return False


if __name__ == "__main__":
    print("\n=== Verificación del entorno del taller ===\n")
    py = check_python()
    print()
    pk = check_paquetes()
    print()
    env = check_env()
    print()
    if env:
        check_azure()
    print("\n===========================================")
    if py and pk and env:
        print(f"{OK} ¡Todo listo para el taller!")
    else:
        print(f"{WARN}Revisa los puntos marcados antes de empezar.")
