from flask import Flask, request, jsonify
import requests
import logging

logging.basicConfig(level=logging.INFO)

logging.info(">>> importing app.py start")
app = Flask(__name__)
logging.info(">>> Flask app created")

try:
    logging.info(">>> Setting up API keys and routes")
    CHATLING_API_KEY = "3CDuWbTMau59Gmmm82KR5Y5nSxWHkzyAnGVFC41FCYF2Tb2GHNr9ud1bGc4jrVbc"
    CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

    @app.route("/", methods=["GET"])
    def health_check():
        return "OK", 200

    @app.route("/webhook", methods=["POST"])
    def kakao_webhook():
        # ... (기존 코드) ...
        return jsonify(kakao_response)

    logging.info(">>> All routes set up successfully")

except Exception as e:
    # 이 부분의 로그를 통해 실제 오류를 찾을 수 있습니다.
    logging.error(f"Failed to set up app routes or keys: {e}", exc_info=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
