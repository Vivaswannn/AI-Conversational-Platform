# CODEBASE_MASTERCLASS.md

This file is a masterclass-style walkthrough of the actual codebase.

Purpose:

- teach you the codebase like a mentor would
- explain how the pieces connect
- explain why each major file exists
- use real snippets from your project
- include "Explain This Like I'm New" sections

If `LEARN.md` is your interview study guide, this file is your **code understanding guide**.

---

## How To Use This File

Read this in order:

1. overall architecture
2. request flow
3. auth
4. database
5. services
6. crisis detection
7. AI / RAG
8. WebSockets
9. Docker/runtime

Best practice:

- read a section
- then open the referenced file in your editor
- explain it aloud in your own words

---

## 1. What This Codebase Really Is

At first glance, this may look like "an AI chatbot project."

But architecturally, it is actually:

- a FastAPI backend
- with auth
- with persistence
- with realtime communication
- with safety logic
- with optional AI enhancement

That is an important mental model.

### Explain This Like I'm New

Imagine you are building a WhatsApp-style backend, but instead of just storing chats, you also want:

- user accounts
- message history
- live streaming replies
- a safety layer for dangerous messages
- AI-generated or fallback responses

That is basically what this codebase is doing.

---

## 2. Big-Picture Architecture

The codebase is organized around layers.

### Layer 1: App entrypoint

- `app/main.py`

### Layer 2: API routes

- `app/api/auth.py`
- `app/api/conversations.py`
- `app/api/messages.py`
- `app/api/websocket.py`

### Layer 3: Shared dependencies

- `app/dependencies.py`

### Layer 4: Business logic

- `app/services/auth_service.py`
- `app/services/conversation_service.py`
- `app/services/chat_service.py`
- `app/services/crisis_service.py`

### Layer 5: AI-specific helpers

- `app/ai/chain.py`
- `app/ai/rag.py`
- `app/ai/memory.py`
- `app/ai/prompts.py`

### Layer 6: Persistence

- `app/models/*`
- `app/database.py`
- `alembic/*`

### Layer 7: Runtime / infrastructure

- `docker-compose.yml`
- `docker/Dockerfile`
- `docker/entrypoint.sh`

---

## 3. Start at the Top: `app/main.py`

This file creates the FastAPI app and wires the whole backend together.

Real snippet:

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.api import auth, conversations, messages, websocket
from app.middleware.rate_limit import limiter
```

What this tells you:

- FastAPI is the web framework
- CORS is needed for browser clients
- there is a rate limit system
- routers are split by concern

Later in the same file:

```python
app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(messages.router)
app.include_router(websocket.router)
```

This is where all route groups are registered.

### Explain This Like I'm New

Think of `main.py` as the **control room** of the backend.

It does not contain the whole business logic itself.
It mainly says:

- "create the app"
- "turn on middleware"
- "plug in these route groups"
- "define a health endpoint"

### Important concept: Lifespan startup

`main.py` also initializes the RAG engine during startup:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing RAG engine...")
    try:
        from app.ai.rag import get_rag_engine
        get_rag_engine()
        logger.info("RAG engine ready")
    except Exception:
        logger.exception("RAG engine initialization failed — RAG will be unavailable")
    yield
```

Meaning:

- when the app starts, it tries to prepare the retrieval system
- if it fails, the app still runs

This is a great example of **graceful degradation**.

### Interview insight

This shows a mature design choice:

> optional AI capability should not bring down the whole backend.

---

## 4. API Layer: `app/api/conversations.py`

This file exposes conversation-related REST endpoints.

Real snippet:

```python
@router.post("/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: str,
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Non-streaming REST endpoint — returns user message and AI response."""
    await conversation_service.get_conversation(db, conversation_id, current_user.id)
    user_msg, ai_msg = await chat_service.process_message(
        db, current_user.id, conversation_id, body.content
    )
    return ChatResponse(message=user_msg, response=ai_msg)
```

### What this code is doing

Step by step:

1. receives `conversation_id`
2. receives body parsed as `ChatRequest`
3. injects DB session
4. injects authenticated user
5. checks the conversation belongs to that user
6. delegates real work to `chat_service`
7. returns a typed response model

### Explain This Like I'm New

This function is a **traffic cop**, not the factory.

It should not do all the work itself.

Its job is:

- accept request
- verify context
- send the task to the service layer
- return the result

That is good backend architecture.

### Why `Depends(...)` matters

This line:

```python
db: AsyncSession = Depends(get_db)
```

means:

> "FastAPI, please give me a database session for this request."

And:

```python
current_user: User = Depends(get_current_user)
```

means:

