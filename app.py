import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify # requests 모듈은 현재 주석 처리된 상태

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
# Railway에서 'CHATLING_API_KEY' 환경 변수를 설정해야 합니다.
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

        # TODO: Chatling API 연동 (아래 코드 주석 해제하여 사용)
        # import requests # requests 모듈은 이 함수 내부에서 사용될 때만 가져오는 것이 효율적입니다.
        # if not CHATLING_API_KEY:
        #     log.error("CHATLING_API_KEY 환경 변수가 설정되지 않았습니다.")
        #     return _kakao_response("챗봇 설정 오류: API 키가 누락되었습니다.")
        
        # headers = {
        #     "Authorization": f"Bearer {CHATLING_API_KEY}",
        #     "Content-Type": "application/json",
        # }
        # payload = {
        #     "messages": [{"role": "user", "content": utterance}]
        # }
        
        # try:
        #     response = requests.post(CHATLING_API_URL, headers=headers, json=payload)
        #     response.raise_for_status() # HTTP 오류 발생 시 예외 발생
        #     chatling_response = response.json()
        #     ai_response = chatling_response["choices"][0]["message"]["content"]
        # except requests.exceptions.RequestException as e:
        #     log.exception(f"Chatling AI API 호출 오류: {e}")
        #     ai_response = "챗봇 응답을 가져오는 데 실패했습니다."
        
        # return _kakao_response(ai_response)

        # 현재는 테스트 모드로 동작
        log.info(f"사용자 발화 수신 (테스트 모드): {utterance}")
        return _kakao_response("테스트 모드: 정상 작동 중")

    except Exception as e:
        log.exception("처리 중 오류 발생: %s", e)
        return _kakao_response("일시적인 오류가 발생했습니다"), 500

# ----- 응답 포맷터 -----
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
    port = int(os.getenv("PORT", 8080))  # Railway 동적 포트 사용
    log.info(f"Flask 앱 로컬 실행 시작 (http://0.0.0.0:{port})")
    app.run(host="0.0.0.0", port=port)
