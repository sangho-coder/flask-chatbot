import logging
from flask import Flask, request, jsonify
import requests

# ----- Logging (stdout로 간단히만) -----
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")
log.info(">>> importing app.py")

# ----- Flask App -----
app = Flask(__name__)
log.info(">>> Flask app created")

# ----- Chatling -----
CHATLING_API_KEY = "3CDuWbTMau59Gmmm82KR5Y5nSxWHkzyAnGVFC41FCYF2Tb2GHNr9ud1bGc4jrVbc"
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

# ----- Health Endpoints -----
@app.get("/")
def root_health():
    return "OK", 200

@app.get("/healthz")
def healthz():
    return jsonify(status="ok"), 200

# ----- Kakao Webhook -----
@app.post("/webhook")
def kakao_webhook():
    try:
        # 헤더가 부정확해도 최대한 파싱
        body = request.get_json(force=True, silent=True) or {}
        log.info("Webhook body: %s", body)

        user_req = body.get("userRequest") or {}
        utter = user_req.get("utterance")
        user_id = (user_req.get("user") or {}).get("id")

        # 형식 오류여도 200으로 응답 (카카오 오류 화면 방지)
        if not utter or not user_id:
            log.error("Invalid payload")
            return jsonify({
                "version": "2.0",
                "template": {"outputs": [
                    {"simpleText": {"text": "요청 형식이 올바르지 않습니다."}}
                ]}
            }), 200

        # Chatling 호출 (응답 제한 고려해 짧은 타임아웃)
        headers = {
            "Authorization": f"Bearer {CHATLING_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"message": utter, "sessionId": user_id}

        answer = None
        try:
            r = requests.post(
                CHATLING_API_URL,
                json=payload,
                headers=headers,
                timeout=2.5
            )
            if r.ok:
                data = r.json() or {}
                answer = data.get("answer")
            else:
                log.error("Chatling error %s: %s", r.status_code, r.text)
        except Exception as e:
            log.exception("Chatling request failed: %s", e)

        # 카카오 포맷으로 항상 200 반환
        return jsonify({
            "version": "2.0",
            "template": {"outputs": [
                {"simpleText": {
                    "text": answer or "현재 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."
                }}
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

# ⚠ Railway/Render 등에서는 gunicorn이 기동합니다.
# 로컬 테스트용이 필요하면 아래 주석 해제:
# if __name__ == "__main__":
#     import os
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
