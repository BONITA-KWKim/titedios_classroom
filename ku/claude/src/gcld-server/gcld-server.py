import os, json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

from mcp.server.fastmcp import FastMCP, Context

# Google API
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

APP = FastMCP("gcal-mcp")

BASE = Path(__file__).parent
CRED_PATH = BASE / "credentials.json"  # GCP에서 받은 파일
TOKEN_PATH = BASE / "token.json"       # 최초 동의 후 생성
# 처음엔 읽기 권한만
SCOPES_READONLY = ["https://www.googleapis.com/auth/calendar.readonly"]
SCOPES_RW       = ["https://www.googleapis.com/auth/calendar"]  # 쓰기 필요 시

def _get_service(readonly: bool = True):
    scopes = SCOPES_READONLY if readonly else SCOPES_RW
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request)  # type: ignore
        else:
            if not CRED_PATH.exists():
                raise FileNotFoundError("credentials.json not found")
            flow = InstalledAppFlow.from_client_secrets_file(str(CRED_PATH), scopes=scopes)
            creds = flow.run_local_server(port=0)  # 브라우저 열림 → 동의
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    return build("calendar", "v3", credentials=creds)

@APP.tool()
def get_calendars() -> List[Dict[str, Any]]:
    """사용자의 캘린더 목록을 조회합니다.(read-only)"""
    svc = _get_service(readonly=True)
    res = svc.calendarList().list().execute()
    items = res.get("items", [])
    return [{"id": it["id"], "summary": it.get("summary"), "primary": it.get("primary", False)} for it in items]

@APP.tool()
def list_events(calendar_id: str = "primary",
                time_min_iso: Optional[str] = None,
                time_max_iso: Optional[str] = None,
                q: Optional[str] = None,
                max_results: int = 10) -> List[Dict[str, Any]]:
    """
    기간 내 이벤트를 조회합니다.(read-only)
    - time_min_iso/time_max_iso: ISO8601 'YYYY-MM-DDTHH:MM:SSZ' 또는 타임존 포함 ISO 권장
    - q: 키워드 검색
    """
    svc = _get_service(readonly=True)
    now = datetime.utcnow()
    time_min = time_min_iso or (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    time_max = time_max_iso or (now + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    events_result = svc.events().list(calendarId=calendar_id, timeMin=time_min,
                                      timeMax=time_max, singleEvents=True, orderBy="startTime",
                                      q=q, maxResults=max_results).execute()
    evts = events_result.get("items", [])
    out = []
    for e in evts:
        out.append({
            "id": e.get("id"),
            "summary": e.get("summary"),
            "start": e.get("start"),
            "end": e.get("end"),
            "location": e.get("location"),
            "hangoutLink": e.get("hangoutLink"),
        })
    return out

# ===== 리소스 추가 =====
@APP.resource("gcal://help")
def help_doc() -> str:
    return (
        "# Google Calendar MCP 사용법\n"
        "- get_calendars: 내 캘린더 목록\n"
        "- list_events: 기간/검색어로 일정 조회\n"
    )

# ===== 프롬프트 추가 =====
@APP.prompt("list_today")
def prompt_list_today(calendar_id: str = "primary", tz: str = "Asia/Seoul") -> str:
    """
    오늘 일정 조회 프롬프트
    - 모델이 list_events 도구를 활용해 한국시간 기준 '오늘' 범위를 계산/조회하도록 지시
    """
    return f"""
다음 지시를 따르세요.

목표: 오늘({tz})의 일정 목록을 {calendar_id} 캘린더에서 조회해 요약합니다.

지침:
1) {tz} 기준으로 오늘 00:00부터 23:59까지의 ISO8601 구간을 계산하세요.
2) gcal MCP의 list_events 도구를 호출하세요.
   - calendar_id="{calendar_id}"
   - time_min_iso, time_max_iso를 오늘 하루 범위로 설정
   - orderBy=startTime, singleEvents=True
3) 표 형태(시작-종료-제목-위치 링크)로 간결히 정리하세요.
"""


@APP.prompt("find_free_slots")
def prompt_find_free_slots(duration_min: int = 60,
                           date_yyyy_mm_dd: str = "",
                           tz: str = "Asia/Seoul",
                           calendar_id: str = "primary") -> str:
    """
    빈 시간대 탐색 프롬프트
    - 모델이 list_events로 바쁜 시간대를 수집하고, 그 사이 공백을 제안하도록 가이드
    """
    return f"""
다음 지시를 따르세요.

목표: {tz} 기준으로 {calendar_id} 캘린더에서 '{date_yyyy_mm_dd or "오늘"}' 하루 동안
최소 {duration_min}분 이상 비어 있는 후보 시간대 3개를 제안합니다.

지침:
1) {tz} 기준으로 대상 날짜의 00:00~23:59 ISO 구간을 계산하세요.
2) gcal MCP의 list_events 도구로 바쁜 구간을 시간 오름차순으로 가져오세요.
3) 바쁜 구간 사이의 공백을 계산해 {duration_min}분 이상인 슬롯만 추립니다.
4) 각 후보 슬롯을 "시작~종료 (분 단위) — 간단 코멘트"로 3개까지 제시합니다.
5) 필요 시 다음 프롬프트로 schedule_meeting을 안내하세요.
"""


if __name__ == "__main__":
    APP.run(transport="stdio")
