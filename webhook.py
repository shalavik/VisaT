from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "a7f4d2e9c6b8f1e3a5d9c2b7e4f8a1d6"  # your token from Meta

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Verified webhook from Meta")
        return challenge, 200
    else:
        return "Forbidden", 403

if __name__ == '__main__':
    app.run(port=3001)
