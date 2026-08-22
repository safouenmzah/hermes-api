"""
Hermes Agent API Server — MVP
Expose Hermes Agent capabilities as a REST API
Pluggable LLM provider backend (Claude, Hermes, etc.)
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

# Import provider abstraction (note: use llm_providers to avoid conflict with hermes providers module)
from llm_providers import get_provider, AgentConfig as ProviderConfig

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

class AgentConfigAPI(BaseModel):
    """Agent configuration (API model)"""
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
    system_prompt: str = Field(
        default="You are a helpful AI assistant.",
        description="System prompt for the agent"
    )

    def to_provider_config(self) -> ProviderConfig:
        """Convert API model to provider config"""
        return ProviderConfig(
            reasoning_effort=self.reasoning_effort,
            model=self.model,
            max_tokens=self.max_tokens,
            system_prompt=self.system_prompt
        )

class ChatRequest(BaseModel):
    """Chat/prompt request"""
    message: str = Field(..., description="User message or prompt")
    conversation_id: Optional[str] = Field(
        default=None,
        description="Track conversation state (for future multi-turn)"
    )
    config: Optional[AgentConfigAPI] = Field(
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
    llm_provider: str
    provider_available: bool
    version: str

# ─── In-memory state (for MVP) ───────────────────────────────────────────

conversations: dict = {}
default_config = AgentConfigAPI()

# Initialize LLM provider
llm_provider = get_provider()

# ─── Helper Functions ───────────────────────────────────────────────────

def check_hermes_available() -> bool:
    """Check if Hermes is installed and accessible"""
    try:
        hermes_home = Path.home() / ".hermes"
        return hermes_home.exists()
    except Exception as e:
        logger.error(f"Error checking Hermes: {e}")
        return False

# ─── API Endpoints ───────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    hermes_ok = check_hermes_available()
    provider_ok = llm_provider.health_check()
    return HealthResponse(
        status="healthy" if provider_ok else "degraded",
        hermes_available=hermes_ok,
        llm_provider=llm_provider.__class__.__name__,
        provider_available=provider_ok,
        version="0.1.0"
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to LLM agent (provider-agnostic)
    """
    try:
        # Use provided config or default
        api_config = request.config or default_config
        provider_config = api_config.to_provider_config()

        # Generate conversation ID if needed
        conv_id = request.conversation_id or f"conv_{len(conversations)}_{hash(request.message) % 10000}"

        # Invoke LLM via configured provider
        response_text, reasoning_used = llm_provider.invoke(request.message, provider_config)

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
            model=api_config.model
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config", response_model=AgentConfigAPI)
async def get_config():
    """Get current default agent config"""
    return default_config

@app.post("/config", response_model=AgentConfigAPI)
async def set_config(config: AgentConfigAPI):
    """Update default agent config"""
    global default_config
    default_config = config
    logger.info(f"Config updated: {config}")
    return default_config

@app.get("/provider")
async def get_provider_info():
    """Get current LLM provider info"""
    return {
        "provider": llm_provider.__class__.__name__,
        "available": llm_provider.health_check(),
        "config_key": "LLM_PROVIDER",
        "possible_values": ["anthropic", "claude", "hermes"],
        "current": os.getenv("LLM_PROVIDER", "anthropic")
    }

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
        "llm_provider": llm_provider.__class__.__name__,
        "endpoints": {
            "health": "GET /health",
            "chat": "POST /chat",
            "config": "GET/POST /config",
            "provider": "GET /provider",
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
