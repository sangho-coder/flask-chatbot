import os
from flask import Flask, Response

app = Flask(__name__)
KAKAO_OK = b'{"version":"2.0","template":{"outputs":[{"simpleText":{"text":"ok"}}]}}'

@app.route("/", methods=["GET"])
@app.route("/healthz", methods=["GET"])
def healthz():
    return Response(b"ok", 200, mimetype="text/plain")

@app.route("/webhook", methods=["POST","GET","HEAD"])
def webhook():
    return Response(KAKAO_OK, 200, mimetype="application/json")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print("PORT=", port, flush=True)
    app.run(host="0.0.0.0", port=port)
