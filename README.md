# DevPulse

> AI-powered GitHub activity digest agent. Monitor any GitHub org or repo and generate smart plain-English summaries using IBM watsonx + LangGraph.

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.11, FastAPI |
| Agent | LangGraph + IBM watsonx (`ibm-watsonx-ai`) |
| Frontend | Next.js 14 (App Router), Tailwind CSS |
| Database | PostgreSQL (via SQLAlchemy + Alembic) |
| Email | SMTP (Gmail / Resend) |
| Infra | Docker Compose |

## Features

- Connect any GitHub repo or org
- On-demand digest generation from the dashboard
- LangGraph agent that scores relevance and surfaces what actually matters
- Plain-English summary delivered via email
- Digest history browsable in the UI

## Quick Start

```bash
cp .env.example .env
# Fill in your keys (GitHub token, watsonx credentials, SMTP)

docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

## Project Structure

```
devpulse/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI route handlers
│   │   ├── agents/       # LangGraph agent definitions
│   │   ├── services/     # GitHub, email, watsonx services
│   │   ├── models/       # SQLAlchemy models
│   │   └── core/         # Config, DB, dependencies
│   └── tests/
├── frontend/
│   └── src/
│       ├── app/          # Next.js App Router pages
│       ├── components/   # UI components
│       └── lib/          # API client, utils
└── docker-compose.yml
```

## Environment Variables

See `.env.example` for all required variables.

