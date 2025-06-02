from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db import SessionLocal, ForeignLawTrend
import math

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/legislative-trends")
def legislative_trends(
    request: Request,
    page: int = 1,
    size: int = 15,
    keyword: str = "",
    nation: str = "",
    db: Session = Depends(get_db)
):
    query_obj = db.query(ForeignLawTrend)

    if keyword:
        like_keyword = f"%{keyword}%"
        query_obj = query_obj.filter(
            ForeignLawTrend.title.ilike(like_keyword) |
            ForeignLawTrend.asc_info.ilike(like_keyword)
        )
    
    if nation:
        query_obj = query_obj.filter(ForeignLawTrend.nation_name == nation)

    total_count = query_obj.count()
    rows = query_obj.order_by(ForeignLawTrend.procl_date.desc()) \
                    .offset((page - 1) * size) \
                    .limit(size).all()

    laws = [{
        "CN": r.cn,
        "TITLE": r.title,
        "NATION_NAME": r.nation_name,
        "PROCL_DATE": r.procl_date,
        "ASC_INFO": r.asc_info,
        "DETAIL_URL": r.detail_url
    } for r in rows]

    total_pages = math.ceil(total_count / size)
    max_buttons = 7
    start_page = max(1, page - max_buttons // 2)
    end_page = min(total_pages, start_page + max_buttons - 1)

    return templates.TemplateResponse("legislative_trends_list.html", {
        "request": request,
        "laws": laws,
        "page": page,
        "size": size,
        "keyword": keyword,
        "nation": nation,
        "total_count": total_count,
        "start_page": start_page,
        "end_page": end_page,
        "total_pages": total_pages
    })
