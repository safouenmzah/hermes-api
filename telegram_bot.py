"""
Telegram Bot Handler for Hermes Agent Management
Per-user agent deployment and chat interface
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)
from telegram.constants import ParseMode
import logging
import os
import json
from pathlib import Path
from datetime import datetime
import httpx
import uuid

logger = logging.getLogger(__name__)

# Storage (in production: use database)
AGENTS_FILE = Path("agents_db.json")

def load_agents() -> dict:
    """Load agents from storage"""
    if AGENTS_FILE.exists():
        return json.loads(AGENTS_FILE.read_text())
    return {}

def save_agents(agents: dict):
    """Save agents to storage"""
    AGENTS_FILE.write_text(json.dumps(agents, indent=2))

# ─── Command Handlers ────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Friend"
    agents = load_agents()

    user_agents = agents.get(str(user_id), {}).get("agents", [])

    welcome_text = f"""
👋 Welcome, {username}!

I'm your Hermes Agent Manager. You can:
• `/deploy` — Create a new AI agent for you
• `/list` — See your agents
• `/status` — Check agent status
• `/config` — Configure agent settings
• `/help` — See all commands

**Or just send a message** to chat with your active agent!

Ready to deploy? Type `/deploy`
"""

    await update.message.reply_text(welcome_text.strip())

async def deploy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /deploy command - create new agent"""
    user_id = update.effective_user.id
    agents = load_agents()

    # Create new agent for this user
    agent_id = f"agent_{uuid.uuid4().hex[:8]}"

    if str(user_id) not in agents:
        agents[str(user_id)] = {"username": update.effective_user.username, "agents": []}

    new_agent = {
        "id": agent_id,
        "name": f"Agent {len(agents[str(user_id)]['agents']) + 1}",
        "status": "running",
        "model": "claude-opus-5",
        "reasoning": "medium",
        "created_at": datetime.now().isoformat(),
        "message_count": 0
    }

    agents[str(user_id)]["agents"].append(new_agent)
    agents[str(user_id)]["active_agent"] = agent_id
    save_agents(agents)

    response = f"""
✅ Agent deployed!

**Agent ID:** `{agent_id}`
**Name:** {new_agent['name']}
**Model:** {new_agent['model']}
**Reasoning:** {new_agent['reasoning']}

You can now:
• Send messages to chat with this agent
• `/config` — Adjust settings
• `/list` — See all your agents
• `/status` — Check this agent
"""

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    logger.info(f"User {user_id} deployed agent {agent_id}")

async def list_agents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /list command - show user's agents"""
    user_id = update.effective_user.id
    agents = load_agents()
    user_data = agents.get(str(user_id), {})
    user_agents = user_data.get("agents", [])

    if not user_agents:
        await update.message.reply_text("No agents yet. Deploy one with `/deploy`")
        return

    response = "🤖 **Your Agents:**\n\n"
    for i, agent in enumerate(user_agents, 1):
        active = "✨ ACTIVE" if agent["id"] == user_data.get("active_agent") else "⏸️  inactive"
        response += f"{i}. **{agent['name']}** ({active})\n"
        response += f"   ID: `{agent['id']}`\n"
        response += f"   Model: {agent['model']} | Reasoning: {agent['reasoning']}\n"
        response += f"   Messages: {agent.get('message_count', 0)}\n\n"

    response += "Use `/switch <agent_id>` to switch agents"
    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command"""
    user_id = update.effective_user.id
    agents = load_agents()
    user_data = agents.get(str(user_id), {})
    active_id = user_data.get("active_agent")

    if not active_id:
        await update.message.reply_text("No active agent. Deploy with `/deploy`")
        return

    agent = next((a for a in user_data.get("agents", []) if a["id"] == active_id), None)

    if not agent:
        await update.message.reply_text("Agent not found")
        return

    response = f"""
🔍 **Agent Status**

