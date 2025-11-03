# Use official Python image
FROM python:3.10-slim

# Create a non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code
COPY --chown=user . /app

# Run your Telegram bot
CMD ["python", "bot.py"]
