FROM python:3.12.5

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY states.db .
COPY tests/ ./tests/
COPY us-flag.png .

EXPOSE 8080

# Create a non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Run app.py when the container launches
CMD ["streamlit", "run", "app.py", "--server.port", "8080"]