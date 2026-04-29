# INTERVIEW_QA.md

This file is your rapid interview practice sheet for the `AI Conversational Platform`.

Use it in two ways:

1. read the question and answer aloud
2. hide the answer and try to answer from memory first

---

## 1. Elevator Pitch

### Q1. What is this project?

This is a backend-first conversational support platform built with FastAPI, PostgreSQL, Redis, JWT auth, WebSockets, crisis detection, and optional AI/RAG integration for supportive chat.

### Q2. What problem were you solving?

I wanted to build more than a basic chatbot demo. I wanted a real backend system that could authenticate users, persist chat history, stream responses in real time, and handle high-risk messages safely.

### Q3. What makes this more than a CRUD app?

It combines CRUD-style APIs with realtime communication, AI integration, safety routing, persistence, and failure-tolerant fallback behavior.

---

## 2. Architecture

### Q4. What is the high-level architecture?

The backend is organized into API routes, dependency/auth handling, service-layer orchestration, AI/RAG helpers, SQLAlchemy models, and infrastructure via Docker Compose with Postgres and Redis.

### Q5. Why did you use a service layer?

To separate transport concerns from application behavior. Routes stay thin while business logic like chat orchestration and crisis handling lives in dedicated services, which makes the code easier to test and reason about.

### Q6. What is the request flow for sending a message?

The request is authenticated, conversation ownership is checked, the user message is saved, crisis detection runs, and then either a safety response is returned or the AI/RAG path is executed. The assistant response is then saved and returned.

### Q7. What is the request flow for WebSockets?

The client connects with a token, the socket is authenticated, JSON messages are validated, conversation ownership is verified, and response chunks are streamed back as token messages followed by a done event.

---

## 3. FastAPI

### Q8. Why FastAPI?

I chose FastAPI because it provides async support, strong request validation with Pydantic, automatic OpenAPI docs, and a clean dependency injection system.

### Q9. What is dependency injection in this project?

Dependency injection is how FastAPI provides things like database sessions and the current authenticated user to route handlers automatically.

### Q10. Why is dependency injection useful?

It reduces repeated code, keeps routes clean, and makes testing easier because dependencies can be overridden.

---

## 4. Authentication and Security

### Q11. How does authentication work?

Users register and log in through REST endpoints. Passwords are hashed with bcrypt, and successful login or registration returns a JWT access token. Protected routes decode the token and load the current user from the database.

### Q12. Why use JWT?

JWT is simple, stateless, and works well for API authentication across both REST and WebSocket paths.

### Q13. What data is in the JWT?

The token includes at least a subject claim (`sub`) for user identity and an expiration claim (`exp`).

### Q14. Why use bcrypt?

bcrypt is intentionally slow, which makes brute-force password attacks harder than using fast general-purpose hashes.

### Q15. What are current auth limitations?

The current system uses access tokens only. It does not yet have refresh tokens, revocation, MFA, or role-based access control.

### Q16. What is the difference between authentication and authorization?

Authentication verifies who the user is. Authorization determines what that authenticated user is allowed to access.

---

## 5. Database and Persistence

### Q17. Why PostgreSQL?

The data model is relational: users own conversations, conversations contain messages, and crisis events reference users and sometimes messages. PostgreSQL is a good fit for that structure and integrity.

### Q18. Why use SQLAlchemy?

SQLAlchemy provides ORM mapping, async support, and expressive query building, which makes database access cleaner and safer than writing raw SQL everywhere.

### Q19. Why use async sessions?

Because database operations are I/O-bound, and async allows the application to handle other work while waiting for the DB.

### Q20. Why use UUIDs instead of integer IDs?

UUIDs are harder to guess and safer to expose through APIs. They also work well when you want globally unique identifiers.

### Q21. What are the main entities?

User, Conversation, Message, and CrisisEvent.

### Q22. Why separate Conversation and Message?

