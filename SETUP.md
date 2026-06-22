# 🚀 NutriGuide AI — Complete Setup Guide

This guide walks you through running the project on your local machine using **MongoDB Compass**.

---

## ✅ Prerequisites Checklist

Install these BEFORE starting:

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.10+ | https://www.python.org/downloads/ |
| Node.js | 18+ | https://nodejs.org |
| MongoDB Community Server | 6.0+ | https://www.mongodb.com/try/download/community |
| MongoDB Compass | Latest | https://www.mongodb.com/products/compass |
| Groq API Key (FREE) | — | https://console.groq.com |

> 💡 **MongoDB Compass** is the GUI to view your database. **MongoDB Community Server** is the actual database engine. You need BOTH.

---

## 🗄️ STEP 1: Start MongoDB Locally

### Windows
1. After installing MongoDB Community Server, it usually runs as a **Windows Service** automatically.
2. Open **Services** (`services.msc`) and verify `MongoDB` is running.
3. If not running: Right-click → Start.

### macOS (via Homebrew)
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

### Linux (Ubuntu)
```bash
sudo systemctl start mongod
sudo systemctl enable mongod
```

### ✅ Verify MongoDB is running
1. Open **MongoDB Compass**.
2. In the connection field, paste: `mongodb://localhost:27017`
3. Click **Connect**.
4. You should see the MongoDB dashboard with system databases (`admin`, `config`, `local`).

---

## 🔧 STEP 2: Backend Setup

Open a terminal in the project root:

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies (takes 2-3 minutes)
pip install -r requirements.txt
```

### Configure environment

```bash
# Copy the template
# Windows:
copy .env.example .env
# macOS / Linux:
cp .env.example .env
```

Open `.env` in any text editor and update:

```
GROQ_API_KEY=gsk_YOUR_ACTUAL_KEY_HERE
```

> 🔑 **Get a free Groq API key**: Sign up at [console.groq.com](https://console.groq.com) → API Keys → Create Key

### Seed the database

```bash
python scripts/seed_database.py
```

Expected output:
```
✅ Connected to database: nutriguide_db
📦 Inserting 15 ingredients...
🏢 Inserting 10 brands...
⚠️  Inserting 6 deficiencies...
💊 Inserting 12 products...
✅ DATABASE SEEDED SUCCESSFULLY
```

Now in **MongoDB Compass**, click the refresh button — you'll see a new database `nutriguide_db` with collections!

### Start the backend

```bash
uvicorn app.main:app --reload --port 8000
```

✅ Backend running at: **http://localhost:8000**
📖 Interactive API docs: **http://localhost:8000/docs**

---

## 🎨 STEP 3: Frontend Setup

Open a **second terminal** (keep the backend running):

```bash
cd frontend

# Install dependencies (takes 1-2 minutes)
npm install

# Start dev server
npm run dev
```

✅ Frontend running at: **http://localhost:5173**

Open this URL in your browser! 🎉

---

## 🧪 STEP 4: Try the App

1. **Home Page** — Browse featured products and health goal categories
2. **Click any product** — See AI-generated summary, ingredient analysis
3. **Click an ingredient's "Explain" button** — Get an AI-powered breakdown
4. **AI Assistant** — Ask: *"I feel tired all day, what supplements help?"*
5. **For You** — Take the 5-step quiz for personalized recommendations
6. **Knowledge** — Learn about vitamins, minerals, and deficiencies

---

## 🗂️ STEP 5: Explore the Database in MongoDB Compass

1. Open MongoDB Compass
2. Connect to `mongodb://localhost:27017`
3. Click `nutriguide_db`
4. You'll see collections:
   - `products` (12 docs) — supplement catalog
   - `ingredients` (15 docs) — vitamins, minerals, herbs
   - `brands` (10 docs)
   - `deficiencies` (6 docs)
   - `users` (auto-created on registration)
   - `chat_history` (auto-created on chat use)

You can edit, add, or delete documents directly from Compass!

---

## 🐛 Troubleshooting

### "MongoDB connection failed"
- ✅ Open MongoDB Compass and verify connection to `mongodb://localhost:27017` works
- ✅ On Windows, check Services for "MongoDB" — must be Running
- ✅ Try: `mongosh` in terminal to confirm DB is up

### "GROQ_API_KEY not configured"
- The app still works! It returns mock AI responses
- For real AI: get a free key at https://console.groq.com → add to `.env`

### Port 8000 or 5173 already in use
- Backend: `uvicorn app.main:app --reload --port 8001`
- Frontend: edit `vite.config.ts` → change port

### `pip install` fails on Windows
- You may need: `pip install --upgrade pip setuptools wheel`
- For bcrypt issues: `pip install bcrypt==4.0.1`

### `npm install` fails
- Delete `node_modules` and `package-lock.json`, then `npm install` again
- Try `npm install --legacy-peer-deps`

---

## 📚 What's Next?

- **Add more products**: Edit `backend/scripts/seed_database.py` and re-run it
- **Customize prompts**: Edit `backend/app/ai/prompts.py`
- **Add new features**: The codebase is well-structured for extension
- **Deploy**: Frontend to Vercel, Backend to Railway, MongoDB to Atlas

---

## 📋 Quick Command Reference

```bash
# Backend (in backend/ folder)
source venv/bin/activate         # activate venv (Linux/Mac)
venv\Scripts\activate            # activate venv (Windows)
uvicorn app.main:app --reload    # run server
python scripts/seed_database.py  # reseed database

# Frontend (in frontend/ folder)
npm run dev          # dev server
npm run build        # production build
npm run preview      # preview build
```

---

## 🎓 Project Architecture Diagram

```
┌──────────────────────────────────────────────────┐
│  Browser (http://localhost:5173)                 │
│  React + Vite + Tailwind                         │
└────────────────┬─────────────────────────────────┘
                 │ HTTP / JSON
                 ▼
┌──────────────────────────────────────────────────┐
│  FastAPI Backend (http://localhost:8000)         │
│  ┌────────────────────────────────────────────┐  │
│  │ Routes: products, chat, recommendations,   │  │
│  │         ingredients, knowledge, auth       │  │
│  └────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────┐  │
│  │ AI Layer:                                  │  │
│  │  - Groq LLM (Llama 3.3 70B)                │  │
│  │  - RAG retrieval                           │  │
│  │  - Recommendation engine                   │  │
│  └────────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────────┘
                 │ Motor (async driver)
                 ▼
┌──────────────────────────────────────────────────┐
│  MongoDB (mongodb://localhost:27017)             │
│  Database: nutriguide_db                         │
│  Viewable in MongoDB Compass                     │
└──────────────────────────────────────────────────┘
```

Happy coding! 🚀