**Name:** {agent['name']}
**ID:** `{agent['id']}`
**Status:** {agent['status']}
**Model:** {agent['model']}
**Reasoning Level:** {agent['reasoning']}
**Created:** {agent['created_at']}
**Messages:** {agent.get('message_count', 0)}
"""

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

async def config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /config command - show/modify agent config"""
    user_id = update.effective_user.id
    agents = load_agents()
    user_data = agents.get(str(user_id), {})
    active_id = user_data.get("active_agent")

    if not active_id:
        await update.message.reply_text("No active agent. Deploy with `/deploy`")
        return

    agent = next((a for a in user_data.get("agents", []) if a["id"] == active_id), None)

    if not agent:
        await update.message.reply_text("Agent not found")
        return

    # Parse config changes
    if context.args:
        for arg in context.args:
            if "=" in arg:
                key, value = arg.split("=", 1)
                if key in ["reasoning", "model"]:
                    agent[key] = value
        save_agents(agents)
        response = f"✅ Config updated!\n\n{format_config(agent)}"
    else:
        response = f"**Current Config:**\n\n{format_config(agent)}\n\nUsage: `/config reasoning=high model=claude-opus-5`"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = """
**Commands:**

🚀 **Agent Management**
• `/deploy` — Create new agent
• `/list` — Show all your agents
• `/switch <id>` — Switch active agent
• `/status` — Check active agent
• `/config [key=value]` — View/modify settings
• `/history` — Last 10 messages

⚙️ **Settings**
• `reasoning=minimal|low|medium|high|xhigh|max`
• `model=claude-opus-5|claude-sonnet-5`

💬 **Chat**
Just send any message to chat with your active agent!

**Example:**
```
/deploy
/config reasoning=high
Hello agent!
/history
```
"""
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /history command"""
    user_id = update.effective_user.id
    agents = load_agents()
    user_data = agents.get(str(user_id), {})
    active_id = user_data.get("active_agent")

    if not active_id:
        await update.message.reply_text("No active agent")
        return

    agent = next((a for a in user_data.get("agents", []) if a["id"] == active_id), None)

    if not agent or "conversation" not in agent:
        await update.message.reply_text("No conversation history yet")
        return

    history = agent.get("conversation", [])[-10:]  # Last 10 messages

    response = "📜 **Recent Messages:**\n\n"
    for msg in history:
        role = "👤" if msg["role"] == "user" else "🤖"
        response += f"{role} {msg['role'].upper()}\n{msg['content'][:100]}...\n\n"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular messages - forward to agent"""
    user_id = update.effective_user.id
    message_text = update.message.text

    agents = load_agents()
    user_data = agents.get(str(user_id), {})
    active_id = user_data.get("active_agent")

    if not active_id:
        await update.message.reply_text("No active agent. Deploy with `/deploy`")
        return

    agent = next((a for a in user_data.get("agents", []) if a["id"] == active_id), None)

    if not agent:
        await update.message.reply_text("Agent not found")
        return

    # Show typing indicator
    await update.message.chat.send_action("typing")

    try:
        # Call agent API (local FastAPI server)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/chat",
                json={
                    "message": message_text,
                    "conversation_id": active_id,
                    "config": {
                        "model": agent.get("model", "claude-opus-5"),
                        "reasoning_effort": agent.get("reasoning", "medium"),
                        "max_tokens": 4096
                    }
                },
                timeout=30.0
            )
            result = response.json()

            # Store in conversation
            if "conversation" not in agent:
                agent["conversation"] = []
            agent["conversation"].append({"role": "user", "content": message_text})
            agent["conversation"].append({"role": "assistant", "content": result["response"]})
            agent["message_count"] = agent.get("message_count", 0) + 1

            save_agents(agents)

            # Send response (truncate if too long)
            response_text = result["response"]
            if len(response_text) > 4000:
                response_text = response_text[:4000] + "\n...(truncated)"

            await update.message.reply_text(response_text)
            logger.info(f"User {user_id} sent message to {active_id}")

    except Exception as e:
        logger.error(f"Error calling agent: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

def format_config(agent: dict) -> str:
    """Format agent config for display"""
    return f"""
**Model:** `{agent.get('model', 'claude-opus-5')}`
**Reasoning:** `{agent.get('reasoning', 'medium')}`
**Max Tokens:** `4096`
"""

def create_bot(token: str) -> Application:
    """Create and configure Telegram bot"""
    app = Application.builder().token(token).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("deploy", deploy))
    app.add_handler(CommandHandler("list", list_agents))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("config", config))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("help", help_command))

    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app

def start_bot_sync(token: str):
    """Start the bot synchronously"""
    app = create_bot(token)
    logger.info("✓ Relay bot connected to Telegram")
    logger.info("✓ Bot is now listening for messages...")
    app.run_polling()
