import os
import logging
from flask import Flask, request, jsonify
import requests

# 필수 환경 변수 체크
if "CHATLING_API_KEY" not in os.environ:
    raise ValueError("🚨 CHATLING_API_KEY 환경 변수가 설정되지 않았습니다.")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = Flask(__name__)
CHATLING_API_KEY = os.environ["CHATLING_API_KEY"]
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

@app.route("/")
def health_check():
    return jsonify(status="healthy"), 200

@app.post("/webhook")
def kakao_webhook():
    # ... [기존 webhook 코드 유지] ...
    # 이 부분의 들여쓰기를 확인해 주세요.
    # 함수 내부에 포함되는 코드는 반드시 들여쓰기가 되어야 합니다.
    return jsonify(
        version="2.0",
        template={
            "outputs": [
                {
                    "simpleText": {
                        "text": "기존 웹훅 응답"
                    }
                }
            ]
        }
    )

# Flask 앱을 실행하는 별도의 함수 정의
def main():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
