import logging, sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger("app")

log.info(">>> importing app.py start")

from flask import Flask, request, jsonify
import requests

log.info(">>> imports OK")

app = Flask(__name__)
log.info(">>> Flask app created")

CHATLING_API_KEY = "3CDuWbTMau59Gmmm82KR5Y5nSxWHkzyAnGVFC41FCYF2Tb2GHNr9ud1bGc4jrVbc"          # 그대로 OK
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

@app.route("/", methods=["GET"])
def health_check():
    return "OK", 200

@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify(status="ok"), 200

@app.route("/webhook", methods=["POST"])
def kakao_webhook():
    try:
        body = request.get_json(silent=True)
        if not body:
            log.error("No JSON body. headers=%s", dict(request.headers))
            return jsonify({"version":"2.0","template":{"outputs":[{"simpleText":{"text":"요청 본문이 비었습니다."}}]}}), 400

        # 방어적으로 꺼내기
        user_req = body.get("userRequest", {})
        utter = user_req.get("utterance")
        user_id = user_req.get("user", {}).get("id")
        if not utter or not user_id:
            log.error("Invalid payload: %s", body)
            return jsonify({"version":"2.0","template":{"outputs":[{"simpleText":{"text":"요청 형식이 올바르지 않습니다."}}]}}), 400

        headers = {"Authorization": f"Bearer {CHATLING_API_KEY}", "Content-Type": "application/json"}
        payload = {"message": utter, "sessionId": user_id}

        r = requests.post(CHATLING_API_URL, json=payload, headers=headers, timeout=10)
        if r.status_code == 200:
            answer = r.json().get("answer", "죄송합니다, 답변을 찾을 수 없습니다.")
        else:
            log.error("Chatling error %s: %s", r.status_code, r.text)
            answer = "죄송합니다, 서버와 연결이 원활하지 않습니다."

        return jsonify({"version":"2.0","template":{"outputs":[{"simpleText":{"text": answer}}]}})

    except Exception:
        log.exception("webhook handler failed")
        return jsonify({"version":"2.0","template":{"outputs":[{"simpleText":{"text":"서버 내부 오류가 발생했습니다."}}]}}), 500
