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
# 과도한 본문 방지(선택): 큰 파일이 바로 /webhook으로 들어오지 않도록
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

log.info("Flask 앱 초기화 완료")
log.info("ENV PORT=%s", os.getenv("PORT"))

# ----- (선택) 환경 변수 -----
CHATLING_API_KEY = os.getenv("CHATLING_API_KEY")
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

# ----- 요청 시간 로깅 -----
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

# ----- 에러 핸들러(응답은 항상 안전하게 반환) -----
@app.errorhandler(Exception)
def _on_error(e):
    log.exception("Unhandled error on %s", request.path)
    # 웹훅 요청에서도 500로 죽지 않게 보호
    return jsonify(error="server error"), 200

# ----- 헬스체크 -----
@app.get("/")
@app.get("/health")
@app.get("/healthz")
def health_check():
    return jsonify(
        status="healthy",
        message="Service is running",
        timestamp=datetime.utcnow().isoformat(),
        env_loaded=bool(CHATLING_API_KEY),
    ), 200

# ----- 웹훅: 어떤 요청이 와도 즉시 200 -----
@app.route("/webhook", methods=["POST", "GET", "HEAD"])
def kakao_webhook():
    # 요청 파싱 없이 로그만 남기고 즉시 응답
    try:
        ua = request.headers.get("User-Agent", "-")
        clen = request.headers.get("Content-Length", "0")
        log.info("Kakao Webhook hit: method=%s len=%s ua=%s", request.method, clen, ua)
    except Exception:
        pass

    # GET/HEAD로 헬스/프리플라이트성 요청이 들어올 수 있음
    if request.method in ("GET", "HEAD"):
        return ("ok", 200)

    # POST일 때는 카카오 v2.0 최소 응답으로 200 반환
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": "웹훅 테스트: 최소화된 응답입니다."}}
            ]
        }
    }), 200

# ----- 로컬 실행용 -----
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    log.info(f"Flask 앱 로컬 실행 시작 (http://0.0.0.0:{port})")
    app.run(host="0.0.0.0", port=port)
