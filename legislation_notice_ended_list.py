from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates
import requests

router = APIRouter()
templates = Jinja2Templates(directory="templates")

API_KEY = "145bca1e52594533863a5b12ec70dbc9"

def fetch_ended_notices(age: int, pIndex: int = 1, pSize: int = 100):
    url = "https://open.assembly.go.kr/portal/openapi/nohgwtzsamojdozky"
    params = {
        "KEY": API_KEY,
        "Type": "json",
        "AGE": age,
        "pIndex": pIndex,
        "pSize": pSize
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        raise HTTPException(status_code=500, detail="입법예고 API 호출 실패")

@router.get("/legislation_notice_ended")
def legislation_notice_ended(request: Request, page: int = 1, size: int = 15, query: str = ""):
    age = 22
    all_notices = []

    for pIndex in range(1, 6):
        data = fetch_ended_notices(age, pIndex=pIndex, pSize=100)
        notices_data = data.get("nohgwtzsamojdozky", [])
        
        if not notices_data:
            break

        for item in notices_data:
            rows = item.get("row", [])
            if not rows:
                continue
            for notice in rows:
                all_notices.append({
                    "BILL_NAME": notice.get("BILL_NAME"),
                    "PROPOSER": notice.get("PROPOSER"),
                    "BILL_ID": notice.get("BILL_ID"),
                    "NOTI_ED_DT": notice.get("NOTI_ED_DT"),
                    "LINK_URL": notice.get("LINK_URL"),
                    "CURR_COMMITTEE": notice.get("CURR_COMMITTEE"),
                })



    if query:
        query_lower = query.lower()
        all_notices = [
            notice for notice in all_notices
            if query_lower in (notice.get("BILL_NAME") or "").lower()
            or query_lower in (notice.get("PROPOSER") or "").lower()
        ]

    all_notices.sort(key=lambda x: x.get("ANNOUNCE_DT", ""), reverse=True)
    start_idx = (page - 1) * size
    paginated_notices = all_notices[start_idx:start_idx + size]

    return templates.TemplateResponse("legislation_notice_ended_list.html", {
        "request": request,
        "ended_notices": paginated_notices,
        "page": page,
        "size": size,
        "query": query,
        "total_count": len(all_notices)
    })