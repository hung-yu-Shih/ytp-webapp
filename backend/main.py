from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# backend/main.py 的目錄
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# frontend 絕對路徑
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")
FRONTEND_DIR = os.path.abspath(FRONTEND_DIR)

# 掛載 static
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# 根路由
@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
