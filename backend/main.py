from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="測試 WebApp")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return HTMLResponse("<h1>🎉 WebApp 啟動成功！</h1>")
