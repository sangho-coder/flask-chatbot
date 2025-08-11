import os
import logging
from flask import Flask, request, jsonify
import requests

# 로깅 설정 (파일 + 콘솔 출력)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('kakao_chatbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("KakaoChatbot")

app = Flask(__name__)
logger.info("Flask 서버 시작")

# 환경 변수 로드
CHATLING_API_KEY = os.environ.get("CHATLING_API_KEY")
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

# 카카오 응답 형식 (공통 템플릿)
def make_kakao_response(text):
    """카카오 챗봇 v2.0 형식으로 응답 생성"""
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": text
                    }
                }
            ]
        }
    }

@app.route("/", methods=["GET"])
def health_check():
    """헬스 체크 (카카오 서버 검증용)"""
    return jsonify(status="OK"), 200

@app.route("/webhook", methods=["POST"])
def kakao_webhook():
    """카카오 웹훅 핸들러 (502 오류 방지 핵심 로직)"""
    try:
        # 1. 요청 데이터 검증
        data = request.get_json()
        if not data or "userRequest" not in data:
            logger.error("잘못된 요청 형식: userRequest 필드 없음")
            return jsonify(make_kakao_response("올바른 요청이 아닙니다.")), 400

        user_utterance = data["userRequest"].get("utterance", "")
        logger.info(f"사용자 질문: {user_utterance}")

        # 2. API 키 검증
        if not CHATLING_API_KEY:
            logger.error("API 키 누락: CHATLING_API_KEY 환경 변수 확인 필요")
            return jsonify(make_kakao_response("챗봇 설정 오류가 발생했습니다.")), 500

        # 3. Chatling AI API 호출 (타임아웃 3초 설정)
        headers = {
            "Authorization": f"Bearer {CHATLING_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "messages": [{"role": "user", "content": user_utterance}]
        }

        response = requests.post(
            CHATLING_API_URL,
            headers=headers,
            json=payload,
            timeout=3  # 카카오의 5초 제한을 고려
        )
        response.raise_for_status()

        # 4. 응답 파싱
        ai_response = response.json()["choices"][0]["message"]["content"]
        logger.info(f"AI 응답: {ai_response}")

        # 5. 카카오 형식으로 반환
        return jsonify(make_kakao_response(ai_response))

    except requests.exceptions.Timeout:
        logger.error("Chatling API 호출 타임아웃")
        return jsonify(make_kakao_response("응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요.")), 200

    except requests.exceptions.RequestException as e:
        logger.error(f"API 호출 실패: {str(e)}")
        return jsonify(make_kakao_response("챗봇 서비스에 일시적 문제가 발생했습니다.")), 200

    except Exception as e:
        logger.critical(f"예상치 못한 오류: {str(e)}", exc_info=True)
        return jsonify(make_kakao_response("처리 중 오류가 발생했습니다.")), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
