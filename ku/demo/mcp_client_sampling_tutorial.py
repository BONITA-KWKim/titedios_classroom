from mcp.server.fastmcp import FastMCP
from typing import List

mcp = FastMCP("grading-server")

@mcp.tool()
def get_scores() -> List[int]:
    """학생들의 점수를 반환합니다."""
    return [85, 90, 72, 64, 98]

# (옵션) 결과 저장 흉내
latest_summary = {"text": ""}

@mcp.tool()
def save_summary(text: str) -> str:
    """LLM이 만든 코멘트를 저장합니다."""
    latest_summary["text"] = text
    return "요약 코멘트가 저장되었습니다."

# 프롬프트(문자열) 예: LLM이 툴을 먼저 쓰도록 강하게 유도
@mcp.prompt()
def analyze_prompt() -> str:
    return (
        "반드시 절차를 따르세요:\n"
        "1) `get_scores` 도구를 호출해 점수 배열을 가져온다.\n"
        "2) 평균/최고/최저를 계산한다.\n"
        "3) 2~3문장의 코멘트를 작성한다.\n"
        "(선택) 코멘트를 `save_summary` 도구로 저장한다."
    )

if __name__ == "__main__":
    mcp.run()
