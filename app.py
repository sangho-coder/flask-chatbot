from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health_check():
    return "OK", 200

@app.route("/webhook", methods=["POST"])
def kakao_webhook():
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "서버가 정상 작동하고 있습니다."
                    }
                }
            ]
        }
    })
