from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import requests, gzip, csv, io

app = FastAPI(title="臺北市公車 ETA API")

# 允許前端訪問
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 靜態檔案
app.mount("/static", StaticFiles(directory="../frontend"), name="static") 

GZ_URL = "https://tcgbusfs.blob.core.windows.net/blobbus/GetEstimateTime.gz"

def fetch_bus_data():
    resp = requests.get(GZ_URL)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="下載資料失敗")
    gz = gzip.open(io.BytesIO(resp.content), mode='rt', encoding='utf-8')
    reader = csv.DictReader(gz, delimiter='\t')
    data = list(reader)
    return data

@app.get("/")
def home():
    return {"message": "歡迎使用臺北市公車預估到站時間 API"}

@app.get("/bus/{route_id}")
def get_bus_eta(route_id: str):
    data = fetch_bus_data()
    result = []
    for row in data:
        if row["RouteID"] == route_id:
            etime = int(row["EstimateTime"])
            if etime >= 0:
                time_str = f"{etime//60}分{etime%60}秒"
            else:
                time_str = {
                    -1: "尚未發車",
                    -2: "交管不停靠",
                    -3: "末班車已過",
                    -4: "今日未營運"
                }.get(etime, "未知")
            result.append({
                "StopID": row["StopID"],
                "EstimateTime": time_str,
                "GoBack": row["GoBack"]
            })
    if not result:
        raise HTTPException(status_code=404, detail="找不到該路線資料")
    return {"RouteID": route_id, "ETA": result}
