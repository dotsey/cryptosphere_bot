from flask import Flask, request
import telegram
import os

app = Flask(__name__)

# Get environment variables
BOT_TOKEN = os.environ["BOT_TOKEN"]
GROUP_CHAT_ID = os.environ["GROUP_CHAT_ID"]
PAYSTACK_SECRET = os.environ["PAYSTACK_SECRET"]

# Initialize Telegram Bot
bot = telegram.Bot(token=BOT_TOKEN)

@app.route("/", methods=["GET"])
def index():
    return "Bot is running."

@app.route("/webhook", methods=["POST"])
def paystack_webhook():
    data = request.get_json()

    # Print everything for debugging
    print("========== PAYSTACK WEBHOOK RECEIVED ==========")
    print("FULL PAYLOAD:", data)
    print("HEADERS:", dict(request.headers))
    print("===============================================")

    signature = request.headers.get("x-paystack-signature")
    print("SIGNATURE RECEIVED:", signature)
    print("SECRET EXPECTED:", PAYSTACK_SECRET)

    if signature != PAYSTACK_SECRET:
        print("❌ Signature mismatch")
        return "Invalid signature", 403

    if data.get("event") == "charge.success":
        customer_email = data["data"]["customer"]["email"]
        metadata = data["data"].get("metadata", {})

        telegram_username = (
            metadata.get("telegram_username") or
            metadata.get("Telegram Username") or
            metadata.get("telegram")
        )

        print("✅ METADATA FOUND:", metadata)
        print("✅ TELEGRAM USERNAME:", telegram_username)

        if telegram_username:
            try:
                # Send a message to the group
                bot.send_message(chat_id=GROUP_CHAT_ID, text=f"✅ New subscriber: @{telegram_username}")
            except Exception as e:
                print(f"❌ Error sending message: {e}")
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
