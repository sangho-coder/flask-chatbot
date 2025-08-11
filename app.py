import logging
from flask import Flask, request, jsonify
import requests

# --- Logging (최상위에서 설정만) ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")
log.info(">>> importing app.py")

# --- Flask app 객체만 생성 ---
app = Flask(__name__)
log.info(">>> Flask app created")

# --- 상수만 선언(실행 로직 금지) ---
CHATLING_API_KEY = "3CDuWbTMau59Gmmm82KR5Y5nSxWHkzyAnGVFC41FCYF2Tb2GHNr9ud1bGc4jrVbc"
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

# --- Health endpoints (Railway 헬스체크 용) ---
@app.get("/")
def root_health():
    return "OK", 200

@app.get("/healthz")
def healthz():
    return jsonify(status="ok"), 200

# --- Kakao Webhook ---
@app.post("/webhook")
def kakao_webhook():
    try:
        body = request.get_json(force=True, silent=True) or {}
        log.info("Webhook body: %s", body)

        user_req = body.get("userRequest") or {}
        utter = user_req.get("utterance")
        user_id = (user_req.get("user") or {}).get("id")

        if not utter or not user_id:
            log.error("Invalid payload")
            return jsonify({
                "version": "2.0",
                "template": {"outputs": [
                    {"simpleText": {"text": "요청 형식이 올바르지 않습니다."}}
                ]}
            }), 200

        headers = {
            "Authorization": f"Bearer {CHATLING_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"message": utter, "sessionId": user_id}

        answer = None
        try:
            r = requests.post(CHATLING_API_URL, json=payload, headers=headers, timeout=2.5)
            if r.ok:
                answer = (r.json() or {}).get("answer")
            else:
                log.error("Chatling error %s: %s", r.status_code, r.text)
        except Exception as e:
            log.exception("Chatling request failed: %s", e)

        return jsonify({
            "version": "2.0",
            "template": {"outputs": [
                {"simpleText": {"text": answer or "현재 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."}}
            ]}
        }), 200

    except Exception as e:
        log.exception("Webhook handler failed: %s", e)
        return jsonify({
            "version": "2.0",
            "template": {"outputs": [
                {"simpleText": {"text": "서버 내부 오류가 발생했습니다."}}
            ]}
        }), 200

# ⚠️ 로컬 실행부 없음 (Railway는 gunicorn이 기동)
# if __name__ == "__main__": app.run(...)
