import os
import logging
import requests
from flask import Flask, request, jsonify

# ----- 로깅 -----
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")

# ----- Flask 앱 -----
app = Flask(__name__)

# ----- 환경 변수 -----
# ⚠️ Railway → Variables 에 CHATLING_API_KEY 를 등록하세요.
CHATLING_API_KEY = os.environ.get("CHATLING_API_KEY")
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

# ----- 헬스체크 -----
@app.get("/")
def health():
    # Railway Health Check용
    return "OK", 200

@app.get("/healthz")
def healthz():
    return jsonify(status="ok"), 200

# ----- 카카오 Webhook -----
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
        # 카카오 5초 룰 대비: 3.5초 타임아웃
        res = requests.post(
            CHATLING_API_URL, json=payload, headers=headers, timeout=3.5
        )
        if res.ok:
            answer = res.json().get("answer", "답변을 찾기 어려워요.")
        else:
            log.warning("Chatling non-200: %s %s", res.status_code, res.text[:200])
            answer = "잠시 후 다시 시도해 주세요."
    except requests.Timeout:
        log.warning("Chatling timeout → fallback")
        answer = "질문을 접수했어요. 조금 뒤 다시 말씀드릴게요."
    except Exception as e:
        log.exception("Chatling call failed: %s", e)
        answer = "서버 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."

    return _kakao_text(answer)

# ----- 카카오 응답 헬퍼 -----
def _kakao_text(text: str):
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": text}}
            ]
        }
    })
