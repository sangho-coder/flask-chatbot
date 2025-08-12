FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway가 PORT를 주입합니다. 없을 때만 8080 사용.
ENV PORT=8080

# gunicorn으로 반드시 0.0.0.0:$PORT 바인딩
CMD exec gunicorn app:app --bind 0.0.0.0:${PORT} \
    --workers 1 --threads 1 --timeout 15 \
    --access-logfile - --error-logfile - --log-level info
