"""
server.py — Servidor MCP (Model Context Protocol) de ejemplo para el taller.

Expone 2 herramientas sencillas que el agente podrá usar:
  - calcular(expresion): evalúa una operación matemática segura
  - clima(ciudad): devuelve un clima simulado (mock)

Se ejecuta por "stdio": no necesitas abrir puertos ni levantar un servidor web.
El notebook 02 lo lanza automáticamente como un subproceso.

(El servidor con la herramienta de RAG del notebook 04 está aparte, en
`mcp_server/rag_server.py`, porque carga librerías más pesadas.)

Para probarlo a mano:
    python mcp_server/server.py
(quedará esperando mensajes por la entrada estándar; ciérralo con Ctrl+C)
"""
import ast
import operator

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("taller-tools")

# --- Evaluador aritmético seguro (sin usar eval()) ---
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.USub: operator.neg,
    ast.Mod: operator.mod,
}


def _eval(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Expresión no permitida")


@mcp.tool()
def calcular(expresion: str) -> str:
    """Evalúa una expresión matemática simple, p. ej. '3 * (4 + 5)'."""
    try:
        resultado = _eval(ast.parse(expresion, mode="eval").body)
        return f"El resultado de {expresion} es {resultado}"
    except Exception as e:
        return f"No pude calcular '{expresion}': {e}"


@mcp.tool()
def clima(ciudad: str) -> str:
    """Devuelve el clima actual (simulado) de una ciudad."""
    datos = {
        "ciudad de méxico": "22°C, parcialmente nublado",
        "madrid": "18°C, soleado",
        "bogotá": "14°C, lluvioso",
        "buenos aires": "25°C, despejado",
    }
    clave = ciudad.strip().lower()
    return f"Clima en {ciudad}: {datos.get(clave, '20°C, agradable (dato simulado)')}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
