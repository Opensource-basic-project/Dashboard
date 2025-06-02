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

@router.get("/nationality-trends")
def get_nationality_trends(
    request: Request,
    page: int = 1,
    size: int = 15,
    query: str = "",
    nation: str = "",
    db: Session = Depends(get_db)
):
    query_obj = db.query(ForeignLawTrend)

    # 검색 필터 (제목, 개요, 국가명)
    if query:
        query_filter = f"%{query}%"
        query_obj = query_obj.filter(
            (ForeignLawTrend.title.ilike(query_filter)) |
            (ForeignLawTrend.asc_info.ilike(query_filter)) |
            (ForeignLawTrend.nation_name.ilike(query_filter))
        )
    
    # 국가 필터
    if nation:
        query_obj = query_obj.filter(ForeignLawTrend.nation_name == nation)

    total_count = query_obj.count()

    trends = query_obj.order_by(ForeignLawTrend.procl_date.desc()) \
                     .offset((page - 1) * size) \
                     .limit(size) \
                     .all()

    trend_list = []
    for trend in trends:
        trend_list.append({
            "CN": trend.cn,
            "TITLE": trend.title,
            "NATION_NAME": trend.nation_name,
            "PROCL_DATE": trend.procl_date,
            "ASC_INFO": trend.asc_info,
            "DETAIL_URL": trend.detail_url,
        })

    total_pages = math.ceil(total_count / size)
    max_buttons = 7
    half = max_buttons // 2

    start_page = max(1, page - half)
    end_page = start_page + max_buttons - 1
    if end_page > total_pages:
        end_page = total_pages
        start_page = max(1, end_page - max_buttons + 1)

    return templates.TemplateResponse("nationality_trends_list.html", {
        "request": request,
        "bills": trend_list,
        "page": page,
        "size": size,
        "query": query,
        "nation": nation,
        "total_count": total_count,
        "start_page": start_page,
        "end_page": end_page,
        "total_pages": total_pages,
    })
