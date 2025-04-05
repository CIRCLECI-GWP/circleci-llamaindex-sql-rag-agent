FROM python:3.12.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY .env .
COPY app.py .
COPY states.db .
COPY tests/ ./tests/

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Run app.py when the container launches
CMD ["streamlit", "run", "app.py", "--server.port", "8080"]