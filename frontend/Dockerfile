FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend ./frontend
COPY reports ./reports
COPY data/synthetic ./data/synthetic

# Streamlit reads ./.streamlit/config.toml from the process working directory.
RUN mkdir -p .streamlit \
    && cp frontend/.streamlit/config.toml .streamlit/config.toml

RUN useradd -m app && chown -R app /app

USER app

CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
