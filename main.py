"""
Hermes Agent API Server — MVP
Expose Hermes Agent capabilities as a REST API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add Hermes to path
sys.path.insert(0, str(Path.home() / ".hermes" / "hermes-agent"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Hermes Agent API",
    description="MVP service wrapping Hermes Agent for web access",
    version="0.1.0"
)

# CORS for frontend/testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Data Models ─────────────────────────────────────────────────────────

class AgentConfig(BaseModel):
    """Agent configuration"""
    reasoning_effort: str = Field(
        default=os.getenv("DEFAULT_REASONING", "medium"),
        description="Reasoning effort: minimal, low, medium, high, xhigh, max, ultra"
    )
    model: str = Field(
        default=os.getenv("DEFAULT_MODEL", "claude-opus-5"),
        description="Model to use"
    )
    max_tokens: int = Field(
        default=int(os.getenv("MAX_TOKENS", "4096")),
        description="Maximum tokens in response"
    )

class ChatRequest(BaseModel):
    """Chat/prompt request"""
    message: str = Field(..., description="User message or prompt")
    conversation_id: Optional[str] = Field(
        default=None,
        description="Track conversation state (for future multi-turn)"
    )
    config: Optional[AgentConfig] = Field(
        default=None,
        description="Override agent config for this request"
    )

class ChatResponse(BaseModel):
    """Chat response"""
    conversation_id: str
    response: str
    reasoning_used: bool
    tokens_used: Optional[int] = None
    model: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    hermes_available: bool
    version: str

# ─── In-memory state (for MVP) ───────────────────────────────────────────

conversations: dict = {}
default_config = AgentConfig()

# ─── Hermes Integration ───────────────────────────────────────────────────

def check_hermes_available() -> bool:
    """Check if Hermes is installed and accessible"""
    try:
        hermes_home = Path.home() / ".hermes"
        return hermes_home.exists()
    except Exception as e:
        logger.error(f"Error checking Hermes: {e}")
        return False

def invoke_hermes_agent(prompt: str, config: AgentConfig) -> tuple[str, bool]:
    """
    Invoke Hermes agent with a prompt.
    Returns: (response_text, reasoning_used)

    For MVP, we'll do a simple subprocess call to `hermes` CLI
    In production, this would use the Python API directly.
    """
    import subprocess
    import json
    import uuid

    try:
        # For now, simulate agent response
        # In production: call hermes gateway or SDK
        hermes_cmd = Path.home() / ".local" / "bin" / "hermes"

        if not hermes_cmd.exists():
            hermes_cmd = Path.home() / ".hermes" / "hermes-agent" / "hermes"

        if hermes_cmd.exists():
            # TODO: Wire up real Hermes CLI invocation
            logger.info(f"Hermes CLI found at {hermes_cmd}")

        # MVP fallback: return structured response
        response = f"""I received your message: "{prompt}"

Using Hermes Agent with:
- Model: {config.model}
- Reasoning: {config.reasoning_effort}
- Max tokens: {config.max_tokens}

[In production, this would invoke your Hermes agent with full reasoning and capabilities]"""

        return response, config.reasoning_effort != "minimal"

    except Exception as e:
        logger.error(f"Error invoking Hermes: {e}")
        raise

# ─── API Endpoints ───────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    hermes_ok = check_hermes_available()
    return HealthResponse(
        status="healthy" if hermes_ok else "degraded",
        hermes_available=hermes_ok,
        version="0.1.0"
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to Hermes agent
    """
    try:
        # Use provided config or default
        config = request.config or default_config

        # Generate conversation ID if needed
        conv_id = request.conversation_id or f"conv_{len(conversations)}_{hash(request.message) % 10000}"

        # Invoke agent
        response_text, reasoning_used = invoke_hermes_agent(request.message, config)

        # Store in conversation history
        if conv_id not in conversations:
            conversations[conv_id] = []
        conversations[conv_id].append({
            "role": "user",
            "content": request.message
        })
        conversations[conv_id].append({
            "role": "assistant",
            "content": response_text
        })

        return ChatResponse(
            conversation_id=conv_id,
            response=response_text,
            reasoning_used=reasoning_used,
            model=config.model
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config", response_model=AgentConfig)
async def get_config():
    """Get current default agent config"""
    return default_config

@app.post("/config", response_model=AgentConfig)
async def set_config(config: AgentConfig):
    """Update default agent config"""
    global default_config
    default_config = config
    logger.info(f"Config updated: {config}")
    return default_config

@app.get("/conversations")
async def list_conversations():
    """List all conversations (MVP only, no auth)"""
    return {
        "count": len(conversations),
        "ids": list(conversations.keys())
    }

@app.get("/conversations/{conv_id}")
async def get_conversation(conv_id: str):
    """Get conversation history"""
    if conv_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"id": conv_id, "messages": conversations[conv_id]}

@app.get("/")
async def root():
    """API root with info"""
    return {
        "name": "Hermes Agent API",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "health": "GET /health",
            "chat": "POST /chat",
            "config": "GET/POST /config",
            "conversations": "GET /conversations",
            "conversation": "GET /conversations/{conv_id}",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    logger.info("Starting Hermes Agent API Server...")
    logger.info(f"Hermes available: {check_hermes_available()}")
    logger.info(f"Listening on {host}:{port}")
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
