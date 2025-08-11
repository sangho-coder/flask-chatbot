import os
import logging
from flask import Flask, request, jsonify
import requests
from celery import Celery

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KakaoAsync")

app = Flask(__name__)

# Celery 설정 (Redis 브로커 사용)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(task_track_started=True)

# 환경 변수
CHATLING_API_KEY = os.environ.get("CHATLING_API_KEY")

def make_kakao_response(text):
    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}]
        }
    }

@app.route("/webhook", methods=["POST"])
def kakao_webhook():
    data = request.json
    user_utterance = data["userRequest"]["utterance"]
    user_id = data["userRequest"]["user"]["id"]  # 사용자 식별자

    # Phase 1: 즉시 응답 (1초 내)
    logger.info(f"즉시 응답 전송 (사용자 ID: {user_id})")
    immediate_response = make_kakao_response("네, 답변드리겠습니다! 🤗")

    # Phase 2: 백그라운드에서 답변 생성
    process_response.delay(user_id, user_utterance)

    return jsonify(immediate_response)

@celery.task
def process_response(user_id, user_utterance):
    """Celery로 비동기 처리되는 답변 생성"""
    try:
        # Chatling API 호출 (실제 답변 생성)
        headers = {"Authorization": f"Bearer {CHATLING_API_KEY}"}
        payload = {"messages": [{"role": "user", "content": user_utterance}]}
        response = requests.post(
            "https://api.chatling.ai/v1/respond",
            headers=headers,
            json=payload,
            timeout=10  # 길어도 OK (Celery는 별도 프로세스)
        )
        ai_response = response.json()["choices"][0]["message"]["content"]

        # 카카오로 추가 메시지 전송 (예: REST API 활용)
        send_kakao_followup(user_id, ai_response)

    except Exception as e:
        logger.error(f"답변 생성 실패: {e}")

def send_kakao_followup(user_id, text):
    """카카오 비즈니스 API로 후속 메시지 전송"""
    kakao_api_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Authorization": f"Bearer {KAKAO_ACCESS_TOKEN}",  # 카카오 액세스 토큰
        "Content-Type": "application/json"
    }
    payload = {
        "template_object": {
            "object_type": "text",
            "text": text,
            "link": {"web_url": "https://your-domain.com"}
        }
    }
    requests.post(kakao_api_url, headers=headers, json=payload)
