import os
from flask import Flask, Response

app = Flask(__name__)

# 미리 직렬화된 카카오 v2.0 최소 JSON (bytes)
KAKAO_OK = (
    b'{"version":"2.0","template":{"outputs":[{"simpleText":{"text":"ok"}}]}}'
)

@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET"])
@app.route("/healthz", methods=["GET"])
def healthz():
    # request 객체에 접근하지 않음
    return Response(b"ok", status=200, mimetype="text/plain")

@app.route("/webhook", methods=["POST", "GET", "HEAD"])
def webhook():
    # request 객체에 어떤 접근도 하지 않고, 고정 응답 즉시 반환
    # (GET/HEAD도 같은 바디/헤더로 200 반환)
    return Response(KAKAO_OK, status=200, mimetype="application/json")

# 로컬 실행용 (Railway에선 gunicorn이 실행)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