Because conversations are the parent thread and messages are the atomic chat records. Separating them makes querying, deletion, ownership, and pagination cleaner.

---

## 6. Migrations

### Q23. Why use Alembic?

Alembic gives explicit, versioned database schema changes, which prevents drift between application models and the real database schema.

### Q24. Why are migrations important even in small projects?

Because changing Python models alone does not update the actual database. Without migrations, runtime errors happen when schema and code diverge.

---

## 7. WebSockets and Realtime

### Q25. Why use WebSockets here?

WebSockets are a good fit for chat because they support persistent bidirectional communication and make streaming responses feel natural.

### Q26. Why not use only REST?

REST is good for finite request/response operations like login or creating a conversation, but live streaming chat is more naturally modeled as a persistent socket connection.

### Q27. Why not use SSE instead of WebSockets?

SSE is simpler for one-way streaming, but WebSockets are better if I want richer bidirectional interaction and more flexible realtime message patterns.

### Q28. What are weaknesses of the current WebSocket design?

There is no connection manager, pub/sub scaling layer, or multi-instance coordination. Query-param token auth is also convenient but weaker operationally than stricter alternatives.

---

## 8. Crisis Detection

### Q29. What is the purpose of crisis detection?

To identify messages that suggest high-risk emotional distress and route them away from normal AI generation into deterministic safety responses.

### Q30. How does crisis detection work?

It uses two stages: keyword-based detection and optional semantic similarity detection using embeddings.

### Q31. Why run crisis detection before the AI path?

Because safety needs to be deterministic in serious cases. It is safer to short-circuit than to let a model improvise on potentially dangerous prompts.

### Q32. What happens on a high-severity message?

The system skips the normal LLM flow, stores a crisis event, saves a predefined assistant safety response, and returns that instead of generating a free-form answer.

### Q33. What is a limitation of the semantic crisis path?

It currently recomputes reference embeddings rather than caching them, which is more expensive than necessary.

---

## 9. AI and RAG

### Q34. What is RAG?

RAG stands for Retrieval-Augmented Generation. It means retrieving relevant knowledge first and then injecting it into the model prompt to ground the answer.

### Q35. Why use RAG in this project?

To make answers more grounded in curated support material rather than relying only on the model’s pretrained knowledge.

### Q36. What tools are used for RAG?

LlamaIndex for orchestration, ChromaDB as the vector store, and OpenAI embeddings for semantic search.

### Q37. What is an embedding?

An embedding is a numeric vector representation of text meaning, used for semantic similarity.

### Q38. What is a vector store?

A vector store is a database optimized for storing embeddings and retrieving semantically similar items.

### Q39. Why chunk documents before embedding them?

Because smaller, semantically focused chunks are easier to retrieve accurately than large documents.

### Q40. What happens if no OpenAI key is available?

The backend falls back to deterministic supportive responses, so the system still works instead of failing completely.

---

## 10. Reliability and Failure Handling

### Q41. What does graceful degradation mean in your project?

It means the backend continues to work in a reduced but valid mode when optional AI dependencies are unavailable or broken.

### Q42. What are the hard dependencies?

The database is a hard dependency for normal backend operation. AI is optional because of fallback mode.

### Q43. What happens if the provider fails during generation?

The chat service catches the error and returns a fallback error message instead of crashing the entire request path.

### Q44. What happens if RAG initialization fails?

Startup logs the failure and the app keeps running with RAG unavailable.

---

## 11. Redis and Infra

### Q45. Why include Redis?

Redis is useful for caching, session-like features, rate limiting state, and pub/sub. Even though it is not deeply used in the current main path, it is the right support system for future scaling.

### Q46. What does Docker Compose do here?

It orchestrates the app, database, Redis, and optional frontend so the development environment is reproducible and easier to run.

### Q47. Why are health checks important?

Because a service starting is not the same as a service being ready to accept requests. Health checks reduce startup race conditions.

### Q48. Explain Docker service-name networking.

