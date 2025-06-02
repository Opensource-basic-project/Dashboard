from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db import SessionLocal, ForeignLawExample
import math

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/legislative-examples")
def legislative_examples(
    request: Request,
    page: int = 1,
    size: int = 15,
    keyword: str = "",
    db: Session = Depends(get_db)
):
    query_obj = db.query(ForeignLawExample)

    if keyword:
        like_keyword = f"%{keyword}%"
        query_obj = query_obj.filter(
            ForeignLawExample.title.ilike(like_keyword) |
            ForeignLawExample.rel_law.ilike(like_keyword)
        )

    total_count = query_obj.count()
    rows = query_obj.order_by(ForeignLawExample.issue_date.desc()) \
                    .offset((page - 1) * size) \
                    .limit(size).all()

    examples = [{
        "CN": r.cn,
        "TITLE": r.title,
        "REL_LAW": r.rel_law,
        "ASC_NAME": r.asc_name,
        "ISSUE_DATE": r.issue_date,
        "DETAIL_URL": r.detail_url
    } for r in rows]

    total_pages = math.ceil(total_count / size)
    max_buttons = 7
    start_page = max(1, page - max_buttons // 2)
    end_page = min(total_pages, start_page + max_buttons - 1)

    return templates.TemplateResponse("legislative_example_list.html", {
        "request": request,
        "examples": examples,
        "page": page,
        "size": size,
        "keyword": keyword,
        "total_count": total_count,
        "start_page": start_page,
        "end_page": end_page,
        "total_pages": total_pages
    })