# 로직 : 실제 데이터 요청/처리 함수
# api 에 실제로 요청을 보내고, 받은 데이터를 처리하는 함수들을 담는 곳

import requests #http 요청을 위해 requests 라이브러리 불러오기

API_KEY = "145bca1e52594533863a5b12ec70dbc9"

def fetch_plenary_bills(age: int, pIndex: int = 1, pSize: int = 10):    #본회의 법안 목록을 가져오는 함수를 정의 
    url = "https://open.assembly.go.kr/portal/openapi/nwbpacrgavhjryiph"
    params = {
        'KEY': API_KEY,
        'Type': 'json',
        'AGE': age,
        'pIndex': pIndex,
        'pSize': pSize
    }
    response = requests.get(url, params=params) #requests.get으로 api 에 get 요청을 보냄, params가 쿼리스트링으로 붙음 
    if response.status_code == 200: #응답이 성공(http 200) 이면? 
        return response.json()  #json 형식으로 변환하여 데이터 반환
    else:
        return None  # 실패하면 None 반환
