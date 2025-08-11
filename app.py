import os
import logging
from flask import Flask, request, jsonify
import requests
import uuid  # 세션 ID 생성용

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("kakao-chatbot")

# Flask 앱 생성
app = Flask(__name__)

# 환경 변수에서 API 키 로드 (Railway Variables와 정확히 일치해야 함)
CHATLING_API_KEY = os.environ.get("CHATLING_API_KEY")
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

# 헬스 체크 엔드포인트
@app.route("/", methods=["GET"])
def health_check():
    return jsonify(
        status="healthy",
        service="kakao-chatbot",
        api_key_configured=bool(CHATLING_API_KEY)  # API 키 설정 여부 확인
    ), 200

# 카카오 웹훅 처리
@app.route("/webhook", methods=["POST"])
def kakao_webhook():
    try:
        # 1. 요청 데이터 파싱
        data = request.get_json()
        user_utterance = data.get("userRequest", {}).get("utterance", "").strip()
        user_id = data.get("userRequest", {}).get("user", {}).get("id", str(uuid.uuid4()))
        
        if not user_utterance:
            logger.error("유효하지 않은 요청: utterance 없음")
            return _make_kakao_response("질문을 입력해주세요.")

        # 2. API 키 확인
        if not CHATLING_API_KEY:
            logger.error("CHATLING_API_KEY 환경 변수 누락")
            return _make_kakao_response("시스템 오류: 관리자에게 문의해주세요.")

        # 3. Chatling API 호출
        headers = {
            "Authorization": f"Bearer {CHATLING_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "message": user_utterance,
            "sessionId": user_id  # 사용자 식별자
        }

        try:
            response = requests.post(
                CHATLING_API_URL,
                headers=headers,
                json=payload,
                timeout=3  # 3초 타임아웃
            )
            response.raise_for_status()
            answer = response.json().get("answer", "답변을 생성하지 못했습니다.")
        except requests.exceptions.Timeout:
            logger.warning("Chatling API 응답 시간 초과")
            answer = "응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."
        except Exception as e:
            logger.error(f"Chatling API 오류: {str(e)}")
            answer = "챗봇 응답 처리 중 오류가 발생했습니다."

        # 4. 카카오 응답 반환
        return _make_kakao_response(answer)

    except Exception as e:
        logger.critical(f"웹훅 처리 실패: {str(e)}", exc_info=True)
        return _make_kakao_response("일시적인 시스템 오류가 발생했습니다.")

# 카카오 응답 생성 헬퍼 함수
def _make_kakao_response(text):
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {
                    "text": text[:1000]  # 1000자 제한
                }
            }]
        }
    })

# 로컬 실행 (Railway에서는 gunicorn 사용)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
