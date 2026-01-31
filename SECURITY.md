# Security Policy

## Reporting a Vulnerability
Please email yashmodi.ie@gmail.com with details. Do not open a public issue for security bugs.

## Sensitive Data
- Never commit `.env` or API keys
- Use `.env.example` for templates
- All secrets should be loaded from environment variables

## API Keys Required
- `GOOGLE_API_KEY` - Google Gemini
- `OPENROUTER_API_KEY` - OpenRouter
- `MISTRAL_API_KEY` - Mistral AI
- `HUGGINGFACE_API_KEY` - HuggingFace
- `DATABASE_URL` - Supabase PostgreSQL
- `REDIS_URL` - Redis cache
