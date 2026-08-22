#!/usr/bin/env python3
"""
Hermes Agent Manager - Launcher
Runs FastAPI server + Telegram bot simultaneously
"""

import os
import sys
import asyncio
import logging
from threading import Thread
from dotenv import load_dotenv
import uvicorn

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_api():
    """Run FastAPI server"""
    logger.info("Starting FastAPI server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("API_PORT", "8000")),
        log_level="info"
    )

async def run_bot():
    """Run Telegram bot"""
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not telegram_token or telegram_token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.error("❌ TELEGRAM_BOT_TOKEN not set in .env")
        logger.error("   Please add your bot token to .env and restart")
        return

    from telegram_bot import start_bot
    logger.info("Starting Telegram bot...")
    await start_bot(telegram_token)

def main():
    """Start both services"""
    logger.info("=" * 60)
    logger.info("Hermes Agent Manager - Startup")
    logger.info("=" * 60)

    # Check Telegram token
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_token or telegram_token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("\n❌ ERROR: Telegram bot token not configured!\n")
        print("📝 Steps to fix:")
        print("1. Open .env file")
        print("2. Replace YOUR_TELEGRAM_BOT_TOKEN_HERE with your actual token")
        print("3. Save and restart this script\n")
        print("📖 How to get a token:")
        print("   - Chat with @BotFather on Telegram")
        print("   - Type /newbot")
        print("   - Follow the prompts")
        print("   - Copy the token to .env\n")
        sys.exit(1)

    logger.info(f"✓ Telegram bot token configured")
    logger.info(f"✓ API port: {os.getenv('API_PORT', '8000')}")
    logger.info("")

    # Start FastAPI in background thread
    api_thread = Thread(target=run_api, daemon=True)
    api_thread.start()
    logger.info("✓ FastAPI server started")

    # Wait a moment for API to start
    import time
    time.sleep(2)

    # Start Telegram bot in main thread
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("\nShutdown signal received. Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
