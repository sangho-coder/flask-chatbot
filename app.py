import os
import logging
from flask import Flask, request, jsonify
import requests

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# Flask 앱 생성
app = Flask(__name__)
logger.info(">>> Flask app created")

# 환경 변수에서 API 키 가져오기
CHATLING_API_KEY = os.environ.get("CHATLING_API_KEY")

CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

@app.route("/", methods=["GET"])
def health_check():
    """서버 상태를 확인하는 헬스 체크 엔드포인트"""
    return jsonify(status="healthy"), 200

@app.route("/webhook", methods=["POST"])
def kakao_webhook():
    """카카오톡 채널 웹훅 요청을 처리하는 엔드포인트"""
    data = request.json
    user_utterance = data["userRequest"]["utterance"]

    # Chatling AI API 키가 설정되지 않았을 경우
    if not CHATLING_API_KEY:
        logger.error("CHATLING_API_KEY 환경 변수가 설정되지 않았습니다.")
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "챗봇 설정 오류: API 키가 누락되었습니다."
                        }
                    }
                ]
            }
        })
    
    # Chatling AI API 호출
    headers = {
        "Authorization": f"Bearer {CHATLING_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "messages": [{"role": "user", "content": user_utterance}]
    }

    try:
        response = requests.post(CHATLING_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        chatling_response = response.json()
        ai_response = chatling_response["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Chatling AI API 호출 오류: {e}")
        ai_response = "챗봇 응답을 가져오는 데 실패했습니다."

    # 카카오톡 포맷에 맞춘 응답 생성
    kakao_response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": ai_response
                    }
                }
            ]
        }
    }
    return jsonify(kakao_response)
