import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify

# ----- 로깅 설정 (Railway에서 확인 가능하도록) -----
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger("KakaoChatbot")

# ----- Flask 앱 생성 (최소 초기화) -----
app = Flask(__name__)
log.info("Flask 앱 초기화 완료")

# ----- 반드시 필요한 환경 변수만 최상위에 유지 -----
CHATLING_API_KEY = os.getenv("CHATLING_API_KEY")

# Chatling API URL (나중에 API 호출 시 사용)
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

# ----- 헬스체크 (Railway 필수) -----
@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET"])
def health_check():
    """Railway Health Check용 엔드포인트"""
    log.info("Health Check 요청 수신")
    return jsonify(
        status="healthy",
        message="Service is running",
        timestamp=datetime.utcnow().isoformat(),
        env_loaded=bool(CHATLING_API_KEY)
    ), 200

# ----- 카카오 웹훅 (아주 간단한 응답으로 즉시 반환) -----
@app.post("/webhook")
def kakao_webhook():
    """카카오톡 채널 웹훅 요청을 처리하는 엔드포인트"""
    log.info("Kakao Webhook 요청 수신 (최소화된 테스트 모드)")
    # 요청 내용을 파싱하지 않고 무조건 고정된 응답을 즉시 반환
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "웹훅 테스트: 최소화된 응답입니다."
                    }
                }
            ]
        }
    })

# ----- 응답 포맷터 (더 이상 사용되지 않지만 혹시 몰라 유지) -----
def _kakao_response(text, status=200):
    """카카오 v2.0 형식 응답을 생성합니다."""
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}]
        }
    }), status

# ----- 메인 실행 (Gunicorn 사용 시 불필요하지만 로컬 테스트용으로 유지) -----
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    log.info(f"Flask 앱 로컬 실행 시작 (http://0.0.0.0:{port})")
    app.run(host="0.0.0.0", port=port)
