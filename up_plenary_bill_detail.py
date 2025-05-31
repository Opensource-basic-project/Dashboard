from db import SessionLocal, PlenaryBill
import requests
from bs4 import BeautifulSoup
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def crawl_plenary_proposal_text(link_url: str):
    try:
        response = requests.get(link_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        summary_div = soup.find("div", id="summaryContentDiv")
        if summary_div:
            return summary_div.get_text(separator="\n").strip()
    except Exception as e:
        print(f"[에러] {link_url} 처리 중 오류: {e}")
    return None

def update_plenary_proposal_text():
    db = SessionLocal()
    try:
        targets = db.query(PlenaryBill).filter(
            (PlenaryBill.proposal_text == None) |
            (PlenaryBill.proposal_text == "")
        ).all()

        for bill in targets:
            if bill.link_url:
                print(f"[본회의] 📄 {bill.bill_name} - 크롤링 시도 중...")
                detail = crawl_plenary_proposal_text(bill.link_url)
                if not detail:
                    print(f"[본회의] ❌ 1차 실패, 재시도 중...")
                    time.sleep(1)
                    detail = crawl_plenary_proposal_text(bill.link_url)
                if detail:
                    bill.proposal_text = detail
                else:
                    print(f"[본회의] 🚫 크롤링 실패: {bill.link_url}")
                time.sleep(1)
        db.commit()
        print("[본회의] ✅ 제안이유 및 주요내용 DB 갱신 완료")
    finally:
        db.close()

if __name__ == "__main__":
    update_plenary_proposal_text()
