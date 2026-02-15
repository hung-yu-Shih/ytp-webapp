from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import requests
from sentence_transformers import SentenceTransformer, util

app = FastAPI()

# 前端靜態檔
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# NLP 模型（中文語意向量）
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# 台北市觀光資料 JSON API
TAIPEI_SPOTS_API = "https://data.taipei/opendata/datalist/apiAccess?scope=resourceAquire&rid=xxxx-xxxx"  # 改成實際 RID

# 抓取資料
spots_cache = []
def fetch_spots():
    global spots_cache
    if spots_cache:
        return spots_cache
    res = requests.get(TAIPEI_SPOTS_API)
    data = res.json()
    # 假設每筆資料有 name, description
    spots_cache = [{"name": item["Name"], "desc": item["Description"]} for item in data["result"]["results"]]
    return spots_cache

@app.get("/predict")
def predict(text: str):
    user_vec = model.encode(text, convert_to_tensor=True)
    results = []
    for spot in fetch_spots():
        spot_vec = model.encode(spot["desc"], convert_to_tensor=True)
        score = util.cos_sim(user_vec, spot_vec).item()
        results.append({"name": spot["name"], "desc": spot["desc"], "score": score})
    # 依相似度排序
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return results[:5]  # 回傳前5名
