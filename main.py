from typing import Union
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from .core.models import JudgeRequest
from .core.judge_engine import judge_code
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import uuid
import subprocess # untuk menjalankan perintah sistem

origins = [
    'http://localhost',
    'http://localhost:3000'
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": {}})


@app.post("/judge")
def judge(payload: JudgeRequest):
    try:
        result = judge_code(payload)
        return result
    except Exception as e:
        print("Tipe error:", type(e).__name__)
        print("Pesan:", e)
        return {"error": str(e)}
        
@app.get("/health")
def health_check():
    return {"status": "ok"}