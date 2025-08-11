import os
import logging
from flask import Flask, request, jsonify
import requests

# ----- 환경 변수 체크 -----
if "CHATLING_API_KEY" not in os.environ:
    raise ValueError("🚨 CHATLING_API_KEY 환경 변수 미설정")

# ----- 로깅 설정 -----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("kakao-chatbot")

# ----- Flask 앱 생성 -----
app = Flask(__name__)
CHATLING_API_KEY = os.environ["CHATLING_API_KEY"]
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

# ----- 헬스 체크 -----
@app.route("/")
def health_check():
    return jsonify(status="healthy", service="kakao-chatbot"), 200

# ----- 카카오 웹훅 -----
@app.post("/webhook")
def kakao_webhook():
    try:
        body = request.get_json(force=True, silent=True) or {}
        logger.info(f"Request: {body}")

        # 필수 필드 추출
        user_req = body.get("userRequest", {})
        utterance = user_req.get("utterance", "").strip()
        user_id = (user_req.get("user") or {}).get("id", "")

        if not utterance or not user_id:
            logger.error("필수 필드 누락")
            return _make_kakao_response("요청 형식이 올바르지 않습니다.")

        # Chatling API 호출
        headers = {
            "Authorization": f"Bearer {CHATLING_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"message": utterance, "sessionId": user_id}

        try:
            response = requests.post(
                CHATLING_API_URL,
                json=payload,
                headers=headers,
                timeout=3
            )
            response.raise_for_status()
            answer = (response.json() or {}).get("answer", "")
        except Exception as e:
            logger.error(f"Chatling API 오류: {str(e)}")
            answer = ""

        return _make_kakao_response(
            answer or "현재 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."
        )

    except Exception as e:
        logger.critical(f"웹훅 처리 실패: {str(e)}", exc_info=True)
        return _make_kakao_response("서버 내부 오류 발생")

# ----- 카카오 응답 생성 헬퍼 -----
def _make_kakao_response(text):
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}]
        }
    })

# ----- 메인 실행 블록 (들여쓰기 주의!) -----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
