web: gunicorn app:app --bind 0.0.0.0:$PORT
worker: celery -A tasks.celery worker --loglevel=info
