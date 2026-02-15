import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 專案根目錄
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = FastAPI()

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def read_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


# 範例 API: 抓取台北市資料大平台資料
@app.get("/api/parks")
def get_parks():
    url = "https://data.taipei/api/v1/dataset/29c7b9c5-1f70-4b5e-b5f3-1653d4c0c7b6?scope=resourceAquire"
    r = requests.get(url)
    data = r.json()
    # 取前 10 個景點簡化
    parks = [{"name": p.get("Name", ""), "address": p.get("Address", "")} for p in data.get("result", {}).get("results", [])[:10]]
    return {"parks": parks}
