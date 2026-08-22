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
    Invoke Hermes agent via Anthropic API (using your configured keys).
    Returns: (response_text, reasoning_used)
    """
    import httpx

    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY not set. Using mock response.")
            return f"Mock: {prompt[:100]}...", False

        # Map model names
        model_map = {
            "claude-opus-5": "claude-3-5-opus-20241022",
            "claude-sonnet-5": "claude-3-5-sonnet-20241022",
            "claude-opus": "claude-3-opus-20240229",
            "claude-sonnet": "claude-3-5-sonnet-20241022",
        }
        actual_model = model_map.get(config.model, config.model)

        # Build request payload
        payload = {
            "model": actual_model,
            "max_tokens": config.max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        # Add thinking if using high reasoning
        if config.reasoning_effort in ["high", "xhigh", "max", "ultra"]:
            payload["thinking"] = {
                "type": "enabled",
                "budget_tokens": min(config.max_tokens // 2, 10000)
            }

        logger.info(f"Calling Anthropic API: {actual_model} (reasoning: {config.reasoning_effort})")

        # Call Anthropic API
        with httpx.Client() as client:
            response = client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json=payload,
                timeout=60.0
            )

            if response.status_code == 200:
                result = response.json()
                # Extract text from response
                text_content = ""
                thinking_content = ""

                for block in result.get("content", []):
                    if block.get("type") == "text":
                        text_content = block.get("text", "")
                    elif block.get("type") == "thinking":
                        thinking_content = block.get("thinking", "")

                response_text = text_content or f"(Agent processed: {prompt[:50]}...)"
                reasoning_used = bool(thinking_content)

                logger.info(f"✓ Anthropic responded ({len(response_text)} chars, reasoning: {reasoning_used})")
                return response_text, reasoning_used
            else:
                error_msg = response.text[:200]
                logger.error(f"API error {response.status_code}: {error_msg}")
                return f"❌ API error: {error_msg}", False

    except httpx.TimeoutException:
        logger.error("API call timed out")
        return "⏱️ Request took too long. Try a simpler prompt.", False
    except Exception as e:
        logger.error(f"Error calling Anthropic: {e}")
        return f"❌ Error: {str(e)[:200]}", False

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
