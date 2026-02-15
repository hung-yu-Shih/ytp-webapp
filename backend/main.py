from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import requests

app = FastAPI(title="台北 AI 觀光工具")

# 將 frontend 資料夾掛載為 /static
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# 首頁
@app.get("/")
def read_index():
    return FileResponse("../frontend/index.html")

# 範例 API: 抓取台北市資料大平台資料
@app.get("/api/parks")
def get_parks():
    url = "https://data.taipei/api/v1/dataset/29c7b9c5-1f70-4b5e-b5f3-1653d4c0c7b6?scope=resourceAquire"
    r = requests.get(url)
    data = r.json()
    # 取前 10 個景點簡化
    parks = [{"name": p.get("Name", ""), "address": p.get("Address", "")} for p in data.get("result", {}).get("results", [])[:10]]
    return {"parks": parks}
