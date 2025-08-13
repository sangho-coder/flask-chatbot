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
# 과도한 본문 방지(웹훅 경로로 큰 파일이 들어오지 않게)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1MB

# ---------- 공용 유틸 ----------
KAKAO_OK_TEXT = "연결 OK"

def kakao_text(text: str) -> Response:
    """카카오 v2.0 simpleText 최소 응답"""
    payload = {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text or ""}}]
        }
    }
    return Response(
        response=app.response_class.dumps(payload),
        status=200,
        mimetype="application/json"
    )

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

# 전역 예외도 200으로(제로-페일)
@app.errorhandler(Exception)
def _on_error(e):
    log.exception("Unhandled error on %s", request.path)
    return kakao_text("일시적인 오류가 있었지만 연결은 정상입니다.")

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
    # GET/HEAD로 확인 오는 경우도 200
    if request.method in ("GET", "HEAD"):
        return Response(b"ok", 200, mimetype="text/plain")

    # 안전 파싱(실패해도 예외 안 던짐)
    data = request.get_json(silent=True) or {}

    # 1) 폴백 블록에서 매핑한 파라미터(@sys.text → usrtext) 우선
    utter = (
        (((data.get("action") or {}).get("params") or {}).get("usrtext")) or
        # 2) 일반 발화
        (((data.get("userRequest") or {}).get("utterance")) or "")
    )
    utter = (utter or "").strip()

    # 여기서는 “에코”로만 응답(지연/외부콜 없음 → 즉시 200)
    if utter:
        return kakao_text(f"[OK] {utter}")
    return kakao_text(KAKAO_OK_TEXT)

# 로컬 실행용(컨테이너에선 gunicorn이 기동)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    log.info("local run on 0.0.0.0:%s", port)
    app.run(host="0.0.0.0", port=port)
