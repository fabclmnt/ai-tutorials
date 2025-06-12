FROM python:3.12-slim

WORKDIR /app

# Install system dependencies if needed (optional)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set environment variable (optional)
ENV STREAMLIT_PORT=8501

# Run the Streamlit app
CMD ["streamlit", "run", "chat.py", "--server.port=${STREAMLIT_PORT}"]
