# 🌿 NutriGuide AI — Intelligent Supplement Discovery Platform

A full-stack AI-powered platform for understanding supplements, their ingredients, benefits, and personalized recommendations.

## 🎯 Features

- 🔍 **Smart Search** — Find supplements by name, brand, or category
- 📋 **Detailed Product Pages** — AI-generated summaries, benefits, target audience
- 🧪 **Ingredient Analyzer** — Click any ingredient for AI explanation
- 💬 **RAG Chatbot** — Ask health questions, get evidence-based answers
- 🎯 **Personalized Recommendations** — Questionnaire-based smart suggestions
- 📚 **Knowledge Hub** — Educational content on vitamins, minerals, deficiencies
- ⚖️ **Product Comparison** — Compare nutrition, ingredients, prices

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS + Shadcn UI |
| Backend | FastAPI + Python 3.10+ |
| Database | MongoDB (local via MongoDB Compass) |
| AI | Groq (Llama 3.3) + LangChain + Sentence Transformers |
| Auth | JWT |
| State Management | React Query + Zustand |

## 📦 Quick Start

### Prerequisites

1. **Python 3.10+** installed
2. **Node.js 18+** installed
3. **MongoDB Community Server** installed and running locally
4. **MongoDB Compass** (GUI for MongoDB) — [Download here](https://www.mongodb.com/products/compass)
5. **Groq API Key** (free) — Get from [console.groq.com](https://console.groq.com)

### 🔧 Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env: add your GROQ_API_KEY

# Seed reference data and import the official Amway India catalog
python scripts/seed_database.py

# Or refresh only the product catalog later
python scripts/import_amway_india_products.py

# Run the backend server
uvicorn app.main:app --reload --port 8000
```

Backend will run at: **http://localhost:8000**
API docs: **http://localhost:8000/docs**

### 🎨 Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend will run at: **http://localhost:5173**

### 🗄️ MongoDB Compass Setup

1. Open MongoDB Compass
2. Connect to: `mongodb://localhost:27017`
3. You'll see database: `nutriguide_db`
4. Collections will be auto-created when you run the seed script

## 📁 Project Structure

```
nutriguide-ai/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # API endpoints
│   │   ├── core/             # Config, security
│   │   ├── db/               # MongoDB connection
│   │   ├── models/           # Pydantic models
│   │   ├── schemas/          # Request/response schemas
│   │   ├── services/         # Business logic
│   │   └── ai/               # LLM, RAG, embeddings
│   ├── scripts/              # Seeding & utilities
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Route pages
│   │   ├── hooks/            # Custom hooks
│   │   ├── api/              # API client
│   │   └── types/            # TypeScript types
│   ├── package.json
│   └── vite.config.ts
└── docs/                     # Additional documentation
```

## 🔑 Environment Variables

Create `backend/.env` from `backend/.env.example`:

```
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=nutriguide_db
GROQ_API_KEY=your_groq_api_key_here
JWT_SECRET_KEY=your_random_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:5173,https://amway-india.vercel.app
```

## 🧪 Testing the App

1. Open `http://localhost:5173`
2. Browse imported Amway India products on the home page
3. Click any product to see AI-generated insights
4. Try the chatbot: *"I feel tired all day, what helps?"*
5. Take the recommendation questionnaire
6. Compare two supplements

## ⚠️ Medical Disclaimer

This platform is for **educational purposes only**. It does NOT provide medical advice. Always consult a qualified healthcare professional before starting any supplement regimen.

## 📜 License

MIT License — Free for academic and personal use.

## 👨‍💻 Author

Built as a Final Year Project demonstrating full-stack AI development.
