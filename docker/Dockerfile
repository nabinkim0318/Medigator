# Local/demo API image for the research prototype.
# Not a production deployment. Build from the repository root:
#   docker build -f docker/Dockerfile .
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY data/ ./data/
COPY rag_index/ ./rag_index/
COPY docker/healthcheck.py ./docker/healthcheck.py

ENV PYTHONPATH=/app
ENV DB_URL=sqlite:///data/medigator.db
ENV DEMO_MODE=true
ENV SYNTHETIC_DATA_ONLY=true
ENV ENABLE_RAG=false

EXPOSE 8082

HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=5 \
    CMD ["python", "docker/healthcheck.py"]

CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8082"]
