import os
from flask import Flask, Response

app = Flask(__name__)

# 미리 직렬화된 고정 JSON (카카오 v2.0 최소 형태)
KAKAO_OK = b'{"version":"2.0","template":{"outputs":[{"simpleText":{"text":"ok"}}]}}'

@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET"])
@app.route("/healthz", methods=["GET"])
def healthz():
    # request 객체에 절대 접근하지 않음
    return Response(b"ok", status=200, mimetype="text/plain")

@app.route("/webhook", methods=["POST", "GET", "HEAD"])
def webhook():
    # request에 절대 접근하지 않음. 무조건 고정 JSON 즉시 200
    return Response(KAKAO_OK, status=200, mimetype="application/json")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
