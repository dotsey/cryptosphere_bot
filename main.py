from flask import Flask, request
import telegram
import os
import hmac
import hashlib

app = Flask(__name__)

# Get environment variables
BOT_TOKEN = os.environ["BOT_TOKEN"]
GROUP_CHAT_ID = os.environ["GROUP_CHAT_ID"]
PAYSTACK_SECRET = os.environ["PAYSTACK_SECRET"]

# Initialize Telegram bot
bot = telegram.Bot(token=BOT_TOKEN)

@app.route("/", methods=["GET"])
def index():
    return "Bot is running."

@app.route("/webhook", methods=["POST"])
def paystack_webhook():
    raw_body = request.data
    received_sig = request.headers.get("x-paystack-signature")

    # Generate expected signature using Paystack secret
    expected_sig = hmac.new(
        key=PAYSTACK_SECRET.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha512
    ).hexdigest()

    # Verify signature
    if received_sig != expected_sig:
        return "Invalid signature", 403

    data = request.get_json()

    if data.get("event") == "charge.success":
        customer = data["data"].get("customer", {})
        metadata = data["data"].get("metadata", {})
        telegram_username = metadata.get("telegram_username")

        if telegram_username:
            try:
                # Attempt to invite the user to the group
                bot.invite_chat_member(chat_id=GROUP_CHAT_ID, user_id=f"@{telegram_username}")
            except Exception as e:
                print(f"Error inviting user: {e}")
    
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
