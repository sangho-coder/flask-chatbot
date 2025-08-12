import os
import time
import logging
from datetime import datetime
from flask import Flask, request, jsonify, g

# ----- 로깅 설정 -----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger("KakaoChatbot")

# ----- Flask 앱 -----
app = Flask(__name__)
# 과도한 본문 방지(선택): 음성/파일이 webhook로 직접 오지 않게
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024
log.info("Flask 앱 초기화 완료")

# ----- 환경 변수 -----
CHATLING_API_KEY = os.getenv("CHATLING_API_KEY")
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

# ----- request 타이밍 로깅(문제 파악용) -----
@app.before_request
def _start_timer():
    g._t0 = time.time()

@app.after_request
def _after(resp):
    try:
        took = int((time.time() - getattr(g, "_t0", time.time())) * 1000)
        log.info("path=%s method=%s status=%s took_ms=%s ua=%s",
                 request.path, request.method, resp.status_code, took,
                 request.headers.get("User-Agent"))
    except Exception:
        pass
    return resp

# ----- 헬스체크 -----
@app.get("/")
@app.get("/health")
@app.get("/healthz")
def health_check():
    log.info("Health Check 요청 수신")
    return jsonify(
        status="healthy",
        message="Service is running",
        timestamp=datetime.utcnow().isoformat(),
        env_loaded=bool(CHATLING_API_KEY)
    ), 200

# ----- 카카오 웹훅: 즉시 200 OK -----
@app.route("/webhook", methods=["POST", "GET", "HEAD"])
def kakao_webhook():
    # 어떤 본문도 파싱하지 않고, 즉시 200 반환
    try:
        ua = request.headers.get("User-Agent", "-")
        clen = request.headers.get("Content-Length", "0")
        log.info("Kakao Webhook hit: method=%s len=%s ua=%s", request.method, clen, ua)
    except Exception:
        pass

    # HEAD/GET 요청이 올 수도 있으니 간단 응답
    if request.method in ("GET", "HEAD"):
        return ("ok", 200)

    # 카카오 v2.0 형식의 최소 응답(POST일 때)
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {"text": "웹훅 테스트: 최소화된 응답입니다."}
                }
            ]
        }
    }), 200

# ----- (참고) 카카오 응답 헬퍼 -----
def _kakao_response(text, status=200):
    return jsonify({
        "version": "2.0",
        "template": {"outputs": [{"simpleText": {"text": text}}]}
    }), status

# ----- 로컬 실행용 -----
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    log.info(f"Flask 앱 로컬 실행 시작 (http://0.0.0.0:{port})")
    app.run(host="0.0.0.0", port=port)
