from typing import Union
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from .core.models import JudgeRequest
from .core.judge_engine import judge_code
from .core.docker_executor_v2 import DockerExecutorV2, DockerExecutorRequest
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .core.judge_engine_v2 import judge_code_v2

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
        
@app.post("/v2/judge")
def judge_v2(payload: JudgeRequest):
    try:
        result = judge_code_v2(payload)
        return result 
    except Exception as e:
        print("Tipe error:", type(e).__name__)
        print("Pesan:", e)
        return {"error": str(e)}

@app.get("/health")
def health_check():
    return {"status": "ok"}