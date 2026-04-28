# AI Conversational Platform

Backend-first conversational support platform built with FastAPI, PostgreSQL, Redis, JWT auth, crisis detection, and streaming WebSockets.

## Current Status

- Backend APIs are functional and can be used without frontend.
- OpenAI key is optional for backend usage.
- When no valid OpenAI key is configured, chat uses a safe fallback response mode.

## Features

- JWT auth (`register`, `login`, `me`)
- Conversation and message APIs
- WebSocket streaming chat
- Crisis detection and safety response routing
- PostgreSQL persistence (users, conversations, messages, crisis events)
- Redis support
- Dockerized local development

## Quick Start (Backend Only, Docker)

From project root:

```bash
docker compose up -d db redis app
```

Health check:

```bash
curl http://localhost:8000/health
```

Docs:

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Optional Frontend

Frontend is present but still in progress. To include it:

```bash
docker compose up -d frontend
```

Then open `http://localhost:5173`.

## Backend Smoke Test (PowerShell)

```powershell
$body = @{ email = "test$(Get-Random)@example.com"; password = "Password123!" } | ConvertTo-Json
$register = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/auth/register" -ContentType "application/json" -Body $body
$token = $register.access_token
$headers = @{ Authorization = "Bearer $token" }

$conv = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/conversations" -Headers $headers -ContentType "application/json" -Body '{"title":"Backend Test"}'
$convId = $conv.id

$msg = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/conversations/$convId/messages" -Headers $headers -ContentType "application/json" -Body '{"content":"Give me one practical stress tip"}'
$msg | ConvertTo-Json -Depth 10
```

## WebSocket Usage

Connect:

`ws://localhost:8000/ws/conversations/{conversation_id}?token=<jwt>`

Send:

`{"content":"Hello"}`

Receive:

- token chunks: `{"token":"..."}`
- completion: `{"done": true}`

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register user |
| POST | `/auth/login` | Login and receive JWT |
| GET | `/auth/me` | Get current user |
| POST | `/conversations` | Create conversation |
| GET | `/conversations` | List user conversations |
| GET | `/conversations/{id}` | Get one conversation |
| DELETE | `/conversations/{id}` | Delete conversation |
| POST | `/conversations/{id}/messages` | Send message (REST) |
| GET | `/conversations/{id}/messages` | List message history |
| WS | `/ws/conversations/{id}` | Stream responses |
| GET | `/health` | Health endpoint |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT signing key (required) |
| `DATABASE_URL` | Postgres connection URL |
| `REDIS_URL` | Redis URL |
| `OPENAI_API_KEY` | Optional; enables LLM + embedding integrations |
| `OPENAI_MODEL` | Chat model (when key available) |
| `OPENAI_EMBEDDING_MODEL` | Embedding model (when key available) |
| `RATE_LIMIT_PER_MINUTE` | API rate-limit configuration |
