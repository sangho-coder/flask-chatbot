import os
import logging
from flask import Flask

# 로깅 강화 (Railway에서 확인 가능하도록)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger("MinimalApp")

app = Flask(__name__)
log.info("Flask 앱 생성 완료")

@app.route("/")
def health_check():
    log.info("Health Check 요청 수신")
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