> "FastAPI, please authenticate the request and give me the logged-in user."

That is dependency injection in action.

---

## 5. Auth Route File: `app/api/auth.py`

This file handles:

- register
- login
- current user

This is where request-side auth behavior starts.

Typical flow:

- user sends email/password
- backend hashes password or verifies it
- backend returns JWT

### Explain This Like I'm New

This file is like the front desk of your login system.

It is not where hashing or token internals are fully implemented.
It is where auth requests enter the backend.

The helper logic lives in `auth_service.py`.

---

## 6. Shared Dependency Layer: `app/dependencies.py`

This file is small, but very important.

Real snippet:

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_session():
        yield session
```

This function supplies a database session to routes.

Now the more important snippet:

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    from app.models.user import User

    payload = decode_access_token(credentials.credentials)
    user_id: str = payload.get("sub")
```

### What this means

When a protected route runs:

1. FastAPI reads the `Authorization: Bearer ...` header
2. token is decoded
3. `sub` claim gives the user id
4. DB query loads the actual user row
5. that user object is passed into the route

This is where stateless JWT becomes actual app identity.

### Explain This Like I'm New

A token alone is not enough.

Why?

Because the system still needs to verify:

- token is valid
- token is not expired
- the user still exists
- the user is still active

That is why the dependency loads the `User` from the DB after decoding the token.

### Important distinction

Token says:

> "someone claiming to be user X"

DB lookup confirms:

> "yes, user X exists and is active"

---

## 7. Auth Service: `app/services/auth_service.py`

This file contains the actual helper logic for passwords and tokens.

Real snippet:

```python
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

### What this means

Passwords are:

- encoded into bytes
- hashed using bcrypt
- never stored as plaintext

Now token creation:

```python
def create_access_token(data: dict) -> str:
    settings = get_settings()
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["exp"] = expire
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

### What this means

When token is created:

- app copies the payload
- adds expiration time
- signs it with the secret key

### Explain This Like I'm New

Think of a JWT like a signed ID card.

The card contains claims like:

- who you are (`sub`)
- when it expires (`exp`)

The signature proves:

- the server created it
- it was not modified by the client

### Important interview clarification

JWT is **signed**, not necessarily **encrypted**.

That means:

- integrity is protected
- secrecy is not automatically guaranteed

---

## 8. Database Layer: `app/database.py`

Real snippet:

```python
def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the session factory, creating the engine exactly once."""
    global _engine, _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
```

### What this means

The engine is created lazily once.

Why?

- avoid doing expensive setup repeatedly
- centralize DB configuration
- support pooling

### Explain This Like I'm New

The engine is like the main DB connector factory.

A session is like one working conversation with the database.

Engine = long-lived setup  
Session = short-lived unit of work

### Why connection pooling matters

Without pooling:

- every request might open a brand new DB connection

That is expensive.

With pooling:

- connections are reused
- latency improves
- concurrency improves

---

## 9. Models: How Data Is Shaped

The important models are:

- `User`
- `Conversation`
- `Message`
- `CrisisEvent`

### Mental model

One user can have many conversations.
One conversation can have many messages.
One user can have many crisis events.

### Explain This Like I'm New

Imagine the data like folders:

- user = account owner
- conversation = one folder/thread
- message = one item inside the folder
- crisis_event = safety log entry about something important that happened

This structure is much cleaner than stuffing everything into one giant table.

---

## 10. Conversation Service: `app/services/conversation_service.py`

This file handles:

- create conversation
- get one conversation
- list conversations
- delete conversation
- save messages
- fetch message history

Real snippet:

```python
async def save_message(
    db: AsyncSession,
    conversation_id: str,
    role: str,
    content: str,
    tokens_used: int = 0,
) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tokens_used=tokens_used,
    )
    db.add(msg)
```

And then:

```python
await db.execute(
    sa_update(Conversation)
    .where(Conversation.id == conversation_id)
    .values(updated_at=datetime.now(timezone.utc))
)
await db.commit()
await db.refresh(msg)
```

### What this means

Saving a message also updates the conversation activity timestamp.

Why?

Because when listing conversations, you usually want most recently active conversations first.

### Explain This Like I'm New

If someone sends a new message in a conversation, that conversation should move to the top in the UI.

That is why `updated_at` is refreshed when a new message is saved.

This is a very common product/backend pattern.

---

## 11. The Most Important File: `app/services/chat_service.py`

This file is the real brain of the backend.

It orchestrates:

- saving the user message
- crisis detection
- history loading
- RAG retrieval
- LLM/fallback response generation
- response persistence

Real snippet:

