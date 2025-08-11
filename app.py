from flask import Flask, request, jsonify
import requests
import logging

logging.basicConfig(level=logging.INFO)

logging.info(">>> importing app.py start")
app = Flask(__name__)
logging.info(">>> Flask app created")

# 이 위치에 로그를 추가하여 충돌 지점 파악
logging.info(">>> Setting up API keys")
CHATLING_API_KEY = "3CDuWbTMau59Gmmm82KR5Y5nSxWHkzyAnGVFC41FCYF2Tb2GHNr9ud1bGc4jrVbc"
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"
logging.info(">>> API keys set")

@app.route("/", methods=["GET"])
def health_check():
    return "OK", 200

@app.route("/webhook", methods=["POST"])
def kakao_webhook():
    # ... (기존 코드) ...
    return jsonify(kakao_response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
