"""
XlArch.io — Auth + App Server (PostgreSQL)
Run locally: DATABASE_URL=postgresql://... python app.py
"""

import os, hashlib, secrets, uuid
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import psycopg2
from psycopg2.extras import RealDictCursor
import uvicorn

DATABASE_URL = os.environ.get("DATABASE_URL", "")

# ── DB ────────────────────────────────────────────────
def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    conn.autocommit = True
    return conn

def init_db():
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id),
            expires_at TIMESTAMPTZ NOT NULL
        );
        CREATE TABLE IF NOT EXISTS architectures (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id),
            title TEXT NOT NULL,
            data JSONB NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    cur.close()
    db.close()

# ── Password hashing ─────────────────────────────────
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return f"{salt}:{h.hex()}"

def verify_password(password: str, stored: str) -> bool:
    salt, h = stored.split(":")
    check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return check.hex() == h

# ── Sessions ──────────────────────────────────────────
SESSION_COOKIE = "xlarch_session"
SESSION_HOURS = 72

def create_session(user_id: str) -> str:
    token = secrets.token_urlsafe(48)
    expires = datetime.utcnow() + timedelta(hours=SESSION_HOURS)
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO sessions (token, user_id, expires_at) VALUES (%s, %s, %s)",
                (token, user_id, expires))
    cur.close()
    db.close()
    return token

def get_current_user(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT u.id, u.email, u.name FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.token = %s AND s.expires_at > NOW()
    """, (token,))
    row = cur.fetchone()
    cur.close()
    db.close()
    return dict(row) if row else None

# ── App ───────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app = FastAPI(title="XlArch.io", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ── Routes: Pages ─────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse("/app", status_code=303)
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse("/app", status_code=303)
    return templates.TemplateResponse("auth.html", {"request": request, "mode": "login", "error": None})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse("/app", status_code=303)
    return templates.TemplateResponse("auth.html", {"request": request, "mode": "signup", "error": None})

@app.get("/reset", response_class=HTMLResponse)
async def reset_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request, "mode": "reset", "error": None, "success": None})

@app.get("/app", response_class=HTMLResponse)
async def app_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

# ── Routes: Auth Actions ──────────────────────────────

@app.post("/auth/signup")
async def do_signup(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    email = email.lower().strip()
    if len(password) < 6:
        return templates.TemplateResponse("auth.html", {
            "request": request, "mode": "signup", "error": "Password must be at least 6 characters"
        })
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cur.fetchone():
        cur.close(); db.close()
        return templates.TemplateResponse("auth.html", {
            "request": request, "mode": "signup", "error": "Email already registered"
        })
    user_id = str(uuid.uuid4())
    cur.execute("INSERT INTO users (id, email, name, password_hash) VALUES (%s, %s, %s, %s)",
                (user_id, email, name.strip(), hash_password(password)))
    cur.close(); db.close()

    token = create_session(user_id)
    response = RedirectResponse("/app", status_code=303)
    response.set_cookie(SESSION_COOKIE, token, max_age=SESSION_HOURS * 3600, httponly=True, samesite="lax")
    return response

@app.post("/auth/login")
async def do_login(request: Request, email: str = Form(...), password: str = Form(...)):
    email = email.lower().strip()
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close(); db.close()

    if not user or not verify_password(password, user["password_hash"]):
        return templates.TemplateResponse("auth.html", {
            "request": request, "mode": "login", "error": "Invalid email or password"
        })

    token = create_session(user["id"])
    response = RedirectResponse("/app", status_code=303)
    response.set_cookie(SESSION_COOKIE, token, max_age=SESSION_HOURS * 3600, httponly=True, samesite="lax")
    return response

@app.post("/auth/reset")
async def do_reset(request: Request, email: str = Form(...)):
    # TODO: Send actual reset email
    return templates.TemplateResponse("auth.html", {
        "request": request, "mode": "reset", "error": None,
        "success": f"If {email} exists, a reset link has been sent."
    })

@app.get("/auth/logout")
async def logout(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        db = get_db()
        cur = db.cursor()
        cur.execute("DELETE FROM sessions WHERE token = %s", (token,))
        cur.close(); db.close()
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response

# ── API ───────────────────────────────────────────────

@app.get("/api/me")
async def me(request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    return {"user": user}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}

# ── Run ───────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