```python
# 1. Save user message
user_msg: Message = await save_message(db, conversation_id, "user", user_content)

# 2. Crisis detection
severity, matched_keywords = await _crisis_detector.detect(user_content)
```

This shows the flow starts with persistence, then safety.

Now the guardrail branch:

```python
if severity in (CrisisSeverity.CRITICAL, CrisisSeverity.HIGH, CrisisSeverity.MEDIUM):
    safety_text = _crisis_detector.get_safety_response(severity)
    await save_message(db, conversation_id, "assistant", safety_text)
    await _log_crisis_event(db, user_id, user_msg.id, severity, matched_keywords)
    yield safety_text
    return
```

### Why this is powerful

This is the moment where the app says:

> "Safety wins over generation."

That is one of the best design decisions in the repo.

### Explain This Like I'm New

If the system thinks the message is serious enough, it does **not** ask the AI to freestyle a response.

Instead:

- it uses a known safe response
- it logs the event
- it exits early

That is called a **short-circuit path**.

### Normal path

If the crisis path does not trigger:

```python
recent = await get_recent_messages(db, conversation_id, n=10)
history = build_chat_history(recent)
```

Then retrieval:

```python
try:
    rag = get_rag_engine()
    context_chunks = rag.query(user_content)
except Exception:
    logger.exception("RAG retrieval failed; proceeding without context")
    context_chunks = []
```

Then response generation:

```python
async for token in stream_response(history, context_chunks, user_content):
    tokens.append(token)
```

### Why this file matters

This file proves you understand orchestration.

You are not just calling an LLM directly.
You are managing:

- state
- control flow
- safety
- fallback behavior
- persistence

That is real backend engineering.

---

## 12. Crisis Detection File: `app/services/crisis_service.py`

This file turns raw text into a risk severity.

It has:

- keyword tiers
- optional semantic detection
- safety response mapping

### Explain This Like I'm New

This file acts like a risk classifier.

It asks:

- does this message match dangerous phrases?
- if not exact phrases, is it semantically similar to dangerous phrases?
- if yes, how severe is it?

### Why a two-stage design?

Because:

- keywords are fast and predictable
- semantics are smarter but more expensive

Using both gives better coverage than using only one.

### Important limitation

The semantic path uses runtime embedding calls and is not yet optimized by caching reference embeddings.

That is a realistic thing to discuss in interviews.

---

## 13. AI Chain File: `app/ai/chain.py`

This file converts:

- history
- retrieved context
- current user message

...into model-ready input.

Real snippet:

```python
def _fallback_response(user_message: str) -> str:
    return (
        "I can still help with supportive guidance even without an AI provider key. "
        f"You said: \"{user_message}\". "
        "A practical next step is to break this into one small action you can do in 10 minutes, "
        "then reassess how you feel."
    )
```

### Why this matters

This fallback makes the backend usable even when no valid OpenAI key is present.

Then:

```python
if not _has_usable_openai_key(settings.OPENAI_API_KEY):
    yield _fallback_response(user_message)
    return
```

### Explain This Like I'm New

This is the code saying:

> "If the AI provider is unavailable, do not crash. Still return something valid."

This is a reliability pattern called **graceful degradation**.

Now prompt construction:

```python
messages: list[BaseMessage] = [SystemMessage(content=system_content)]
messages.extend(history)
messages.append(HumanMessage(content=user_message))
```

### What this means

The model sees:

1. system instructions
2. previous conversation turns
3. current user message

That is how the app simulates conversational continuity.

---

## 14. RAG File: `app/ai/rag.py`

This file builds and queries the retrieval engine.

Real snippet:

```python
documents = SimpleDirectoryReader(settings.KNOWLEDGE_BASE_PATH).load_data()
splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
```

### Why split documents?

Because embedding a whole giant document is less useful than embedding smaller, meaningful chunks.

Then:

```python
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    embed_model=embed_model,
    transformations=[splitter],
)
```

### What this means

The index stores semantic representations of the knowledge base.

Then query:

```python
response = self._query_engine.query(user_message)
return [node.node.text for node in response.source_nodes]
```

Meaning:

- user asks something
- top relevant chunks are returned
- those chunks become prompt context

### Explain This Like I'm New

RAG is basically:

1. search your own notes first
2. then answer using those notes

That is often better than asking the model to answer from memory alone.

---

## 15. Message History Endpoint: `app/api/messages.py`

This file is small but useful to understand pagination and message access.

Real snippet:

```python
@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def get_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
```

### What this teaches

This is a simple example of:

- path params
- query params
- validation constraints
- paginated access

### Explain This Like I'm New

`limit` = how many messages to fetch  
`offset` = how many messages to skip

This is a classic pagination pattern.

Why use it?

