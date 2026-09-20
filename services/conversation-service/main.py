from fastapi import Depends
import sys
import os
import structlog
import uuid
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request, Depends
from llm_client import send_message
from sqlalchemy.orm import Session
from database import get_db
from models import Conversation, Message


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader"))
from working_memory import get_history, append_message
from config_loader import get_secret  # noqa: E402

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)
logger = structlog.get_logger()

DATABASE_URL = get_secret("DATABASE_URL", vault_path="conversation-service")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

app = FastAPI(title="Conversational Agent Service")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info(
        "request_handled",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )
    return response


@app.get("/")
def root():
    return {"message": "Conversational Agent Service - v1.0 MVP"}


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "conversation-service", "environment": ENVIRONMENT}


@app.get("/readyz")
def readyz():
    return {"status": "ready"}


class ChatTestRequest(BaseModel):
    conversation_id: str | None = None
    message: str




@app.post("/v1/test/chat")
def test_chat(payload: ChatTestRequest):
    conversation_id = payload.conversation_id or str(uuid.uuid4())

    # আগের হিস্ট্রি লোড করা
    history = get_history(conversation_id)

    # এখনকার user মেসেজ history-তে যোগ করা (LLM-কে পাঠানোর আগে)
    append_message(conversation_id, "user", payload.message)

    # পুরো history দিয়ে একটা কনটেক্সট-সহ প্রম্পট বানানো (সরল approach — শুধু আগের মেসেজগুলো জোড়া দেওয়া)
    context_lines = [f"{m['role']}: {m['content']}" for m in history]
    context_lines.append(f"user: {payload.message}")
    full_context = "\n".join(context_lines)

    try:
        result = send_message(full_context)
    except RuntimeError as e:
        logger.error("chat_test_failed", error=str(e))
        raise HTTPException(status_code=503, detail="AI service temporarily unavailable")

    # assistant-এর রিপ্লাই memory-তে সেভ করা
    append_message(conversation_id, "assistant", result["reply"])

    return {
        "conversation_id": conversation_id,
        "reply": result["reply"],
        "provider_used": result["provider_used"],
    }


@app.post("/v1/conversations")
def create_conversation(db: Session = Depends(get_db)):
    conversation = Conversation()
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    logger.info("conversation_created", conversation_id=str(conversation.id))
    return {"conversation_id": str(conversation.id)}


class SendMessageRequest(BaseModel):
    message: str


@app.post("/v1/conversations/{conversation_id}/messages")
def send_conversation_message(conversation_id: str, payload: SendMessageRequest, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # PostgreSQL থেকে আগের হিস্ট্রি লোড করা (persistent, source of truth)
    previous_messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    # ইউজারের নতুন মেসেজ সেভ করা
    user_msg = Message(conversation_id=conversation_id, role="user", content=payload.message)
    db.add(user_msg)
    db.commit()

    # LLM-কে পাঠানোর জন্য কনটেক্সট বানানো
    context_lines = [f"{m.role}: {m.content}" for m in previous_messages]
    context_lines.append(f"user: {payload.message}")
    full_context = "\n".join(context_lines)

    try:
        result = send_message(full_context)
    except RuntimeError as e:
        logger.error("conversation_message_failed", conversation_id=conversation_id, error=str(e))
        raise HTTPException(status_code=503, detail="AI service temporarily unavailable")

    # Working memory (Redis) আপডেট — দ্রুত-অ্যাক্সেস ক্যাশ হিসেবে
    append_message(conversation_id, "user", payload.message)
    append_message(conversation_id, "assistant", result["reply"])

    # Assistant-এর রিপ্লাই PostgreSQL-এ স্থায়ীভাবে সেভ করা
    assistant_msg = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=result["reply"],
        provider_used=result["provider_used"],
    )
    db.add(assistant_msg)
    db.commit()

    logger.info("conversation_message_success", conversation_id=conversation_id, provider=result["provider_used"])
    return {
        "conversation_id": conversation_id,
        "reply": result["reply"],
        "provider_used": result["provider_used"],
    }


@app.get("/v1/conversations/{conversation_id}/history")
def get_conversation_history(conversation_id: str, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "provider_used": m.provider_used,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
    }