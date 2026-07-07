"""
Ejercicio 02 (servidor) — Agrega una herramienta a un servidor MCP.

MCP = Model Context Protocol (Protocolo de Contexto de Modelo).
Este archivo es el SERVIDOR: expone herramientas. Complétalo y luego, en una
terminal, ejecuta el CLIENTE (que lanza este servidor automáticamente):

    python ejercicios/02_cliente.py "convierte 100 USD a EUR"
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ejercicio-tools")


# ----- Herramienta de ejemplo (YA resuelta) ---------------------------------
@mcp.tool()
def saludar(nombre: str) -> str:
    """Devuelve un saludo para la persona indicada."""
    return f"¡Hola, {nombre}! Bienvenida al taller."


# ===== EJERCICIO: completa esta herramienta MCP =============================
@mcp.tool()
def convertir_moneda(monto: float, de: str, a: str) -> str:
    """Convierte un monto entre monedas usando tasas fijas (USD, EUR, MXN, COP)."""
    # EJERCICIO: usa este diccionario (valor de 1 unidad de cada moneda en USD):
    #   tasas = {"USD": 1.0, "EUR": 1.08, "MXN": 0.058, "COP": 0.00025}
    # Pasos:
    #   1) convierte 'monto' de la moneda 'de' a dólares (USD)
    #   2) convierte de USD a la moneda 'a'
    #   3) devuelve un texto con el resultado
    # Pista: normaliza a mayúsculas con  de.upper()  y  a.upper()
    raise NotImplementedError("Completa la herramienta convertir_moneda")


if __name__ == "__main__":
    mcp.run(transport="stdio")
