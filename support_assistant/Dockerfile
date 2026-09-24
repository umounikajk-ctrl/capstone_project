# 1. Use Python 3.11
FROM python:3.11-slim

# 2. Create /app as the working directory inside the container
WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --default-timeout=300 -r /app/requirements.txt

COPY main.py /app/main.py
COPY graph.py /app/graph.py
COPY ingest.py /app/ingest.py
COPY prompts.py /app/prompts.py

COPY docs /app/docs

RUN mkdir -p /app/data/chroma

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]