Containers talk to each other using Compose service names like `db` or `redis`, while the host machine talks to exposed ports like `localhost:8000`.

---

## 12. Tests

### Q49. What do your tests cover?

They cover auth behavior, chat flow basics, crisis override behavior, config behavior, and route-level integration paths.

### Q50. What are test limitations?

Tests use in-memory SQLite and mocked AI/RAG behavior, so they do not fully represent production Postgres, real provider behavior, or full runtime networking.

### Q51. Why is mocking still useful?

Mocking makes tests deterministic, faster, and focused on application logic rather than external dependencies.

---

## 13. Design Tradeoffs

### Q52. What is the strongest design decision in this project?

The crisis-detection short-circuit is probably the strongest, because it puts safety ahead of normal generative behavior.

### Q53. What is the biggest architecture weakness?

Auth and reliability are still basic compared to production-grade systems: no refresh tokens, no revocation, incomplete rate-limit enforcement, and limited scaling strategy for WebSockets.

### Q54. What would you improve first?

I would improve auth lifecycle management, semantic detection efficiency, rate-limit enforcement, and observability.

### Q55. How would you scale WebSockets?

I would introduce Redis-backed pub/sub or a dedicated connection manager and design for multi-instance coordination rather than relying on per-process socket loops only.

---

## 14. Behavioral / Reflection Questions

### Q56. What did you learn from building this?

I learned how to connect backend fundamentals with AI features responsibly. The project taught me that the hard part is not just generating text, but managing auth, persistence, safety, realtime communication, and failure handling.

### Q57. If you started over, what would you change?

I would still keep the same core architecture, but I would design refresh-token auth and observability earlier, and I would cache semantic detection reference embeddings from the start.

### Q58. What part are you most proud of?

I am most proud that the backend works as a real system even without a live AI key, and that safety logic is treated as a first-class architectural concern.

### Q59. What was the hardest bug or challenge?

A key challenge was getting the runtime environment stable across Docker, database readiness, auth, CORS, and fallback behavior while keeping the backend usable during integration issues.

### Q60. Why did you put this on your resume?

Because it demonstrates a combination of backend engineering, realtime systems, persistence, authentication, safety-aware product thinking, and AI integration in one project.

---

## 15. Lightning Round

### Q61. What is async good for?

I/O-bound waits.

### Q62. What is async bad for?

CPU-heavy tasks.

### Q63. What is JWT good for?

Simple stateless auth.

### Q64. What is JWT weak at?

Revocation and logout invalidation.

### Q65. What is RAG for?

Grounding responses in retrieved knowledge.

### Q66. What is Redis best for?

Low-latency transient state like caching, rate limits, or pub/sub.

### Q67. What is Alembic for?

Versioned database schema migrations.

### Q68. Why not store plaintext passwords?

Because it is insecure and unacceptable.

### Q69. Why does the system save user messages before AI?

To avoid losing input and preserve history even if later steps fail.

### Q70. Why is crisis detection before AI?

Because safety should override normal generation in high-risk cases.

---

## 16. Final Practice Prompt

If an interviewer says:

> "Walk me through your project from the top, then tell me the hardest tradeoff you made."

You can answer like this:

> I built a backend-first conversational support platform using FastAPI, PostgreSQL, Redis, JWT auth, and WebSockets. Users authenticate, create conversations, and send messages through either REST or WebSocket flows. Messages are persisted, recent history is reconstructed from the DB, and a crisis-detection layer runs before any AI behavior. If the system detects a serious safety signal, it bypasses the normal model path and returns a deterministic safety response. Otherwise, it can use retrieval-augmented generation with LlamaIndex and ChromaDB, or fall back to deterministic supportive messaging if no AI key is configured. The hardest tradeoff was balancing simplicity with production realism: I built a clean core architecture with persistence, safety, and realtime communication first, while leaving advanced auth, observability, and scaling concerns as the next hardening phase.
