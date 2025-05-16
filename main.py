from fastapi import FastAPI
from plenary_bills_list import router as plenary_router

app = FastAPI()
app.include_router(plenary_router)
