from fastapi import APIRouter, HTTPException
import requests

API_KEY = "145bca1e52594533863a5b12ec70dbc9"

router = APIRouter()

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
    if response.status_code == 200:
        return response.json()
    else:
        return None

@router.get("/plenary")
def get_all_plenary_bills(page: int = 1, size: int = 15):
    ages = [20, 21, 22]
    all_bills = []

    for age in ages:
        data = fetch_plenary_bills(age, pIndex=page, pSize=size)
        if data and 'nwbpacrgavhjryiph' in data:
            bills_data = data['nwbpacrgavhjryiph']
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
