# app.py
import os
import logging
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")

CHATLING_API_KEY = os.environ.get("CHATLING_API_KEY")  # Railway Variables에 넣을 것
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

@app.get("/")
def health():
    return "OK", 200

@app.post("/webhook")
def kakao_webhook():
    body = request.get_json(silent=True) or {}
    user_req = body.get("userRequest", {})
    utter = user_req.get("utterance")
    user_id = user_req.get("user", {}).get("id", "unknown")

    if not CHATLING_API_KEY:
        log.error("CHATLING_API_KEY is not set")
        return _kakao_text("서버 키 설정이 필요합니다. 잠시 후 다시 시도해 주세요."), 500

    if not utter:
        return _kakao_text("질문을 입력해 주세요."), 400

    headers = {
        "Authorization": f"Bearer {CHATLING_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"message": utter, "sessionId": user_id}

    try:
        # 5초 룰 대비: 3.5초 정도 타임아웃
        res = requests.post(CHATLING_API_URL, json=payload, headers=headers, timeout=3.5)
        if res.ok:
            answer = res.json().get("answer", "답변을 찾기 어려워요.")
        else:
            log.warning("Chatling non-200: %s %s", res.status_code, res.text[:200])
            answer = "잠시 후 다시 시도해 주세요."
    except requests.Timeout:
        # 5초 전에 바로 응답
        log.warning("Chatling timeout → fallback")
        answer = "질문을 접수했어요. 조금 뒤 다시 말씀드릴게요."

    return _kakao_text(answer)

def _kakao_text(text: str):
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}]
        }
    })
