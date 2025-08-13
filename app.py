import os
import time
import logging
from datetime import datetime
from flask import Flask, request, jsonify, Response, g

# ---------- 로깅 ----------
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger("kakao-skill")

# ---------- Flask ----------
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1MB

def kakao_text(text: str):
    """카카오 v2.0 simpleText 최소 응답 (jsonify 사용)"""
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text or ""}}]
        }
    })

# 요청 타이머/액세스 로그
@app.before_request
def _start_timer():
    g._t0 = time.time()

@app.after_request
def _after(resp: Response):
    try:
        took_ms = int((time.time() - getattr(g, "_t0", time.time())) * 1000)
        log.info(
            "path=%s method=%s status=%s took_ms=%s ua=%s ip=%s",
            request.path, request.method, resp.status_code, took_ms,
            request.headers.get("User-Agent", "-"),
            request.headers.get("X-Forwarded-For", request.remote_addr)
        )
    except Exception:
        pass
    return resp

# 전역 예외도 JSON 200으로 감싸기 (제로-페일)
@app.errorhandler(Exception)
def _on_error(e):
    log.exception("Unhandled error on %s", request.path)
    return kakao_text("일시적 오류가 있었지만 연결은 정상입니다."), 200

# ---------- 헬스체크 ----------
@app.get("/")
@app.get("/health")
@app.get("/healthz")
def healthz():
    return jsonify(
        status="healthy",
        message="Service is running",
        timestamp=datetime.utcnow().isoformat()
    ), 200

# ---------- 카카오 스킬 웹훅 ----------
@app.route("/webhook", methods=["POST", "GET", "HEAD"])
def webhook():
    if request.method in ("GET", "HEAD"):
        return Response(b"ok", 200, mimetype="text/plain")

    data = request.get_json(silent=True) or {}
    utter = (
        (((data.get("action") or {}).get("params") or {}).get("usrtext")) or
        (((data.get("userRequest") or {}).get("utterance")) or "")
    )
    utter = (utter or "").strip()

    if utter:
        return kakao_text(f"[OK] {utter}"), 200
    return kakao_text("연결 OK"), 200

# 로컬 실행용
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    log.info("local run on 0.0.0.0:%s", port)
    app.run(host="0.0.0.0", port=port)
