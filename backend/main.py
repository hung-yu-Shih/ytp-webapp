from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3
from pathlib import Path

# =====================
# FastAPI App
# =====================
app = FastAPI(title="AI 台北行旅工具 API")

# =====================
# CORS (允許手機前端跨域呼叫)
# =====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# =====================
# 靜態前端設定
# =====================
BASE_DIR = Path(__file__).parent.parent  # 從 backend/ 往上一層 app/
frontend_dir = BASE_DIR / "frontend"

# 提供 /static 服務
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# 首頁
@app.get("/", include_in_schema=False)
def root():
    index_file = frontend_dir / "index.html"
    if not index_file.exists():
        return {"error": "index.html 不存在"}
    return FileResponse(index_file)

# =====================
# SQLite 資料庫
# =====================
DB_PATH = Path(__file__).parent / "app.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    # 使用者表
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    # 專案表
    conn.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    conn.commit()
    conn.close()

init_db()

# =====================
# Pydantic Models
# =====================
class AuthData(BaseModel):
    username: str
    password: str

class ProjectData(BaseModel):
    name: str

# =====================
# 使用者登入 / 註冊
# =====================
@app.post("/register")
def register(data: AuthData):
    conn = get_conn()
    try:
        conn.execute("INSERT INTO users(username,password) VALUES (?,?)", (data.username, data.password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="帳號已存在")
    conn.close()
    return {"message":"註冊成功"}

@app.post("/login")
def login(data: AuthData):
    conn = get_conn()
    user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (data.username, data.password)).fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    return {"id": user["id"], "username": user["username"]}

# =====================
# 專案 CRUD
# =====================
@app.get("/projects/{user_id}")
def get_projects(user_id: int):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM projects WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    return [{"id": r["id"], "name": r["name"]} for r in rows]

@app.post("/projects/{user_id}")
def create_project(user_id: int, data: ProjectData):
    conn = get_conn()
    conn.execute("INSERT INTO projects(user_id,name) VALUES (?,?)", (user_id, data.name))
    conn.commit()
    conn.close()
    return {"message":"專案建立成功"}

@app.delete("/projects/{user_id}/{project_id}")
def delete_project(user_id: int, project_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM projects WHERE id=? AND user_id=?", (project_id, user_id))
    conn.commit()
    conn.close()
    return {"message":"專案已刪除"}
