
# ✅ Razorpay Webhook + Email Backend (Flask)

from flask import Flask, request, jsonify
import hmac
import hashlib
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)

# === Razorpay Secret Key (Keep this safe!) ===
RAZORPAY_SECRET = "your_webhook_secret_here"  # Replace with your actual Razorpay webhook secret
ADMIN_EMAIL = "avishkp5@gmail.com"
APP_PASSWORD = "blqv ncbyn pfhu nwzq"  # Replace with your actual Gmail App Password
ULTRAPROBOT_PAYMENT_PAGE = "https://ultraprobot-ai.netlify.app"  # ✅ Your public payment page

# === Verify Signature ===
def verify_signature(payload, signature):
    generated_signature = hmac.new(
        key=RAZORPAY_SECRET.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(generated_signature, signature)

# === Email Notification ===
def send_payment_email(email, name, amount):
    msg = MIMEText(
        f"Payment of Rs. {amount} was successfully received from {name}.\n\nYour UltraProBot subscription has been activated ✅\n\nAccess your scanner: {ULTRAPROBOT_PAYMENT_PAGE}"
    )
    msg["Subject"] = "✅ Payment Successful - UltraProBot"
    msg["From"] = ADMIN_EMAIL
    msg["To"] = email

    # Gmail SMTP setup (use App Password)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(ADMIN_EMAIL, APP_PASSWORD)
    server.send_message(msg)
    server.quit()

# === Webhook Endpoint ===
@app.route("/webhook", methods=["POST"])
def razorpay_webhook():
    payload = request.data
    signature = request.headers.get("X-Razorpay-Signature")

    if not verify_signature(payload, signature):
        return jsonify({"status": "Invalid signature"}), 400

    data = request.json
    event = data.get("event")

    if event == "payment.captured":
        payment_info = data["payload"]["payment"]["entity"]
        email = payment_info.get("email", ADMIN_EMAIL)
        amount = int(payment_info.get("amount", 0)) / 100
        name = payment_info.get("contact", "User")

        print(f"✅ Payment captured from {name} - ₹{amount}")

        # ✅ Send confirmation email
        send_payment_email(email, name, amount)

        # ✅ Activate subscription logic (e.g., update JSON/db)
        # activate_user_subscription(email)

        return jsonify({"status": "Payment processed"}), 200

    return jsonify({"status": "Unhandled event"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
