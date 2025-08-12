import os
import logging
from flask import Flask, request, jsonify
import requests

# ----- 로깅 설정 (Railway에서 확인 가능하도록 강화) -----
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger("KakaoChatbot")

# ----- Flask 앱 초기화 (최소한의 코드만 최상위에 유지) -----
app = Flask(__name__)
log.info("Flask 앱 초기화 완료")

# ----- 지연 가능성이 있는 코드는 함수 내부로 이동 -----
def get_chatling_key():
    """필요 시점에 환경 변수 로드"""
    key = os.environ.get("CHATLING_API_KEY")
    if not key:
        log.error("CHATLING_API_KEY 환경 변수 누락")
    return key

# ----- 헬스체크 엔드포인트 (Railway 필수) -----
@app.get("/")
def health():
    log.info("Health check passed")  # 로그 추가
    return "OK", 200

@app.get("/healthz")
def healthz():
    return jsonify(status="ok"), 200

# ----- 카카오 Webhook (최적화된 버전) -----
@app.post("/webhook")
def kakao_webhook():
    # 1. 요청 파싱 (에러 처리 강화)
    try:
        body = request.get_json()
        if not body:
            log.warning("빈 요청 수신")
            return _kakao_text("올바른 요청이 아닙니다."), 400
            
        user_req = body.get("userRequest", {})
        utter = user_req.get("utterance", "").strip()
        user_id = user_req.get("user", {}).get("id", "unknown")
        
        if not utter:
            return _kakao_text("질문을 입력해 주세요."), 400

    except Exception as e:
        log.exception("요청 파싱 실패: %s", e)
        return _kakao_text("서버 처리 오류"), 500

    # 2. API 키 확인 (필요 시점에 로드)
    chatling_key = get_chatling_key()
    if not chatling_key:
        return _kakao_text("서버 설정 오류"), 500

    # 3. Chatling API 호출 (타임아웃 3.5초 유지)
    try:
        headers = {
            "Authorization": f"Bearer {chatling_key}",
            "Content-Type": "application/json"
        }
        payload = {"message": utter, "sessionId": user_id}
        
        res = requests.post(
            "https://api.chatling.ai/v1/respond",
            json=payload,
            headers=headers,
            timeout=3.5
        )
        
        if res.ok:
            answer = res.json().get("answer", "답변을 찾기 어려워요.")
        else:
            log.warning(f"Chatling API 오류: {res.status_code} - {res.text[:200]}")
            answer = "일시적인 오류가 발생했습니다."

    except requests.Timeout:
        log.warning("Chatling API 타임아웃")
        answer = "질문을 접수했어요. 조금 뒤 다시 말씀드릴게요."
    except Exception as e:
        log.exception("Chatling API 호출 실패: %s", e)
        answer = "서버 오류가 발생했습니다."

    return _kakao_text(answer)

# ----- 카카오 응답 포맷터 -----
def _kakao_text(text: str):
    """카카오 v2.0 형식 응답 생성 (오타 방지용)"""
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {  # 주의: 대소문자 정확히 맞출 것
                    "text": text
                }
            }]
        }
    })

# ----- 메인 실행 (Railway 호환) -----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Railway 동적 포트 지원
    app.run(host="0.0.0.0", port=port)
