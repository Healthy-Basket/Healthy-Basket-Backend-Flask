FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser

USER root

COPY requirements.txt .

RUN mkdir -p /app/venv && chmod -R 777 /app/venv

RUN python -m venv /app/venv \
    && . /app/venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt

RUN chown -R appuser:appuser /app

USER appuser

COPY . .

EXPOSE 5000

ENV PATH="/app/venv/bin:$PATH"

CMD ["venv/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
