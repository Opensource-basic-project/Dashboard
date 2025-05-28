from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db import SessionLocal, LegislationNotice
import math

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/legislation_notice_ongoing")
def legislation_notice_ongoing(
    request: Request,
    page: int = 1,
    size: int = 15,
    query: str = "",
    committee: str = "",
    db: Session = Depends(get_db)
):
    query_obj = db.query(LegislationNotice)
    
    if query:
        query_filter = f"%{query}%"
        query_obj = query_obj.filter(
            (LegislationNotice.bill_name.ilike(query_filter)) |
            (LegislationNotice.proposer.ilike(query_filter))
        )

    if committee:
        query_obj = query_obj.filter(LegislationNotice.curr_committee == committee)

    total_count = query_obj.count()

    notices = query_obj.order_by(LegislationNotice.announce_dt.desc()) \
                       .offset((page - 1) * size) \
                       .limit(size) \
                       .all()

    notices_list = []
    for n in notices:
        notices_list.append({
            "BILL_NAME": n.bill_name,
            "PROPOSER": n.proposer,
            "BILL_ID": n.bill_id,
            "NOTI_ED_DT": n.noti_ed_dt,
            "LINK_URL": n.link_url,
            "CURR_COMMITTEE": n.curr_committee,
            "ANNOUNCE_DT": n.announce_dt,
        })

    # ✅ 페이지네이션 번호 계산 추가
    total_pages = math.ceil(total_count / size)
    max_buttons = 7
    half = max_buttons // 2

    start_page = max(1, page - half)
    end_page = start_page + max_buttons - 1
    if end_page > total_pages:
        end_page = total_pages
        start_page = max(1, end_page - max_buttons + 1)

    return templates.TemplateResponse("legislation_notice_ongoing_list.html", {
        "request": request,
        "ongoing_notices": notices_list,
        "page": page,
        "size": size,
        "query": query,
        "committee": committee,
        "total_count": total_count,
        "start_page": start_page,
        "end_page": end_page,
        "total_pages": total_pages,  # 선택적
    })
