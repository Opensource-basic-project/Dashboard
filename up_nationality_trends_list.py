import requests
from db import SessionLocal, ForeignLawTrend
from sqlalchemy.orm import Session

API_KEY = "9f665ae0aeea4ed1bc2f23e1326456a2"

def fetch_foreign_law_trends(page: int = 1, display_lines: int = 100, keyword: str = "법"):
    url = "http://lnp.nanet.go.kr/openapi/lawpreced"
    params = {
        "KEY": API_KEY,
        "TYPE": "json",
        "PAGE_NO": page,
        "DISPLAY_LINES": display_lines,
        "SEARCH_KEYWORD": keyword,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def save_foreign_law_trends_to_db(db: Session, laws: list):
    for law in laws:
        cn = law.get("CN")
        if not cn:
            continue

        exists = db.query(ForeignLawTrend).filter(ForeignLawTrend.cn == cn).first()
        if exists:
            continue

        new_law = ForeignLawTrend(
            cn=cn,
            title=law.get("TITLE"),
            nation_name=law.get("NATION_NAME"),
            procl_date=law.get("PROCL_DATE"),
            asc_info=law.get("ASC_INFO"),
            detail_url=law.get("DETAIL_URL"),
        )
        db.add(new_law)
    db.commit()

def update_foreign_law_trends_db():
    all_laws = []
    for page in range(1, 6):  # 최대 5페이지까지 요청
        data = fetch_foreign_law_trends(page=page, display_lines=100)
        print(data)
        law_list = data.get("lawpreced", {}).get("list", [])
        if not law_list:
            break
        all_laws.extend(law_list)

    db = SessionLocal()
    try:
        db.query(ForeignLawTrend).delete()
        db.commit()
        save_foreign_law_trends_to_db(db, all_laws)
        print("주요국 입법동향 DB 갱신 완료")
    finally:
        db.close()

if __name__ == "__main__":
    update_foreign_law_trends_db()
