from fastapi import APIRouter, Request, HTTPException 
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from sqlalchemy.orm import Session
from db import SessionLocal, EndedLegislationNotice

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/legislation_ended/{bill_id}")
def legislation_ended_detail(request: Request, bill_id: str, db: Session = Depends(get_db)):
    bill = db.query(EndedLegislationNotice).filter(EndedLegislationNotice.bill_id == bill_id).first()

    if not bill:
        raise HTTPException(status_code=404, detail="해당 bill_id에 대한 데이터를 찾을 수 없습니다.")

    return templates.TemplateResponse("legislation_notice_ended_detail.html", {
        "request": request,
        "bill": {
            "BILL_NAME": bill.bill_name,
            "PROPOSER": bill.proposer,
            "BILL_ID": bill.bill_id,
            "NOTI_ED_DT": bill.noti_ed_dt,
            "LINK_URL": bill.link_url,
            "CURR_COMMITTEE": bill.curr_committee,
            "ANNOUNCE_DT": bill.announce_dt,
        },
        "proposal_text": bill.proposal_text,
        "link_url": bill.link_url,
    })
