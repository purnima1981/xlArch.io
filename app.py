"""
XlArch.io — Auth + App Server (PostgreSQL)
Run locally: DATABASE_URL=postgresql://... python app.py
"""

import os, hashlib, secrets, uuid, json, ast, tempfile
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import psycopg
from psycopg.rows import dict_row
import uvicorn
import httpx

from engine import (
    compute_layout, new_architecture, SYSTEM_PROMPT, CATALOG,
    get_all_icon_keys, render_png,
)
from renderer import render, commands_to_pptx, commands_to_canvas_js
from templates_ref import TEMPLATES

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# ── DB ────────────────────────────────────────────────
def get_db():
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row, autocommit=True)
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
    if ":" not in stored:
        return False
    salt, h = stored.split(":", 1)
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
        return RedirectResponse("/canvas", status_code=303)
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

@app.get("/app")
async def app_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return RedirectResponse("/canvas", status_code=303)

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

# ── Templates API ─────────────────────────────────────

@app.get("/api/templates")
async def list_templates():
    return {"templates": {k: {"name": v["name"], "description": v["description"]} for k, v in TEMPLATES.items()}}

@app.get("/api/templates/{template_id}")
async def get_template(template_id: str):
    t = TEMPLATES.get(template_id)
    if not t:
        return JSONResponse({"error": "Template not found"}, status_code=404)
    arch = dict(t["data"])
    render_result = render(arch)
    merged = render_result["architecture"]
    merged["positions"] = render_result["positions"]
    return {"architecture": merged, "renderCommands": render_result["commands"]}

# ── Canvas Page ───────────────────────────────────────

@app.get("/canvas", response_class=HTMLResponse)
async def canvas_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("canvas.html", {
        "request": request, "user": user, "catalog": CATALOG,
    })

# ── Generate Architecture (Claude API) ────────────────

@app.post("/api/generate")
async def generate(request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    body = await request.json()
    prompt = body.get("prompt", "")
    if not prompt.strip():
        return JSONResponse({"error": "Prompt required"}, status_code=400)

    if not ANTHROPIC_API_KEY:
        return JSONResponse({"error": "ANTHROPIC_API_KEY not configured"}, status_code=500)

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post("https://api.anthropic.com/v1/messages", headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }, json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4000,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}],
        })

    if resp.status_code != 200:
        return JSONResponse({"error": f"Claude API error: {resp.status_code}"}, status_code=502)

    data = resp.json()
    raw = "".join(c.get("text", "") for c in data.get("content", []))

    # Parse the Python dict
    raw = raw.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()

    try:
        architecture = ast.literal_eval(raw)
    except Exception:
        try:
            architecture = json.loads(raw)
        except Exception:
            return JSONResponse({"error": "Failed to parse architecture", "raw": raw[:500]}, status_code=422)

    # Render — ONE function, used by canvas AND pptx
    render_result = render(architecture)
    merged = render_result["architecture"]
    merged["positions"] = render_result["positions"]

    return {"architecture": merged, "renderCommands": render_result["commands"]}

# ── Update Positions (from canvas drag) ───────────────

@app.post("/api/update-positions")
async def update_positions(request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    body = await request.json()
    return {"ok": True}

# ── Re-render (after node/edge changes) ───────────────

@app.post("/api/rerender")
async def rerender(request: Request):
    body = await request.json()
    arch = body.get("architecture")
    if not arch:
        return JSONResponse({"error": "No architecture"}, status_code=400)
    render_result = render(arch)
    merged = render_result["architecture"]
    merged["positions"] = render_result["positions"]
    return {"architecture": merged, "renderCommands": render_result["commands"], "positions": render_result["positions"]}

# ── Export PPTX ───────────────────────────────────────

@app.post("/api/export/pptx")
async def export_pptx(request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    body = await request.json()
    arch = body.get("architecture")
    if not arch:
        return JSONResponse({"error": "No architecture"}, status_code=400)

    path = os.path.join(tempfile.gettempdir(), f"xlarch_{uuid.uuid4().hex[:8]}.pptx")
    try:
        render_result = render(arch)
        commands_to_pptx(render_result, path)
        return FileResponse(path, filename="xlarch_architecture.pptx",
                          media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ── Export PNG ────────────────────────────────────────

@app.post("/api/export/png")
async def export_png(request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    body = await request.json()
    arch = body.get("architecture")
    if not arch:
        return JSONResponse({"error": "No architecture"}, status_code=400)

    path = os.path.join(tempfile.gettempdir(), f"xlarch_{uuid.uuid4().hex[:8]}")
    try:
        result = render_png(arch, path)
        if result and os.path.exists(result):
            return FileResponse(result, filename="xlarch_architecture.png", media_type="image/png")
        return JSONResponse({"error": "PNG rendering failed"}, status_code=500)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ── Save / Load Architecture ──────────────────────────

@app.post("/api/save")
async def save_arch(request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    body = await request.json()
    arch = body.get("architecture")
    if not arch:
        return JSONResponse({"error": "No architecture"}, status_code=400)

    arch_id = body.get("id") or str(uuid.uuid4())
    title = arch.get("title", "Untitled")

    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO architectures (id, user_id, title, data)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET title = %s, data = %s, updated_at = NOW()
    """, (arch_id, user["id"], title, json.dumps(arch), title, json.dumps(arch)))
    cur.close(); db.close()

    return {"id": arch_id, "saved": True}

@app.get("/api/architectures")
async def list_archs(request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT id, title, created_at, updated_at FROM architectures
        WHERE user_id = %s ORDER BY updated_at DESC
    """, (user["id"],))
    rows = cur.fetchall()
    cur.close(); db.close()

    return {"architectures": [dict(r) for r in rows]}

@app.get("/api/architectures/{arch_id}")
async def get_arch(arch_id: str, request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM architectures WHERE id = %s AND user_id = %s", (arch_id, user["id"]))
    row = cur.fetchone()
    cur.close(); db.close()

    if not row:
        return JSONResponse({"error": "Not found"}, status_code=404)

    arch = row["data"] if isinstance(row["data"], dict) else json.loads(row["data"])
    render_result = render(arch)
    merged = render_result["architecture"]
    merged["positions"] = render_result["positions"]
    return {"architecture": merged, "renderCommands": render_result["commands"]}

# ── Run ───────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
