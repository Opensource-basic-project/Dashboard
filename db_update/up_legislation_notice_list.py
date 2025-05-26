import requests
from db import SessionLocal, LegislationNotice
from sqlalchemy.orm import Session

API_KEY = "145bca1e52594533863a5b12ec70dbc9"

def fetch_ongoing_notices(age: int, pIndex: int = 1, pSize: int = 100):
    url = "https://open.assembly.go.kr/portal/openapi/nknalejkafmvgzmpt"
    params = {
        "KEY": API_KEY,
        "Type": "json",
        "AGE": age,
        "pIndex": pIndex,
        "pSize": pSize
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def save_notices_to_db(db: Session, notices: list):
    # 현재는 기존 데이터 모두 삭제 후 재저장 방식으로 변경
    # 필요 시 중복체크 로직으로 바꿀 수 있음
    for notice in notices:
        bill_id = notice.get("BILL_ID")
        if not bill_id:
            continue
        exists = db.query(LegislationNotice).filter(LegislationNotice.bill_id == bill_id).first()
        if exists:
            continue

        new_notice = LegislationNotice(
            bill_name=notice.get("BILL_NAME"),
            proposer=notice.get("PROPOSER"),
            bill_id=bill_id,
            noti_ed_dt=notice.get("NOTI_ED_DT"),
            link_url=notice.get("LINK_URL"),
            curr_committee=notice.get("CURR_COMMITTEE"),
            announce_dt=notice.get("ANNOUNCE_DT"),
        )
        db.add(new_notice)
    db.commit()

def update_legislation_db():
    age = 22
    all_rows = []
    for pIndex in range(1, 6):
        data = fetch_ongoing_notices(age, pIndex=pIndex, pSize=100)
        notices_data = data.get("nknalejkafmvgzmpt", [])
        if not notices_data:
            break
        for item in notices_data:
            rows = item.get("row", [])
            all_rows.extend(rows)

    db = SessionLocal()
    try:
        # 기존 데이터 모두 삭제
        db.query(LegislationNotice).delete()
        db.commit()

        save_notices_to_db(db, all_rows)
        print("DB 갱신 완료")
    finally:
        db.close()

if __name__ == "__main__":
    update_legislation_db()
