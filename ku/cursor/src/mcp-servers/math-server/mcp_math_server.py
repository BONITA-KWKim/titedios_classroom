import logging

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("Math")

# 도구 1: 더하기 함수
@mcp.tool()
def add(a, b) -> int:
    """더하기"""
    try:
        a = int(a)
        b = int(b)
        logging.info(f"Adding {a} and {b}")
        return a + b
    except ValueError:
        logging.error(f"Invalid input: {a}, {b} - {e}")
        raise ValueError("Invalid input")

@mcp.tool()
def subtract(a, b) -> int:
    """빼기"""
    try:
        a = int(a)
        b = int(b)
        logging.info(f"Subtracting {a} and {b}")
        return a - b
    except ValueError:
        logging.error(f"Invalid input: {a}, {b} - {e}")
        raise ValueError("Invalid input")


if __name__ == "__main__":
    mcp.run(transport="stdio")
