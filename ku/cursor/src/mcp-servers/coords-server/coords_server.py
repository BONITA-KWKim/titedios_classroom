import json
from mcp.server.fastmcp import FastMCP, Context
from pathlib import Path

mcp = FastMCP("coord-server")

@mcp.tool()
async def get_coords_by_city(ctx: Context, city: str) -> str:
    """
    주어진 도시 이름의 위도와 경도 좌표를 조회합니다.
    """
    try:
        resource_result_list = await ctx.read_resource("coords://location_coords")

        location_json_str = resource_result_list[0].content

        all_coords = json.loads(location_json_str)

        city_coords = all_coords.get(city)
        
        if city_coords:
            return f"{city}의 좌표는 위도 {city_coords['lat']}, 경도 {city_coords['lon']}입니다."
        else:
            return f"오류: '{city}'에 대한 좌표 정보를 찾을 수 없습니다."

    except Exception as e:
        return f"오류: 리소스 조회 중 문제가 발생했습니다 - {e}"

COORDS_PATH = Path(__file__).parent / "coords.json"

@mcp.resource("coords://location_coords")
def load_location_coords():
    """
    지역별 위도·경도 좌표 정보를 제공하는 정적 리소스
    """
    if not COORDS_PATH.exists():
        return json.dumps({"error": "coords.json 파일을 찾을 수 없습니다."}, ensure_ascii=False)
    
    try:
        with open(COORDS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": f"파일 읽기 실패: {e}"}, ensure_ascii=False)
    return json.dumps()

@mcp.prompt("query_coords")
def query_coords(location: str) -> str:
    """
    특정 지역의 위도·경도를 조회하기 위한 프롬프트 예제
    """
    return f"""
    다음 지역의 위도, 경도(lat, lon) 정보를 조회해주세요: {location}
    get_coords_by_city MCP 도구를 사용하여 {location}의 좌표를 확인하고 알려주세요.
    """

if __name__=="__main__":
    mcp.run(transport="stdio")