Because conversations can get long, and you do not always want to return all messages at once.

---

## 16. Rate Limiter File: `app/middleware/rate_limit.py`

Real snippet:

```python
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
)
```

### What this means

The limiter identifies clients by remote IP address and gives them a default request budget per minute.

### Explain This Like I'm New

Rate limiting is like saying:

> "You can only knock on the server’s door so many times per minute."

Why?

- stops spam
- reduces abuse
- protects backend capacity

### Important honesty point

The limiter is configured, but enforcement is not fully applied across all routes yet.

That is worth remembering.

---

## 17. WebSocket File: `app/api/websocket.py`

This file powers real-time chat.

Real snippet:

```python
@router.websocket("/ws/conversations/{conversation_id}")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: str,
    token: str | None = Query(default=None),
):
```

This defines the WebSocket endpoint.

Now the auth logic:

```python
header_token, selected_subprotocol = _extract_subprotocol_token(
    websocket.headers.get("sec-websocket-protocol")
)
ws_token = token or header_token
if not ws_token:
    raise ValueError("Missing websocket token")
```

### What this means

The socket can authenticate either:

- from query string
- or from WS subprotocol

Then the loop:

```python
while True:
    raw = await websocket.receive_text()
```

This means the socket stays open and can receive many messages over time.

Then:

```python
async for token_chunk in chat_service.process_message_streaming(
    db, user_id, conversation_id, content
):
    await websocket.send_json({"token": token_chunk})

await websocket.send_json({"done": True})
```

### Explain This Like I'm New

Think of WebSocket as a phone call instead of sending letters.

REST is like:

- send letter
- wait for reply

WebSocket is like:

- keep the line open
- talk continuously

That is why it feels natural for chat streaming.

---

## 18. Testing Setup: `tests/conftest.py`

This file is the backbone of your test environment.

Real snippet:

```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

This means tests use an in-memory SQLite DB instead of real Postgres.

Then:

```python
with patch("app.ai.chain.ChatOpenAI") as mock_llm_cls:
    mock_llm = AsyncMock()
```

### What this means

The tests replace the real LLM dependency with a fake implementation.

### Why mocking matters

You do not want tests to:

- depend on network access
- spend money on provider calls
- fail randomly because an external API is down

### Explain This Like I'm New

A mock is a pretend version of something expensive or external.

In this project:

- real LLM is replaced by fake streaming tokens
- real RAG behavior is simplified

This makes tests:

- faster
- cheaper
- more deterministic

---

## 19. Docker Compose: How the App Actually Runs

Real snippet:

```yaml
services:
  app:
    build:
      context: .
      dockerfile: docker/Dockerfile
```

This says:

- build the backend container from the project root

Then:

```yaml
environment:
  DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/ai_support
  REDIS_URL: redis://redis:6379
```

### What this means

Inside Docker, the app talks to:

- `db`
- `redis`

using service names, not `localhost`.

### Explain This Like I'm New

Inside the `app` container:

- `localhost` means the app container itself
- `db` means the database container
- `redis` means the redis container

That is a common Docker networking concept that many beginners miss.

---

## 20. The Three Most Important Design Lessons In This Codebase

### Lesson 1: Keep transport and business logic separate

Routes should not do everything.
Services should own behavior.

### Lesson 2: Safety should be a system path, not a prompt trick

The crisis short-circuit is stronger than merely asking the model to "be safe."

### Lesson 3: Optional AI is better than total dependency on AI

Fallback mode keeps the backend functional when the provider is unavailable.

These three lessons are the heart of the project.

---

## 21. Beginner FAQ

### "Why do we need both REST and WebSocket?"

Because they solve different communication patterns.

### "Why do we save messages in a database?"

So chat history persists across requests and sessions.

### "Why do we need models and schemas?"

Models define database structure.
Schemas define API input/output shape.

### "Why do we need migrations?"

Because changing Python code does not automatically change the actual database schema.

### "Why not just call OpenAI directly in the route?"

Because that would mix transport, business logic, and provider logic in one place, making the code harder to test and maintain.

---

## 22. What You Should Be Able To Explain After Reading This

After reading this file, you should be able to explain:

- what each major folder does
- how auth works
- how a REST message request flows
- how a WebSocket message flows
- how crisis detection changes behavior
- how RAG works in this project
- why fallback mode exists
- why Docker service-name networking matters
- why tests use mocks

If you can explain those confidently, you understand the codebase at a strong level.

---

## 23. Best Next Step

After this file, do this:

1. open each referenced file
2. read the snippet in context
3. explain it aloud in your own words
4. then practice using `INTERVIEW_QA.md`

That is how you turn reading into real understanding.
