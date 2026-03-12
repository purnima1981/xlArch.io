# XlArch.io

The intelligent architecture platform.

## Deploy to Railway

1. Create a new project on [railway.app](https://railway.app)
2. Add a **PostgreSQL** database (click "+ New" → "Database" → "PostgreSQL")
3. Add a **GitHub repo** service (click "+ New" → "GitHub Repo" → select this repo)
4. Railway auto-links the `DATABASE_URL` env var from Postgres to your app
5. Deploy. That's it.

The app auto-creates tables on first boot.

## Local Development

```bash
# Set your Postgres connection string
export DATABASE_URL="postgresql://user:pass@localhost:5432/xlarch"

# Install deps
pip install -r requirements.txt

# Run
python app.py
# Open http://localhost:8000
```

## Project Structure

```
xlarch/
├── app.py              ← FastAPI server + auth
├── templates/
│   ├── landing.html    ← Home page
│   ├── auth.html       ← Login / Signup / Reset
│   └── dashboard.html  ← App (post-login)
├── static/
│   └── logo.svg        ← XlArch logo
├── requirements.txt
├── Procfile
└── railway.toml
```
