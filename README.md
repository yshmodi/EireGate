# EireGate 🌉

AI-powered job matching platform that analyzes resumes and finds the best-fit jobs globally with smart match scores.

## Features
- 📄 **Resume Parsing** — Upload PDF, AI extracts skills, experience, education
- 🔍 **Job Search** — Scrape LinkedIn, Indeed, Glassdoor for real jobs
- 🎯 **Match Scoring** — Skill alignment scoring (0-100%)
- ✨ **Resume Tailoring** — AI rewrites resume for specific job descriptions
- 🔄 **Multi-LLM Router** — Automatic fallback between Gemini, OpenRouter, Mistral, HuggingFace

## Tech Stack
| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Python 3.11, Pydantic |
| LLM | Multi-router (Gemini, OpenRouter, Mistral, HuggingFace) |
| Agents | LangGraph with Supabase checkpointer |
| Job Scraping | JobSpy (LinkedIn, Indeed, Glassdoor) |
| Cache | Redis (2-hour TTL) |
| Database | Supabase (PostgreSQL) |

## Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/eiregate.git
cd eiregate
conda activate eiregate  # or: python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
```

Required keys:
- `GOOGLE_API_KEY` — [Get from Google AI Studio](https://aistudio.google.com/apikey)
- `DATABASE_URL` — Supabase PostgreSQL connection string
- `REDIS_URL` — Redis connection (default: `redis://localhost:6379/0`)

Optional (for fallback):
- `OPENROUTER_API_KEY` — [Get from OpenRouter](https://openrouter.ai/keys)
- `MISTRAL_API_KEY` — [Get from Mistral](https://console.mistral.ai/api-keys)
- `HUGGINGFACE_API_KEY` — [Get from HuggingFace](https://huggingface.co/settings/tokens)

### 3. Run the API
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Health Checks
```
GET /health              # Basic health check
GET /health/llm          # LLM provider status
GET /health/llm/test     # Test all LLM providers
```

### Resume
```
POST /api/v1/resume/upload    # Upload & parse PDF
POST /api/v1/resume/tailor    # Tailor for specific job
POST /api/v1/resume/process   # Full pipeline
```

### Jobs
```
GET /api/v1/jobs/search       # Search jobs (LinkedIn, Indeed, Glassdoor)
GET /api/v1/jobs/{job_id}     # Get single job by ID
```

## Project Structure
```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── agents/              # LangGraph workflows
│   ├── api/v1/              # API routes
│   ├── core/                # LLM router, cache, config
│   ├── models/              # Pydantic models
│   └── services/            # Business logic
├── .env                     # Environment variables
└── requirements.txt         # Dependencies
```

## Development

See [TECHNICAL_PLAN.md](TECHNICAL_PLAN.md) for detailed progress tracking.

### Testing LLM Providers
```bash
# Test all providers
curl http://localhost:8000/health/llm/test

# Test specific provider
curl http://localhost:8000/health/llm/test/Gemini
```

### Current Status
- ✅ Backend API complete
- ✅ Multi-LLM routing with fallback
- ✅ Job search & caching
- 🚧 Database schema (next)
- 🚧 Supabase Auth (next)
- 🚧 Frontend (Next.js)

## License
MIT
