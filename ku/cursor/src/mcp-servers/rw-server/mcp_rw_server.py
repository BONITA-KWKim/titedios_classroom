import logging

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("File RW")

@mcp.tool()
def read_file(file_path: str) -> str:
    """파일 읽기"""
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        raise Exception(f"Error reading file: {e}")

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """파일 쓰기"""
    try:
        with open(file_path, "w") as file:
            file.write(content)
        return "File written successfully"
    except Exception as e:
        logging.error(f"Error writing file: {e}")
        raise Exception(f"Error writing file: {e}")

if __name__ == "__main__":
    mcp.run(transport="stdio")

