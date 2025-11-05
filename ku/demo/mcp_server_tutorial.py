from mcp.server.fastmcp import FastMCP
from pathlib import Path

mcp = FastMCP("Hello-MCP-Server")


@mcp.tool()
def welcome(name: str) -> str:
    """
    입력한 이름과 환영 인사를 조합해 문구를 생성합니다.
    """
    return f"Hello, {name}!\nNice to have you here in MCP world!"

@mcp.resource("greeting://intro")
def server_readme():
    """
    서버 소개 정보를 제공하는 리소스입니다.
    """
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8")
    return "Welcom to the Hello MCP Server!"

@mcp.prompt()
def get_name(name:str) -> str:
    """
    이름을 입력받아 환영 메시지를 생성하는 프롬프트입니다.
    """
    return f"""
    welcome MCP 도구를 사용하여 이름 {name}과 환영인사를 조합해 문구를 만들어 주세요.
    """

@mcp.tool()
def get_scores() -> list:
    """
    학생들의 점수 배열을 반환합니다.
    이 결과를 바탕으로 코멘트를 생성하려면 먼저 이 도구를 호출한 뒤,
    반환된 점수로 평균/최고/최저를 계산하세요.
    """
    return [85, 90, 72, 64, 98]

if __name__=="__main__":
    mcp.run()
