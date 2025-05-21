from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates
import requests

router = APIRouter()
templates = Jinja2Templates(directory="templates")

API_KEY = "145bca1e52594533863a5b12ec70dbc9"

def fetch_plenary_bills(age: int, pIndex: int = 1, pSize: int = 100):
    url = "https://open.assembly.go.kr/portal/openapi/nwbpacrgavhjryiph"
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
        raise HTTPException(status_code=500, detail="국회 본회의 API 호출 실패")

@router.get("/plenary")
def get_plenary_bills(request: Request, page: int = 1, size: int = 15, query: str = ""):
    age = 22
    all_bills = []

    for pIndex in range(1, 6):
        data = fetch_plenary_bills(age, pIndex=pIndex, pSize=100)
        bills_data = data.get("nwbpacrgavhjryiph", [])
        
        if not bills_data:
            break

        for item in bills_data:
            rows = item.get("row", [])
            if not rows:
                continue
            for bill in rows:
                all_bills.append({
                    "PROPOSE_DT": bill.get("PROPOSE_DT"),
                    "BILL_NM": bill.get("BILL_NM"),
                    "COMMITTEE_NM": bill.get("COMMITTEE_NM"),
                    "PROC_RESULT_CD": bill.get("PROC_RESULT_CD"),
                    "PROPOSER": bill.get("PROPOSER"),
                    "BILL_ID": bill.get("BILL_ID"),
                    "LINK_URL": bill.get("LINK_URL")
                })


    if query:
        query_lower = query.lower()
        all_bills = [
            bill for bill in all_bills
            if query_lower in (bill.get("BILL_NM") or "").lower()
            or query_lower in (bill.get("PROPOSER") or "").lower()
        ]

    all_bills.sort(key=lambda x: x.get("PROPOSE_DT", ""), reverse=True)
    start_idx = (page - 1) * size
    paginated_bills = all_bills[start_idx:start_idx + size]

    return templates.TemplateResponse("plenary_bills_list.html", {
        "request": request,
        "bills": paginated_bills,
        "page": page,
        "size": size,
        "query": query,
        "total_count": len(all_bills)
    })