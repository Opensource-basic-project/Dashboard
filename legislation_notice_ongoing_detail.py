from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
import requests
from bs4 import BeautifulSoup
import re

router = APIRouter()
templates = Jinja2Templates(directory="templates")

API_KEY = "145bca1e52594533863a5b12ec70dbc9"

# bill_id로 API 여러 페이지 탐색하면서 LINK_URL과 bill 데이터 가져오기
def get_link_url_from_api(bill_id: str, age=22, max_pages=5):
    url = "https://open.assembly.go.kr/portal/openapi/nknalejkafmvgzmpt"
    for pIndex in range(1, max_pages + 1):
        params = {
            'KEY': API_KEY,
            'Type': 'json',
            'AGE': age,
            'pSize': 100,
            'pIndex': pIndex,
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if 'nknalejkafmvgzmpt' in data and isinstance(data['nknalejkafmvgzmpt'], list):
                bills_data = data['nknalejkafmvgzmpt'][1].get('row', [])
                for bill in bills_data:
                    if str(bill.get('BILL_ID')).strip() == str(bill_id).strip():
                        return bill.get('LINK_URL'), bill
        except Exception as e:
            print(f"API 호출 에러: {e}")
            break
    return None, None

# LINK_URL 페이지 크롤링해서 제안 이유 및 주요내용 추출
def crawl_proposal_detail(link_url: str):
    try:
        response = requests.get(link_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # '제안이유 및 주요내용' 항목의 텍스트가 담긴 div.desc 태그 찾기
        item_divs = soup.find_all("div", class_="item")
        for item in item_divs:
            h4 = item.find("h4")
            if h4 and "제안이유 및 주요내용" in h4.text:
                desc_div = item.find("div", class_="desc")
                if desc_div:
                    text = desc_div.get_text(separator="\n").strip()
                    
                    text = re.sub(r'^[ \t]+', '', text, flags=re.MULTILINE)
                    return text
    except Exception as e:
        print(f"크롤링 에러: {e}")
    return "제안이유 및 주요내용을 불러올 수 없습니다."


@router.get("/legislation_ongoing/{bill_id}")
def plenary_bills_detail(request: Request, bill_id: str):
    link_url, bill = get_link_url_from_api(bill_id)
    if not link_url:
        raise HTTPException(status_code=404, detail="해당 bill_id에 대한 LINK_URL을 찾을 수 없습니다.")

    proposal_text = crawl_proposal_detail(link_url) or "제안이유 및 주요내용을 불러올 수 없습니다."

    return templates.TemplateResponse("legislation_notice_ongoing_detail.html", {
        "request": request,
        "bill": bill,
        "proposal_text": proposal_text,
        "link_url": link_url
    })
