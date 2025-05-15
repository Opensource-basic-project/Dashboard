# 라우터 : url 경로 정의
# fastapi에서 url 라우팅을 담당하는 파일 

from fastapi import APIRouter, HTTPException    #fastapi의 라우터기능과 http 예외처리 클래스 임포트 
from bills_service import fetch_plenary_bills   #bills.py에서 만들었던 fetch_plenary_bills 함수 가져옴

router = APIRouter()    #라우터 인스턴스 생성 

@router.get("/plenary") #http get 요청으로 /plenary 경로에 접속한다면? 아래 함수 실행 
def get_all_plenary_bills(page: int=1, size: int =15):
    ages = [20, 21, 22]
    all_bills = []

    for age in ages:
        data = fetch_plenary_bills(age, pIndex=page, pSize = size)
        if data and 'nwbpacrgavhjryiph' in data:
            bills_data = data['nwbpacrgavhjryiph']  #실제 법안 데이터가 들어있는 부분 추출 

            # bills_data는 리스트인데, 리스트 안에 head, row 두 딕셔너리가 있음
            # row만 추출해서 추가해야 함
            for element in bills_data:
                if 'row' in element:
                    for bill in element['row']:
                        simplified_bill = {
                            "PROPOSE_DT": bill.get("PROPOSE_DT"),
                            "BILL_NM": bill.get("BILL_NM"),
                            "COMMITTEE_NM": bill.get("COMMITTEE_NM"),
                            "PROC_RESULT_CD": bill.get("PROC_RESULT_CD"),
                            "PROPOSER": bill.get("PROPOSER"),
                        }
                        all_bills.append(simplified_bill)


        else:
            raise HTTPException(status_code=500, detail=f"Failed to get data for age {age}")

    return {"results": all_bills}


