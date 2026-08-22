# Telegram Bot Setup

Get your Telegram bot running in 5 minutes.

## Step 1: Get Your Bot Token

### Via @BotFather (Official Telegram Method)

1. **Open Telegram** on your phone or desktop
2. **Search for** `@BotFather` (verified by Telegram)
3. **Send** `/start`
4. **Send** `/newbot`
5. Follow prompts:
   - **Name your bot**: e.g., "Hermes Agent Manager"
   - **Username**: e.g., `hermes_agent_bot` (must be unique)
6. **Copy the token** you receive — looks like: `123456:ABCdefGHIjklmnoPQRstuvwxyz`

## Step 2: Add Token to .env

1. Open `/Users/saf/hermes-api/.env`
2. Replace this line:
   ```
   TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
   ```
   With your actual token:
   ```
   TELEGRAM_BOT_TOKEN=123456:ABCdefGHIjklmnoPQRstuvwxyz
   ```
3. Save the file

## Step 3: Start the Service

```bash
cd /Users/saf/hermes-api
source venv/bin/activate
python run.py
```

You should see:
```
Starting FastAPI server...
✓ FastAPI server started
Starting Telegram bot...
✓ Telegram bot is running
```

## Step 4: Test Your Bot

1. **Open Telegram**
2. **Find your bot** by username (e.g., `@hermes_agent_bot`)
3. **Send** `/start`
4. **Send** `/deploy`
5. **Send** `Hello!`

The bot should respond! 🎉

---

## Available Commands

Once bot is running, users can:

```
/start          - Welcome message
/deploy         - Create new agent
/list           - Show all agents
/switch <id>    - Switch active agent
/status         - Check active agent
/config         - View/modify settings
/history        - Last 10 messages
/help           - Show all commands
```

**Chat directly** — just send any message to talk to your active agent.

---

## Configuration

Users can configure their agents:

```
/config reasoning=high
/config model=claude-opus-5
/config reasoning=medium model=claude-sonnet-5
```

**Reasoning levels**: `minimal`, `low`, `medium`, `high`, `xhigh`, `max`, `ultra`
**Models**: `claude-opus-5`, `claude-sonnet-5`

---

## Troubleshooting

### Bot not responding
- Check token is correct in `.env`
- Ensure bot is still running: `python run.py`
- Try sending `/start` again in Telegram

### "Agent not found"
- Deploy first with `/deploy`
- List agents with `/list`
- Use `/switch <agent_id>` to select

### API errors
- Ensure FastAPI is running on `localhost:8000`
- Check `server.log` for errors

---

## Multiple Bots

To run multiple bots (e.g., prod + test):

1. Create 2 separate bots via @BotFather
2. Create 2 `.env` files: `.env.prod`, `.env.test`
3. Run: `python -c "from dotenv import load_dotenv; load_dotenv('.env.prod'); import run; run.main()"`

Or create a separate directory for each bot.

---

## Next Steps

- ✅ Bot is running locally
- ⬜ Share bot username with friends/family
- ⬜ Collect feedback on what they want
- ⬜ Deploy to Railway (same as API)
- ⬜ Add real Argo integration

**Ready?** Continue to `DEPLOY.md` for cloud deployment.
