FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose API port
EXPOSE 8000

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Starting Relay MVP services..."\n\
python start_api.py &\n\
API_PID=$!\n\
python start_bot.py &\n\
BOT_PID=$!\n\
echo "API Server: $API_PID"\n\
echo "Telegram Bot: $BOT_PID"\n\
wait $API_PID $BOT_PID' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
