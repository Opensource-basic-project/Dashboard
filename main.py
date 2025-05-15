from fastapi import FastAPI #fastapi 기본 모듈 임포트 
from bills import router as bills_router    #bills.py에서 만든 라우터를 bills_routuer로 가져옴

app = FastAPI()

app.include_router(bills_router)
