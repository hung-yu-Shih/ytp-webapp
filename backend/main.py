from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# 把 frontend 資料夾掛在 /static
app.mount("/static", StaticFiles(directory="../frontend"), name="static")  # ❌ 這會出錯

# 正確寫法：
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
frontend_path = os.path.abspath(frontend_path)

app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_path, "index.html"))
