import os
import logging
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

# --- env 로드 ---
load_dotenv()

# --- 로깅 ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")

# --- Flask ---
app = Flask(__name__)

# --- 설정 ---
CHATLING_API_KEY = os.getenv("CHATLING_API_KEY")  # 반드시 .env에 넣기
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

# Celery(백그라운드 작업)
from tasks import celery, query_chatling, log_event  # noqa: E402

@app.get("/")
def root():
    return "OK", 200

@app.get("/healthz")
def healthz():
    return jsonify(status="ok"), 200

@app.post("/webhook")
def webhook():
    """
    카카오 5초 룰:
      1) 가능한 한 빠르게 동기 처리(<=2.5s) 시도
      2) 실패/지연 시 즉시 200 + "잠시 후 안내" 메시지
      3) 백그라운드(Celery)에서 실제 답변 준비/로그 등 처리
    """
    body = request.get_json(force=True, silent=True) or {}
    user_req = body.get("userRequest") or {}
    utter = user_req.get("utterance")
    user_id = (user_req.get("user") or {}).get("id") or "anon"
    log.info(f"Webhook: utter={utter}, user_id={user_id}")

    if not utter:
        return _kakao_text("요청 형식이 올바르지 않습니다."), 200

    # 1) 빠른 동기 호출(2.0~2.5초 이내) 시도
    answer = None
    try:
        headers = {
            "Authorization": f"Bearer {CHATLING_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"message": utter, "sessionId": user_id}
        r = requests.post(CHATLING_API_URL, json=payload, headers=headers, timeout=2.2)
        if r.ok:
            answer = (r.json() or {}).get("answer")
    except Exception as e:
        log.warning(f"Sync call timeout or error: {e}")

    if answer:
        # 2-a) 바로 반환
        log_event.delay("answer", {"u": user_id, "q": utter, "a": answer})
        return _kakao_text(answer), 200

    # 2-b) 즉시 응답(5초 안에 끝)
    #     그리고 3) 백그라운드 큐로 실제 처리 넘김(옵션)
    query_chatling.delay(utter, user_id)
    log_event.delay("queued", {"u": user_id, "q": utter})
    return _kakao_text("잠시만요, 확인 중입니다."), 200


def _kakao_text(text: str):
    """카카오 i 오픈빌더 응답 포맷"""
    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}]
        }
    }

# 로컬 실행용(배포에선 gunicorn/waitress로 띄우세요)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
