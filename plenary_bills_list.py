from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db import SessionLocal, PlenaryBill  # PlenaryBill 테이블 import
import math

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/plenary")
def get_plenary_bills(
    request: Request,
    page: int = 1,
    size: int = 15,
    query: str = "",
    committee: str = "",
    db: Session = Depends(get_db)
):
    query_obj = db.query(PlenaryBill)

    if query:
        query_filter = f"%{query}%"
        query_obj = query_obj.filter(
            (PlenaryBill.bill_name.ilike(query_filter)) |
            (PlenaryBill.proposer.ilike(query_filter))
        )

    if committee:
        query_obj = query_obj.filter(PlenaryBill.curr_committee == committee)

    total_count = query_obj.count()

    bills = query_obj.order_by(PlenaryBill.propose_dt.desc()) \
                 .offset((page - 1) * size) \
                 .limit(size) \
                 .all()

    bill_list = []
    for bill in bills:
        bill_list.append({
            "BILL_ID": bill.bill_id,
            "BILL_NM": bill.bill_name,
            "PROPOSER": bill.proposer,
            "PROC_RESULT_CD": bill.proc_result_cd,
            "COMMITTEE_NM": bill.committee_nm,
            "PROPOSE_DT": bill.propose_dt,
            "LINK_URL": bill.link_url
        })
        
    total_pages = math.ceil(total_count / size)
    max_buttons = 7
    half = max_buttons // 2

    start_page = max(1, page - half)
    end_page = start_page + max_buttons - 1
    if end_page > total_pages:
        end_page = total_pages
        start_page = max(1, end_page - max_buttons + 1)


    return templates.TemplateResponse("plenary_bills_list.html", {
        "request": request,
        "bills": bill_list,
        "page": page,
        "size": size,
        "query": query,
        "committee": committee,
        "total_count": total_count,
        "start_page": start_page,
        "end_page": end_page,
        "total_pages": total_pages, 
    })
