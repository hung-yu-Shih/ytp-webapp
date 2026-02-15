from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import requests, gzip, csv, io
from pathlib import Path

app = FastAPI(title="臺北市公車 ETA API")

# 允許前端訪問
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 靜態檔案
BASE_DIR = Path(__file__).resolve().parent.parent
frontend_dir = BASE_DIR / "frontend"

if not frontend_dir.exists():
    raise RuntimeError(f"找不到資料夾: {frontend_dir}")

app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# 首頁
@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_file = frontend_dir / "index.html"
    if not index_file.exists():
        return HTMLResponse(content="<h1>index.html 不存在</h1>", status_code=404)
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))

# 公車資料 URL
GZ_URL = "https://tcgbusfs.blob.core.windows.net/blobbus/GetEstimateTime.gz"

def fetch_bus_data():
    """下載並解析公車預估到站資料"""
    resp = requests.get(GZ_URL)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="下載資料失敗")
    
    gz = gzip.open(io.BytesIO(resp.content), mode='rt', encoding='utf-8')
    reader = csv.DictReader(gz, delimiter='\t')
    data = list(reader)
    return data

# API 範例首頁
@app.get("/api")
def api_home():
    return {"message": "歡迎使用臺北市公車預估到站時間 API"}

# 公車 ETA 查詢
@app.get("/api/bus/{route_id}")
def get_bus_eta(route_id: str):
    data = fetch_bus_data()
    result = []

    for row in data:
        if str(row["RouteID"]) == str(route_id):  # RouteID 是數字，轉字串比對
            etime_str = row["EstimateTime"]
            # 特殊代碼對應文字
            if etime_str in ["-1", "-2", "-3", "-4"]:
                time_str = {
                    "-1": "尚未發車",
                    "-2": "交管不停靠",
                    "-3": "末班車已過",
                    "-4": "今日未營運"
                }[etime_str]
            else:
                try:
                    etime = int(etime_str)
                    time_str = f"{etime//60}分{etime%60}秒"
                except:
                    time_str = "未知"

            result.append({
                "StopID": row["StopID"],
                "EstimateTime": time_str,
                "GoBack": row["GoBack"]
            })

    if not result:
        raise HTTPException(status_code=404, detail=f"找不到路線 {route_id} 的資料")

    return {"RouteID": route_id, "ETA": result}
