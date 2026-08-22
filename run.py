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
    import subprocess

    logger.info("=" * 60)
    logger.info("Relay Agent Manager - Startup")
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
    logger.info("Starting services...")
    logger.info("")

    # Start API in background process
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app",
         "--host", "0.0.0.0",
         "--port", os.getenv("API_PORT", "8000"),
         "--log-level", "info"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    logger.info("✓ FastAPI server starting on port 8000...")

    # Wait for API to be ready
    import time
    time.sleep(2)

    # Start Telegram bot in main thread
    logger.info("✓ Relay bot starting...")
    logger.info("")
    logger.info("=" * 60)
    logger.info("Both services are running!")
    logger.info("Find your bot at: t.me/RelayxyzBot")
    logger.info("=" * 60)
    logger.info("")

    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("\n\nShutdown signal received.")
        logger.info("Stopping API server...")
        api_process.terminate()
        api_process.wait()
        logger.info("✓ All services stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()
