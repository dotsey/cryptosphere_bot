from flask import Flask, request, jsonify
import telegram
import os

app = Flask(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
GROUP_CHAT_ID = os.environ["GROUP_CHAT_ID"]
PAYSTACK_SECRET = os.environ["PAYSTACK_SECRET"]

bot = telegram.Bot(token=BOT_TOKEN)

@app.route("/", methods=["GET"])
def index():
    return "Bot is running."

@app.route("/webhook", methods=["POST"])
def paystack_webhook():
    data = request.get_json()

    signature = request.headers.get("x-paystack-signature")
    if signature != PAYSTACK_SECRET:
        return "Invalid signature", 403

    if data.get("event") == "charge.success":
        email = data["data"]["customer"]["email"]
        metadata = data["data"].get("metadata", {})
        telegram_username = metadata.get("telegram")

        if telegram_username:
            try:
                bot.send_message(
                    chat_id=GROUP_CHAT_ID,
                    text=f"✅ {telegram_username}, your payment was successful! Welcome to the VIP group."
                )
            except Exception as e:
                print(f"Error sending message: {e}")
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
