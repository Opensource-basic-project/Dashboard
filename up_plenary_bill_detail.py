from db import SessionLocal, PlenaryBill
import requests
from bs4 import BeautifulSoup
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def crawl_plenary_review_info(soup):
    def extract(table_summary_keyword, 처리일_idx, 처리결과_idx):
        table = soup.find("table", summary=lambda s: s and table_summary_keyword in s)
        if table:
            tr = table.find("tbody").find("tr")
            tds = tr.find_all("td")
            처리일 = tds[처리일_idx].get_text(strip=True) if len(tds) > 처리일_idx else ""
            처리결과 = tds[처리결과_idx].get_text(strip=True) if len(tds) > 처리결과_idx else ""
            return 처리일, 처리결과
        return "", ""

    # 소관위 심사정보: 처리일 = td[3], 처리결과 = td[4]
    so_date, so_result = extract("소관위 심사정보", 3, 4)

    # 법사위 심사정보: 처리일 = td[2], 처리결과 = td[3]
    law_date, law_result = extract("법사위 체계자구심사정보", 2, 3)

    # 본회의 심의정보: 의결일 = td[1], 회의결과 = td[3]
    plenary_date, plenary_result = extract("본회의 심의정보", 1, 3)

    return {
        "so_committee_date": so_date,
        "so_committee_result": so_result,
        "law_committee_date": law_date,
        "law_committee_result": law_result,
        "plenary_vote_date": plenary_date,
        "plenary_vote_result": plenary_result
    }

def crawl_plenary_proposal_text(link_url: str):
    try:
        response = requests.get(link_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # ✅ 제안이유 본문
        summary_div = soup.find("div", id="summaryContentDiv")
        if summary_div:
            raw_text = summary_div.get_text(separator="\n").strip()
            cleaned_lines = [line.lstrip() for line in raw_text.splitlines()]
            cleaned_text = "\n".join(cleaned_lines)
        else:
            cleaned_text = None

        # ✅ 심사 정보 크롤링
        review_info = crawl_plenary_review_info(soup)

        return cleaned_text, review_info

    except Exception as e:
        print(f"[에러] {link_url} 처리 중 오류: {e}")
        return None, {}

def update_plenary_proposal_text():
    db = SessionLocal()
    try:
        targets = db.query(PlenaryBill).filter(
            PlenaryBill.link_url != None
        ).all()

        for bill in targets:
            print(f"[본회의] 📄 {bill.bill_name} - 크롤링 시도 중...")
            detail, review_info = crawl_plenary_proposal_text(bill.link_url)

            if not detail:
                print(f"[본회의] ❌ 1차 실패, 재시도 중...")
                time.sleep(1)
                detail, review_info = crawl_plenary_proposal_text(bill.link_url)

            if detail:
                changed = False
                if bill.proposal_text != detail:
                    bill.proposal_text = detail
                    changed = True

                # ✅ 심사정보 업데이트
                for key, value in review_info.items():
                    if hasattr(bill, key) and getattr(bill, key) != value:
                        setattr(bill, key, value)
                        changed = True

                if changed:
                    print(f"[업데이트] ✏️ {bill.bill_name} - 변경 사항 반영됨")
                else:
                    print(f"[유지] ⏩ {bill.bill_name} - 내용 동일, 덮어쓰기 생략")
            else:
                print(f"[본회의] 🚫 크롤링 실패: {bill.link_url}")

            time.sleep(1)

        db.commit()
        print("[본회의] ✅ 제안이유 및 주요내용 + 심사정보 DB 갱신 완료")

    finally:
        db.close()

if __name__ == "__main__":
    update_plenary_proposal_text()
