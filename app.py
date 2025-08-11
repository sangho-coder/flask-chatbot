from flask import Flask, request, jsonify
import requests
import logging

# ----- 로깅 설정 -----
logging.basicConfig(level=logging.INFO)
logging.info(">>> importing app.py start")

# ----- Flask 앱 생성 -----
app = Flask(__name__)
logging.info(">>> Flask app created")

try:
    logging.info(">>> Setting up API keys and routes")

    CHATLING_API_KEY = "3CDuWbTMau59Gmmm82KR5Y5nSxWHkzyAnGVFC41FCYF2Tb2GHNr9ud1bGc4jrVbc"
    CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

    # ----- 헬스체크 -----
    @app.route("/", methods=["GET"])
    def health_check():
        return "OK", 200

    # ----- 카카오 Webhook -----
    @app.route("/webhook", methods=["POST"])
    def kakao_webhook():
        try:
            body = request.get_json(force=True, silent=True) or {}
            logging.info(f"Webhook body: {body}")

            user_req = body.get("userRequest") or {}
            utter = user_req.get("utterance")
            user_id = (user_req.get("user") or {}).get("id")

            if not utter or not user_id:
                logging.error("Invalid payload")
                return jsonify({
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {"simpleText": {"text": "요청 형식이 올바르지 않습니다."}}
                        ]
                    }
                }), 200

            headers = {
                "Authorization": f"Bearer {CHATLING_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "message": utter,
                "sessionId": user_id
            }

            answer = None
            try:
                r = requests.post(
                    CHATLING_API_URL,
                    json=payload,
                    headers=headers,
                    timeout=2.5
                )
                if r.ok:
                    data = r.json()
                    answer = data.get("answer")
                else:
                    logging.error(f"Chatling error {r.status_code}: {r.text}")
            except Exception as e:
                logging.exception(f"Chatling request failed: {e}")

            kakao_response = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {"simpleText": {
                            "text": answer or "현재 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."
                        }}
                    ]
                }
            }
            return jsonify(kakao_response), 200

        except Exception as e:
            logging.exception(f"webhook handler failed: {e}")
            return jsonify({
                "version": "2.0",
                "template": {
                    "outputs": [
                        {"simpleText": {"text": "서버 내부 오류가 발생했습니다."}}
                    ]
                }
            }), 200

    logging.info(">>> All routes set up successfully")

except Exception as e:
    logging.error(f"Failed to set up app routes or keys: {e}", exc_info=True)

# ----- 로컬 실행 시 -----
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
