from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 允許跨域（手機可訪問）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# 掛載靜態檔案
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# 主頁
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("../frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

# 簡單 AI API：文字反轉
@app.get("/predict")
async def predict(text: str):
    return {"output": text[::-1]}
