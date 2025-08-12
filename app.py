import os
import logging
from datetime import datetime
from flask import Flask, jsonify

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
CHATLING_API_KEY = os.getenv("CHATLING_API_KEY")  # 주의: getenv() 사용

# ----- 헬스체크 (Railway 필수) -----
@app.route("/")
@app.route("/health")
def health_check():
    """Railway Health Check용 엔드포인트"""
    log.info("Health Check 요청 수신")
    return jsonify(
        status="healthy",
        message="Service is running",
        timestamp=datetime.utcnow().isoformat(),
        env_loaded=bool(CHATLING_API_KEY)  # 환경 변수 로드 확인용
    ), 200

# ----- 카카오 웹훅 (기본 구조만 유지) -----
@app.post("/webhook")
def kakao_webhook():
    try:
        # 필수 파라미터 검증
        data = request.get_json()
        if not data:
            log.error("빈 요청 수신")
            return _kakao_response("올바른 요청이 아닙니다"), 400

        user_req = data.get("userRequest", {})
        utterance = user_req.get("utterance", "").strip()
        
        if not utterance:
            return _kakao_response("질문을 입력해 주세요"), 400

        # 간단한 응답 테스트 (실제 API 호출 전 단계)
        return _kakao_response("테스트 모드: 정상 작동 중")

    except Exception as e:
        log.exception("처리 중 오류 발생: %s", e)
        return _kakao_response("일시적인 오류가 발생했습니다"), 500

# ----- 응답 포맷터 -----
def _kakao_response(text, status=200):
    """카카오 v2.0 형식 응답"""
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}]
        }
    }), status

# ----- 메인 실행 -----
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # Railway 동적 포트
    app.run(host="0.0.0.0", port=port)
