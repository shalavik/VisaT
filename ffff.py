from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

WHATSAPP_TOKEN = 'YOUR_WHATSAPP_CLOUD_API_TOKEN'
PHONE_NUMBER_ID = 'YOUR_PHONE_NUMBER_ID'
VERIFY_TOKEN = 'your_verify_token'

@app.route("/webhook/whatsapp", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Invalid verification token", 403

    if request.method == 'POST':
        data = request.get_json()
        try:
            for entry in data["entry"]:
                for change in entry["changes"]:
                    value = change["value"]
                    messages = value.get("messages")
                    if messages:
                        for message in messages:
                            sender = message["from"]  # WhatsApp ID (e.g. phone number)
                            send_template_message(sender)
        except Exception as e:
            print(f"Error processing message: {e}")
        return "ok", 200


def send_template_message(recipient_phone_number):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": recipient_phone_number,
        "type": "template",
        "template": {
            "name": "hello_world",  # must be an approved template
            "language": {"code": "en_US"}
        }
    }

    response = requests.post(url, headers=headers, json=data)
    print(f"Sent response: {response.status_code} {response.text}")