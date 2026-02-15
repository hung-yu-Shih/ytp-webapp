from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

app = FastAPI()

# 允許跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 回傳首頁
@app.get("/")
async def root():
    return FileResponse("../frontend/index.html")

# 簡單文字反轉 API
@app.get("/predict")
async def predict(text: str):
    return {"output": text[::-1]}

# 靜態檔案
from fastapi.staticfiles import StaticFiles
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")
