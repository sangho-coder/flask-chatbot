import os
from flask import Flask, request, jsonify
from celery import Celery
import requests

app = Flask(__name__)

# Celery 설정 (Redis 사용)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

# 필수! Chatling API 키 (도커/서버에 환경변수로 설정)
CHATLING_API_KEY = os.environ.get("CHATLING_API_KEY")

# 카카오 형식의 빈 응답 생성 (고객은 아무것도 안 보임)
def make_invisible_response():
    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": " "}}]  # 공백 1글자
        }
    }

@app.route("/webhook", methods=["POST"])
def kakao_webhook():
    # 1. 즉시 "빈 응답" 전송 (고객은 볼 수 없음)
    invisible_response = make_invisible_response()
    
    # 2. 백그라운드에서 답변 생성 (Celery)
    process_response.delay(request.json)
    
    return jsonify(invisible_response)

@celery.task
def process_response(data):
    """실제 답변은 여기서 생성 후 카카오 API로 전송"""
    user_id = data["userRequest"]["user"]["id"]
    question = data["userRequest"]["utterance"]
    
    # Chatling API 호출
    headers = {"Authorization": f"Bearer {CHATLING_API_KEY}"}
    response = requests.post(
        "https://api.chatling.ai/v1/respond",
        json={"messages": [{"role": "user", "content": question}]},
        headers=headers,
        timeout=10
    )
    answer = response.json()["choices"][0]["message"]["content"]
    
    # 카카오 API로 최종 답변 전송 (예: REST API 또는 SDK 사용)
    send_kakao_message(user_id, answer)

def send_kakao_message(user_id, text):
    """카카오 API로 메시지 보내기 (별도 구현 필요)"""
    print(f"📨 사용자 {user_id}에게 답변 전송: {text}")  # 테스트용 로그
    # 실제 구현 시 여기에 카카오 API 코드 추가

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
