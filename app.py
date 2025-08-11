# app.py
import os
from flask import Flask, request, jsonify
from tasks import query_chatling  # 안전: tasks.py가 Flask를 안 불러서 순환참조 없음

app = Flask(__name__)

CHATLING_API_KEY = os.environ.get("CHATLING_API_KEY")  # 배포 시엔 환경변수로!
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"  # (직접 호출 대비용, 실제는 태스크 사용)

@app.get("/")
def health():
    return "OK", 200

@app.post("/webhook")
def kakao_webhook():
    body = request.get_json(silent=True) or {}
    user_req = body.get("userRequest", {})
    utter = user_req.get("utterance")
    user_id = user_req.get("user", {}).get("id", "unknown")

    if not utter:
        return jsonify({
            "version": "2.0",
            "template": {"outputs":[{"simpleText":{"text":"질문이 비었습니다."}}]}
        }), 400

    # 비동기 태스크 큐에 던지고, 5초 제한 고려해서 빠르게 응답
    # 필요하면 .get(timeout=…) 으로 동기 대기도 가능 (테스트용)
    # result = query_chatling.delay(utter, CHATLING_API_KEY, user_id)

    # 데모/확인용: 잠깐 동기 호출 (배포전 로컬에서만 사용 권장)
    try:
        answer = query_chatling.apply(args=[utter, CHATLING_API_KEY, user_id]).get(timeout=9)
    except Exception:
        answer = "일시적 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."

    return jsonify({
        "version": "2.0",
        "template": {"outputs":[{"simpleText":{"text": answer}}]}
    })
