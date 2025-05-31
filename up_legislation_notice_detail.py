from db import SessionLocal, LegislationNotice
import requests
from bs4 import BeautifulSoup
import re

def crawl_proposal_detail(link_url: str):
    try:
        response = requests.get(link_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for item in soup.find_all("div", class_="item"):
            h4 = item.find("h4")
            if h4 and "제안이유 및 주요내용" in h4.text:
                desc_div = item.find("div", class_="desc")
                if desc_div:
                    return re.sub(r'^[ \t]+', '', desc_div.get_text(separator="\n").strip(), flags=re.MULTILINE)
    except Exception as e:
        print(f"[에러] {link_url} 처리 중 오류: {e}")
    return None

def update_proposal_text():
    db = SessionLocal()
    try:
        targets = db.query(LegislationNotice).filter(
            (LegislationNotice.proposal_text == None) | 
            (LegislationNotice.proposal_text == "")
        ).all()

        for bill in targets:
            if bill.link_url:
                print(f"📄 {bill.bill_name} - 크롤링 중...")
                detail = crawl_proposal_detail(bill.link_url)
                if detail:
                    bill.proposal_text = detail
        db.commit()
        print("✅ 제안이유 및 주요내용 DB 갱신 완료")
    finally:
        db.close()

if __name__ == "__main__":
    update_proposal_text()
