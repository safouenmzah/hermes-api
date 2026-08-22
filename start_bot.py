#!/usr/bin/env python3
"""Start Telegram bot only"""
import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Start the Telegram bot"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("❌ TELEGRAM_BOT_TOKEN not set in .env")
        sys.exit(1)

    from telegram_bot import start_bot_sync

    logger.info("🚀 Starting Relay bot...")
    logger.info("💬 Find your bot at: t.me/RelayxyzBot")
    logger.info("")

    try:
        start_bot_sync(token)
    except KeyboardInterrupt:
        logger.info("\n✓ Bot stopped gracefully")
        sys.exit(0)

if __name__ == "__main__":
    main()
