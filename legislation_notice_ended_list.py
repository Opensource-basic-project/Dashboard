from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db import SessionLocal, EndedLegislationNotice  # 종료 테이블 import

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/legislation_notice_ended")
def legislation_notice_ended(request: Request, page: int = 1, size: int = 15, query: str = "", db: Session = Depends(get_db)):
    # DB에서 쿼리 및 페이징 처리
    query_obj = db.query(EndedLegislationNotice)
    if query:
        query_filter = f"%{query}%"
        query_obj = query_obj.filter(
            (EndedLegislationNotice.bill_name.ilike(query_filter)) |
            (EndedLegislationNotice.proposer.ilike(query_filter))
        )

    total_count = query_obj.count()

    notices = query_obj.order_by(EndedLegislationNotice.announce_dt.desc()) \
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

    return templates.TemplateResponse("legislation_notice_ended_list.html", {
        "request": request,
        "ended_notices": notices_list,
        "page": page,
        "size": size,
        "query": query,
        "total_count": total_count,
    })
