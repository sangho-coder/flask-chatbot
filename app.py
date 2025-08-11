import logging, sys
from flask import Flask, request, jsonify
import requests

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger("app")

log.info(">>> importing app.py start")
log.info(">>> imports OK")

app = Flask(__name__)
log.info(">>> Flask app created")

CHATLING_API_KEY = "3CDuWbTMau59Gmmm82KR5Y5nSxWHkzyAnGVFC41FCYF2Tb2GHNr9ud1bGc4jrVbc"
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
        # Content-Type 이 틀려도 파싱 시도
        body = request.get_json(force=True, silent=True) or {}
        if not body:
            log.error("No JSON body. headers=%s", dict(request.headers))
            # ❗항상 200으로 반환 (카카오가 오류로 처리하지 않게)
            return jsonify({
                "version":"2.0",
                "template":{"outputs":[{"simpleText":{"text":"요청 본문이 비었습니다."}}]}
            }), 200

        user_req = body.get("userRequest", {}) or {}
        utter = user_req.get("utterance")
        user_id = (user_req.get("user") or {}).get("id")
        if not utter or not user_id:
            log.error("Invalid payload: %s", body)
            return jsonify({
                "version":"2.0",
                "template":{"outputs":[{"simpleText":{"text":"요청 형식이 올바르지 않습니다."}}]}
            }), 200  # ❗200으로

        headers = {
            "Authorization": f"Bearer {CHATLING_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"message": utter, "sessionId": user_id}

        # ❗카카오 타임아웃 고려 (<=3초)
        try:
            r = requests.post(CHATLING_API_URL, json=payload, headers=headers, timeout=2.5)
            if r.ok:
                answer = r.json().get("answer", "죄송합니다, 답변을 찾을 수 없습니다.")
            else:
                log.error("Chatling error %s: %s", r.status_code, r.text)
                answer = "죄송합니다, 서버와 연결이 원활하지 않습니다."
        except Exception as e:
            log.exception("Chatling request failed")
            answer = "현재 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."

        return jsonify({
            "version":"2.0",
            "template":{"outputs":[{"simpleText":{"text": answer}}]}
        }), 200

    except Exception:
        log.exception("webhook handler failed")
        return jsonify({
            "version":"2.0",
            "template":{"outputs":[{"simpleText":{"text":"서버 내부 오류가 발생했습니다."}}]}
        }), 200  # ❗200으로
