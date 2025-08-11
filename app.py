import os
import requests
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CHATLING_API_KEY = os.getenv("CHATLING_API_KEY")
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

celery = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

@celery.task(name="tasks.query_chatling", max_retries=1, soft_time_limit=8, time_limit=10)
def query_chatling(message: str, session_id: str):
    headers = {
        "Authorization": f"Bearer {CHATLING_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"message": message, "sessionId": session_id}
    try:
        r = requests.post(CHATLING_API_URL, json=payload, headers=headers, timeout=4)
        if r.ok:
            return (r.json() or {}).get("answer")
        return None
    except Exception:
        return None

@celery.task(name="tasks.log_event", ignore_result=True)
def log_event(kind: str, payload: dict):
    # TODO: Google Sheets 기록 등 필요 시 구현
    return True
