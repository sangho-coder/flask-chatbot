from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Chatling API Key (하드코딩)
CHATLING_API_KEY = "3CDuWbTMau59Gmmm82KR5Y5nSxWHkzyAnGVFC41FCYF2Tb2GHNr9ud1bGc4jrVbc"
CHATLING_API_URL = "https://api.chatling.ai/v1/respond"

@app.route("/", methods=["GET"])
def health_check():
    return "OK", 200

@app.route("/webhook", methods=["POST"])
def kakao_webhook():
    try:
        body = request.get_json()
        user_msg = body['userRequest']['utterance']

        # Chatling API 호출
        headers = {
            "Authorization": f"Bearer {CHATLING_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "message": user_msg,
            "sessionId": body['userRequest']['user']['id']  # 사용자별 세션 유지
        }
        chatling_res = requests.post(CHATLING_API_URL, json=payload, headers=headers)

        if chatling_res.status_code == 200:
            chatling_answer = chatling_res.json().get("answer", "죄송합니다, 답변을 찾을 수 없습니다.")
        else:
            chatling_answer = "죄송합니다, 서버와 연결이 원활하지 않습니다."

        # 카카오톡 응답 포맷
        kakao_response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": chatling_answer
                        }
                    }
                ]
            }
        }
        return jsonify(kakao_response)

    except Exception as e:
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": f"에러 발생: {str(e)}"
                        }
                    }
                ]
            }
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
