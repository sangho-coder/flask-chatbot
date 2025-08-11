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

# ✅ 수정된 부분: 함수 정의와 main 블록 분리
def main():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()  # 명시적 함수 호출로 들여쓰기 문제 해결
