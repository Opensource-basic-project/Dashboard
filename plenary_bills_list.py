# 본회의 처리 법안 목록 기능 
from fastapi import APIRouter, HTTPException
import requests

API_KEY = "145bca1e52594533863a5b12ec70dbc9"

router = APIRouter()    #API 경로들을 담을 라우터 객체 생성 

#국회 본회의 처리 법안 데이터를 외부 API에서 가져오는 함수  
def fetch_plenary_bills(age: int, pIndex: int = 1, pSize: int = 10):     
    url = "https://open.assembly.go.kr/portal/openapi/nwbpacrgavhjryiph"
    params = {
        'KEY': API_KEY,
        'Type': 'json',
        'AGE': age,
        'pIndex': pIndex,
        'pSize': pSize
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:     #성공적으로 응답이 오면 JSON 반환 실패하면 None 반환 
        return response.json()
    else:
        return None

# API 경로 /plenary 정의 
@router.get("/plenary")
# HTTP GET 요청이 /plenary 경로로 들어오면 이 함수를 실행함 
def get_all_plenary_bills(page: int = 1, size: int = 15):
    ages = [20, 21, 22]
    all_bills = []

    for age in ages:
        pIndex = 1
        while True:
            data = fetch_plenary_bills(age, pIndex=pIndex, pSize=100)
            if data and 'nwbpacrgavhjryiph' in data:
                bills_data = data['nwbpacrgavhjryiph']

                # 종료 조건: bills_data가 없거나 row가 비어 있으면 중단
                if not bills_data or all('row' not in elem or not elem['row'] for elem in bills_data):
                    break

                for element in bills_data:
                    if 'row' in element:
                        for bill in element['row']:
                            simplified_bill = {
                                "AGE": age,
                                "PROPOSE_DT": bill.get("PROPOSE_DT"),
                                "BILL_NM": bill.get("BILL_NM"),
                                "COMMITTEE_NM": bill.get("COMMITTEE_NM"),
                                "PROC_RESULT_CD": bill.get("PROC_RESULT_CD"),
                                "PROPOSER": bill.get("PROPOSER"),
                            }
                            all_bills.append(simplified_bill)
                pIndex += 1  # 다음 페이지
            else:
                break  # 실패했거나 더 이상 데이터 없음

    # 정렬 및 페이지네이션
    all_bills.sort(key=lambda x: x.get("PROPOSE_DT", ""), reverse=True)
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_bills = all_bills[start_idx:end_idx]

    return {
        "total_count": len(all_bills),
        "page": page,
        "size": size,
        "results": paginated_bills
    }
