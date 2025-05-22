from fastapi import FastAPI

from plenary_bills_list import router as plenary_router
from plenary_bills_detail import router as plenary_detail_router
from legislation_notice_ongoing_list import router as notice_list_router
from legislation_notice_ended_list import router as notice_list_ended_router
#from legislation_notice_ongoing_detail import router as notice_detail_router

app = FastAPI()

app.include_router(plenary_router)
app.include_router(plenary_detail_router)
app.include_router(notice_list_router)
app.include_router(notice_list_ended_router)
#app.include_router(notice_detail_router)

#가상환경 활성화 : .\venv\Scripts\Activate.ps1
#서버 실행 : uvicorn main:app --reload

