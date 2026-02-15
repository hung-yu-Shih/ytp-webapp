from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="測試 WebApp")

# 前端資料夾，嘗試掛載，如果沒找到就跳過
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
else:
    print("⚠️ frontend 資料夾不存在，靜態檔案與首頁會 404")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>🎉 WebApp 啟動成功（簡單測試版）</h1>")
